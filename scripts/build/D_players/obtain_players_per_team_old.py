import json
from pathlib import Path
import yaml
import re
import sys
from collections import defaultdict
import math

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

def role_factor(weight):
    return math.sqrt(weight)

def build_role_candidates(players):

    role_candidates = defaultdict(list)

    for player in players:

        roles = get_player_roles(player)

        for role, role_weight in roles.items():

            role_candidates[role].append({
                "player": player,
                "score": player["score"] * role_factor(role_weight),
                "role_weight": role_weight
            })

    return role_candidates

def utility_score(player):

    roles = get_player_roles(player)

    return (
        player["score"] *
        sum(roles.values())
    )

def get_selected_ids(assignment_by_role):
    return {
        entry["player"]["ID_transfermarkt"]
        for entries in assignment_by_role.values()
        for entry in entries
    }

def build_initial_solution(roles, role_candidates):

    squad = []
    selected = set()

    for role, count in roles:

        for _ in range(count):

            candidates = role_candidates.get(role, [])

            for candidate in candidates:

                player = candidate["player"]
                pid = player["ID_transfermarkt"]

                if pid in selected:
                    continue

                squad.append({
                    "role": role,
                    "player": player,
                    "score": candidate["score"],
                    "role_weight": candidate["role_weight"]
                })

                selected.add(pid)
                break

            else:
                print(f"No hay candidatos para {role}")

    return squad

def add_utility_player(squad, players):

    selected_ids = {
        x["player"]["ID_transfermarkt"]
        for x in squad
    }

    remaining_players = [
        player
        for player in players
        if player["ID_transfermarkt"] not in selected_ids
    ]

    utility = max(
        remaining_players,
        key=utility_score,
        default=None
    )

    if utility is None:
        return

    squad.append({
        "role": "UTILITY",
        "player": utility,
        "score": utility_score(utility),
        "role_weight": None
    })

def build_selected_squad(assignment_by_role):

    squad = []

    for role, entries in assignment_by_role.items():

        for entry in entries:

            squad.append({
                "role": role,
                "player": entry["player"],
                "score": entry["score"],
                "role_weight": entry["role_weight"]
            })

    return squad

def select_squad(players, tactic):

    role_candidates = build_role_candidates(players)

    roles = sorted(
        (
            (role, count)
            for role, count in TACTICS[tactic].items()
            if role != "UTILITY"
        ),
        key=lambda x: (
            len(role_candidates[x[0]]),
            -x[1]
        )
    )

    '''
    for role, candidates in role_candidates.items():
        print(f"\n{role}")

        for candidate in candidates[:5]:
            print(
                candidate["player"]["ID_transfermarkt"],
                candidate["player"]["name"],
                round(candidate["score"], 3)
            ) 
    return
    '''

    squad = build_initial_solution(roles, role_candidates)

    add_utility_player(squad, players)

    return {
        "squad": squad
    }, role_candidates

def find_best_swap(solution, role_candidates):

    squad = solution["squad"]
    selected_set = {x["player"]["ID_transfermarkt"] for x in squad}

    best_move = None
    best_delta = 0

    for i, current in enumerate(squad):

        current_role = current["role"]
        current_score = current["score"]

        candidates = role_candidates.get(current_role, [])

        original_best = (
            max(candidates, key=lambda c: c["score"])["score"]
            if candidates
            else 0
        )

        for cand in candidates:

            pid = cand["player"]["ID_transfermarkt"]

            if pid in selected_set:
                continue

            delta = (
                cand["score"]
                - current_score
                - 0.1 * original_best
            )

            if delta > best_delta:
                best_delta = delta
                best_move = (i, cand)

    return best_move

def optimize_solution(solution, role_candidates, min_delta=0, max_iters=50):

    squad = solution["squad"]

    improved = True
    iters = 0

    while improved and iters < max_iters:

        improved = False
        iters += 1

        move = find_best_swap(solution, role_candidates)

        if not move:
            break

        i, candidate = move

        old = squad[i]

        delta = candidate["score"] - old["score"]

        if delta <= min_delta:
            continue

        squad[i] = {
            "role": old["role"],
            "player": candidate["player"],
            "score": candidate["score"],
            "role_weight": candidate["role_weight"]
        }

        improved = True

    return solution

def export_solution(solution, tactic):
    return {
        "tactic": tactic,
        "players": solution["squad"]
    }

def main(yml = "teams"):

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

        solution, role_candidates = select_squad(players, tactic)

        solution = optimize_solution(solution, role_candidates)

        #continue

        if not solution:
            continue

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
