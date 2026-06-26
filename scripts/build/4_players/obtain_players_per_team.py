import json
from pathlib import Path
import yaml
import re
import sys
from collections import defaultdict

sys.path.append(str(Path(__file__).parent))

from mappings.roles import TACTICAL_ROLES
from mappings.roles import GROUP_TO_ROLES
from mappings.roles import ROLE_MAP
from mappings.roles import POSITION_TO_ROLES
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
    total_positions = len(positions)

    total = sum(
        count
        for count in positions.values()
        if count is not None
    )

    for position, count in positions.items():

        # print(f"Position: {position}, Count: {count}, Total: {total}")

        if count is None:
            position_weight = 1.0 / total_positions

        else:
            position_weight = count / total
        
        # print(position_weight)

        mapping = POSITION_TO_ROLES.get(position) or GROUP_TO_ROLES.get(position)

        if mapping:
            for role, role_weight in mapping.items():
                roles[role] = roles.get(role, 0) + position_weight * role_weight

    return roles

def versatility(player):
    return sum(player["roles"].values())

def select_squad(players, tactic):

    slots = expand_tactic(tactic)
    #print(slots)

    role_candidates = defaultdict(list)

    for player in players:
        roles = get_player_roles(player)
        player["roles"] = roles
        
        for role, role_weight in roles.items():

            role_score = (
                player["score"]
                * role_weight
                / versatility(player)
            )

            role_candidates[role].append({
                "player": player,
                "score": player["score"] * role_weight,
                "role_weight": role_weight
            })
    
    for candidates in role_candidates.values():
        candidates.sort(key=lambda c: c["score"], reverse=True)
    
    #print(role_candidates)

    slots.sort(
        key=lambda role: len(role_candidates[role])
    )

    '''
    for role, candidates in role_candidates.items():
        print(f"\n{role}")

        for candidate in candidates[:5]:
            print(
                candidate["player"]["name"],
                round(candidate["score"], 3)
            )
    '''

    selected_ids = set()
    selected_squad = []

    for role in slots:

        candidates = role_candidates.get(role, [])

        for candidate in candidates:

            player = candidate["player"]

            if player["ID_transfermarkt"] in selected_ids:
                continue

            selected_ids.add(player["ID_transfermarkt"])

            selected_squad.append({
                "role": role,
                "player": player,
                "score": candidate["score"]
            })

            break
        
    return selected_squad

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

        squad = select_squad(players, tactic)

        #continue
        output_path = output_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(squad, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
