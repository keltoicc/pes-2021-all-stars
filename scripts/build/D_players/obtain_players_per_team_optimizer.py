import json
from pathlib import Path
import yaml
import re
import sys
from collections import defaultdict
import math
from collections import Counter

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

    for role, count in TACTICS[tactic].items():

        slots.extend([role] * count)

    return slots

def build_slot_candidates(players, slots):

    candidates = defaultdict(list)

    for role in set(slots):

        for player in players:

            role_data = player["roles"].get(role)

            if role_data is None:
                continue

            candidates[role].append({
                "player": player,
                "score": role_data["score"],
                "weight": role_data["weight"]
            })

        candidates[role].sort(
            key=lambda x: x["score"],
            reverse=True
        )

    return candidates

def greedy_assignment(players, slots, slot_candidates):

    assignments = []
    selected = set()

    slot_counts = Counter(slots)

    ordered_roles = sorted(
        slot_counts.keys(),
        key=lambda role: (
            len(slot_candidates[role]),
            -slot_counts[role]
        )
    )

    for role in ordered_roles:

        needed = slot_counts[role]

        assigned = 0

        for candidate in slot_candidates[role]:

            player = candidate["player"]
            pid = player["ID_transfermarkt"]

            if pid in selected:
                continue

            assignments.append({
                "role": role,
                "player": player,
                "score": candidate["score"],
                "role_weight": candidate["weight"]
            })

            selected.add(pid)

            assigned += 1

            if assigned == needed:
                break

        if assigned != needed:
            print(f"No hay suficientes jugadores para {role}")

    return {
        "slots": assignments,
        "total_score": sum(
            slot["score"]
            for slot in assignments
        )
    }

def get_role_score(player, role):

    role_data = player["roles"].get(role)

    if role_data is None:
        return None

    return role_data["score"], role_data["weight"]

def optimize_assignments(solution):

    assignments = solution["slots"]

    while True:

        best_move = None
        best_delta = 0

        for i in range(len(assignments) - 1):

            a = assignments[i]

            if a["role"] == "UTILITY":
                continue

            for j in range(i + 1, len(assignments)):

                b = assignments[j]

                if b["role"] == "UTILITY":
                    continue

                if a["role"] == b["role"]:
                    continue

                a_new = get_role_score(
                    a["player"],
                    b["role"]
                )

                if a_new is None:
                    continue

                b_new = get_role_score(
                    b["player"],
                    a["role"]
                )

                if b_new is None:
                    continue

                current = a["score"] + b["score"]
                proposed = a_new[0] + b_new[0]

                delta = proposed - current

                if delta > best_delta:
                    best_delta = delta
                    best_move = (
                        i,
                        j,
                        a_new,
                        b_new
                    )

        if best_move is None:
            break

        i, j, a_new, b_new = best_move

        assignments[i], assignments[j] = (
            {
                "role": assignments[j]["role"],
                "player": assignments[i]["player"],
                "score": a_new[0],
                "role_weight": a_new[1]
            },
            {
                "role": assignments[i]["role"],
                "player": assignments[j]["player"],
                "score": b_new[0],
                "role_weight": b_new[1]
            }
        )

        solution["total_score"] += best_delta

    return solution

def clone_solution(solution):
    return {
        "slots": [slot.copy() for slot in solution["slots"]],
        "total_score": solution["total_score"]
    }

def optimize_roster(solution, players):

    while True:

        selected = {
            slot["player"]["ID_transfermarkt"]
            for slot in solution["slots"]
        }

        remaining_players = [
            player
            for player in players
            if player["ID_transfermarkt"] not in selected
        ]

        best_solution = solution
        best_score = solution["total_score"]

        for player in remaining_players:

            for i, slot in enumerate(solution["slots"]):

                # El nuevo jugador debe poder jugar en ese rol
                new_slot = replace_player(slot, player)

                if new_slot is None:
                    continue

                candidate = clone_solution(solution)

                candidate["slots"][i] = new_slot

                candidate["total_score"] = (
                    candidate["total_score"]
                    - slot["score"]
                    + new_slot["score"]
                )

                candidate = optimize_assignments(candidate)

                if candidate["total_score"] > best_score:

                    best_solution = candidate
                    best_score = candidate["total_score"]

        if best_solution is solution:
            break

        solution = best_solution

    return solution

def replace_player(slot, player):

    role = slot["role"]

    score = get_role_score(player, role)

    if score is None:
        return None

    return {
        "role": role,
        "player": player,
        "score": score[0],
        "role_weight": score[1]
    }

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

        slot_candidates = build_slot_candidates(players, slots)

        solution = greedy_assignment(
            players,
            slots,
            slot_candidates
        )

        solution = optimize_assignments(solution)

        solution = optimize_roster(
            solution,
            players
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
