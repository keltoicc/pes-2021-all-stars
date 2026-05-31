import json
from pathlib import Path
from collections import defaultdict, Counter

# ============================================
# PATHS
# ============================================

INPUT_DIR = Path("data/processed/players/normalized")
OUTPUT_DIR = Path("data/processed/player_clubs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# ACHIEVEMENT CLASSIFICATION
# ============================================

INDIVIDUAL_KEYWORDS = [
    "ballon d'or",
    "golden boot",
    "player of the year",
    "mvp",
    "top scorer",
    "best player",
    "fifa world player",
    "team of the year",
    "best goalkeeper",
]

# ============================================
# HELPERS
# ============================================

def is_individual_award(title: str) -> bool:
    title_lower = title.lower()

    return any(keyword in title_lower for keyword in INDIVIDUAL_KEYWORDS)


def safe_int(value):
    if value is None:
        return 0

    try:
        return int(value)
    except:
        return 0


def safe_float(value):
    if value is None:
        return 0.0

    try:
        return float(value)
    except:
        return 0.0


# ============================================
# PROCESS PLAYER
# ============================================

def process_player(player_data):

    player_info = player_data.get("player", {})
    matches = player_data.get("matches", [])
    achievements = player_data.get("achievements", [])

    output = {
        "player": {
            "short_name": player_info.get("short_name"),
            "nation_1": player_info.get("nation_1"),
            "nation_2": player_info.get("nation_2"),
            "height": player_info.get("height"),
            "foot": player_info.get("foot"),
            "position_group": player_info.get("position_group"),
            "position_1": player_info.get("position_1"),
            "position_2": player_info.get("position_2"),
            "position_3": player_info.get("position_3"),
            "market_value": player_info.get("market_value"),
            "prime_date": player_info.get("prime_date"),
        },
        "clubs": {}
    }

    clubs = defaultdict(lambda: {
        "seasons": set(),

        "stats": {
            "matches": 0,
            "participations": 0,
            "minutes": 0,
            "starts": 0,
            "captain_matches": 0,
            "goals": 0,
            "assists": 0,
            "goals_conceded": 0,
            "points": 0
        },

        "positions": Counter(),

        "competitions": defaultdict(lambda: {
            "matches": 0,
            "minutes": 0,
            "goals": 0,
            "assists": 0
        }),

        "awards": {
            "team_titles": [],
            "individual_titles": []
        },

        "derived": {},
    })

    # ============================================
    # MATCHES
    # ============================================

    for match in matches:

        club_id = str(match.get("club_id"))

        if not club_id or club_id == "None":
            continue

        club = clubs[club_id]

        season = match.get("season")

        if season is not None:
            club["_seasons"].add(season)

            if season is not None:
                club["seasons"].add(season)

        participated = bool(match.get("participation"))

        club["stats"]["matches"] += 1

        if participated:
            club["stats"]["participations"] += 1

        minutes = safe_int(match.get("minutes"))
        goals = safe_int(match.get("goals"))
        assists = safe_int(match.get("assists"))
        goals_conceded = safe_int(match.get("goals_conceded"))
        points = safe_int(match.get("club_points"))

        club["stats"]["minutes"] += minutes
        club["stats"]["goals"] += goals
        club["stats"]["assists"] += assists
        club["stats"]["goals_conceded"] += goals_conceded
        club["stats"]["points"] += points

        if match.get("started"):
            club["stats"]["starts"] += 1

        if match.get("captain"):
            club["stats"]["captain_matches"] += 1

        position = match.get("position")

        if position:
            club["positions"][position] += 1

        competition = match.get("competition_type")

        if competition:

            comp = club["competitions"][competition]

            comp["matches"] += 1
            comp["minutes"] += minutes
            comp["goals"] += goals
            comp["assists"] += assists

    club["seasons"] = sorted(list(club["seasons"]))

    # ============================================
    # ACHIEVEMENTS
    # ============================================

    for achievement in achievements:

        club_id = achievement.get("club_id")

        if club_id is None:
            continue

        club_id = str(club_id)

        title_entry = {
            "title": achievement.get("title"),
            "season": achievement.get("season"),
            "season_id": achievement.get("season_id")
        }

        if is_individual_award(achievement.get("title", "")):
            clubs[club_id]["awards"]["individual_titles"].append(title_entry)

        else:
            clubs[club_id]["awards"]["team_titles"].append(title_entry)

    # ============================================
    # DERIVED STATS
    # ============================================

    for club_id, club in clubs.items():

        matches_played = club["stats"]["participations"]

        goals = club["stats"]["goals"]
        assists = club["stats"]["assists"]
        minutes = club["stats"]["minutes"]

        club["derived"] = {
            "goal_ratio": round(goals / matches_played, 4)
            if matches_played > 0 else 0,

            "assist_ratio": round(assists / matches_played, 4)
            if matches_played > 0 else 0,

            "minutes_per_match": round(minutes / matches_played, 2)
            if matches_played > 0 else 0,

            "season_count": len(club["_seasons"])
        }

        club["positions"] = dict(club["positions"])
        club["competitions"] = dict(club["competitions"])

        del club["_seasons"]

    output["clubs"] = dict(clubs)

    return output


# ============================================
# MAIN
# ============================================

def main():

    player_files = list(INPUT_DIR.glob("*.json"))

    total = len(player_files)

    for index, file_path in enumerate(player_files, start=1):

        try:

            with open(file_path, "r", encoding="utf-8") as f:
                player_data = json.load(f)

            processed = process_player(player_data)

            output_path = OUTPUT_DIR / file_path.name

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    processed,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            print(f"[{index}/{total}] OK -> {file_path.name}")

        except Exception as e:

            print(f"[{index}/{total}] ERROR -> {file_path.name}")
            print(e)


if __name__ == "__main__":
    main()