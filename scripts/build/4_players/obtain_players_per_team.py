import json
from pathlib import Path
import yaml
import re
import sys

sys.path.append(str(Path(__file__).parent))

from mappings.roles import TACTICAL_ROLES
from mappings.roles import GROUP_TO_ROLES
from mappings.roles import ROLE_MAP
from mappings.tactics import TACTICS

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def build_team_players(team, teams_dir):
    json_file = teams_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

    if not json_file.exists():
        return None

    with json_file.open(encoding="utf-8") as f:
        all_players = json.load(f)

    players = []

    for player in all_players:
        data = obtain_players(
            str(player["ID_transfermarkt"]),
            str(team["ID_transfermarkt"])
        )

        if data:
            players.append(data)

    players.sort(key=lambda x: x["score"], reverse=True)

    return players

def obtain_players(player_id, team_id):
    
    player_score_file = Path(f"data/built/players/scores/{player_id}.json")

    if not player_score_file.exists():
        print(f"No hay json para {player_id}")
        return
    
    with player_score_file.open(encoding="utf-8") as f:
        player_data = json.load(f)
    
    for club_id, club_data in player_data.get("clubs", {}).items():
        if club_id == team_id:
            data = {
                "ID_transfermarkt": player_id,
                "name": player_data.get("profile", {}).get("short_name"),
                "score": club_data.get("importance", {}).get("total"),
                "positions": club_data.get("positions"),
            }
            return data

def obtain_tactics(team, tactics_dir):
    tactic_file = tactics_dir / f"{team['ID_pes']}_{slugify(team['name'])}.yml"
    
    if not tactic_file.exists():
        print(f"No hay yml para {tactic_file}")
        return None
    
    tactic_data = yaml.safe_load(
        tactic_file.read_text(encoding="utf-8")
    )["team"]

    return tactic_data.get("tactic")

def expand_tactic(tactic_name):
    slots = []

    for role, count in TACTICS[tactic_name].items():
        if role == "UTILITY":
            continue

        slots.extend([role] * count)

    return slots

def get_player_roles(player):
    roles = {}

    positions = player.get("positions", {})

    total = sum(
        count
        for count in positions.values()
        if count is not None
    )

    for position, count in positions.items():

        if count is None:
            continue

        position_weight = count / total

        for role, role_positions in ROLE_MAP.items():

            if position not in role_positions:
                continue

            role_weight = role_positions[position]

            roles[role] = roles.get(role, 0) + (
                position_weight * role_weight
            )

    return roles

def select_squad(players, tactic):

    slots = expand_tactic(tactic)

    #slots.sort(key=lambda role: role_candidate_count[role])
    print(slots)

def main():

    teams = yaml.safe_load(
        Path("config/teams_debug.yml").read_text(encoding="utf-8")
    )["teams"]

    teams_dir = Path("data/processed/players")
    tactics_dir = Path("data/built/tactics")
    output_dir = Path("data/built/players/teams")
    output_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        players = build_team_players(team, teams_dir)

        if not players:
            continue

        tactic = obtain_tactics(team, tactics_dir)

        select_squad(players, tactic)

        continue
        output_path = output_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(players, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
