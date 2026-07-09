import json
from pathlib import Path
import yaml
import re
import sys
import math

sys.path.append(str(Path(__file__).parent))

from mappings.roles import GROUP_TO_ROLES
from mappings.roles import POSITION_TO_ROLES
from mappings.tactics import TACTICS
from builders.hungarian import hungarian

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
            positions = club_data.get("positions", {})

            roles = build_player_roles(
                positions,
                club_data["importance"]["total"]
            )
            
            data = {
                "ID_transfermarkt": player_id,
                "name": player_data["profile"]["short_name"],
                "score": club_data["importance"]["total"],
                "roles": roles
            }
            return data

def build_player_roles(positions, player_score):

    roles = {}

    total_positions = len(positions)

    total = sum(
        count
        for count in positions.values()
        if count is not None
    )

    for position, count in positions.items():

        if count is None:
            position_weight = 1 / total_positions
        else:
            position_weight = count / total

        mapping = (
            POSITION_TO_ROLES.get(position)
            or GROUP_TO_ROLES.get(position)
        )

        if not mapping:
            continue

        for role, role_weight in mapping.items():

            weight = position_weight * role_weight

            if role not in roles:
                roles[role] = {
                    "weight": 0,
                    "score": 0
                }

            roles[role]["weight"] += weight

    for role, data in roles.items():

        data["score"] = (
            player_score *
            role_factor(data["weight"])
        )
    
    roles["UTILITY"] = {
        "weight": sum(
            role["weight"]
            for role in roles.values()
        ),
        "score": player_score
    }

    return roles

def obtain_tactics(team, tactics_dir):
    tactic_file = tactics_dir / f"{team['ID_pes']}_{slugify(team['name'])}.yml"
    
    if not tactic_file.exists():
        print(f"No hay yml para {tactic_file}")
        return None
    
    tactic_data = yaml.safe_load(
        tactic_file.read_text(encoding="utf-8")
    )["team"]

    return tactic_data.get("tactic")

def role_factor(weight):
    return math.sqrt(weight)

def build_slots(tactic):

    slots = []

    slot_id = 0

    for role, count in TACTICS[tactic].items():

        for _ in range(count):

            slots.append({
                "id": slot_id,
                "role": role
            })

            slot_id += 1

    return slots

def build_assignment_matrix(players, slots):

    matrix = []

    for player in players:

        row = []

        for slot in slots:

            role_data = player["roles"].get(slot["role"])

            if role_data is None:
                score = 0
            else:
                score = role_data["score"]

            row.append(score)

        matrix.append(row)

    return matrix

def build_cost_matrix(score_matrix):

    max_score = max(
        max(row)
        for row in score_matrix
    )

    cost_matrix = []

    for row in score_matrix:

        cost_matrix.append([
            max_score - score
            for score in row
        ])

    return cost_matrix

def hungarian_assignment(players, slots):

    score_matrix = build_assignment_matrix(
        players,
        slots
    )

    cost_matrix = build_cost_matrix(
        score_matrix
    )

    assignment = hungarian(cost_matrix)

    solution = {
        "slots": [],
        "total_score": 0
    }

    for player_index, slot_index in assignment:

        player = players[player_index]
        slot = slots[slot_index]

        role_data = player["roles"][slot["role"]]

        solution["slots"].append({
            "role": slot["role"],
            "player": player,
            "score": role_data["score"],
            "role_weight": role_data["weight"]
        })

        solution["total_score"] += role_data["score"]

    return solution

def export_solution(solution, tactic):

    return {
        "tactic": tactic,
        "total_score": round(solution["total_score"], 2),
        "players": [
            {
                "role": slot["role"],
                "player": slot["player"],
                "score": round(slot["score"], 2),
                "role_weight": round(slot["role_weight"], 4)
            }
            for slot in solution["slots"]
        ]
    }

#def main(yml = "teams"):
def main(yml = "teams_debug"):

    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
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

        slots = build_slots(tactic)

        solution = hungarian_assignment(
            players,
            slots
        )

        output_path = output_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                export_solution(solution, tactic),
                f,
                indent=4,
                ensure_ascii=False
            )

if __name__ == "__main__":
    main()
