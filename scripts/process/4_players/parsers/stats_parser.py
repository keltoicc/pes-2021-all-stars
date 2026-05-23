from pathlib import Path
import json


def parse_stats(stats_path):
    with open(stats_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    matches = []

    for item in data["data"]["performance"]:

        general = item["statistics"]["generalStatistics"]
        goals = item["statistics"]["goalStatistics"]
        play = item["statistics"]["playingTimeStatistics"]

        minutes = play.get("playedMinutes") or 0

        position_id = general.get("positionId")

        matches.append({
            "game_id": item["gameInformation"]["gameId"],
            "season": item["gameInformation"]["season"]["display"],
            "competition_type": item["gameInformation"]["competitionTypeId"],

            "club_id": item["clubsInformation"]["club"]["clubId"],
            "opponent_id": item["clubsInformation"]["opponent"]["clubId"],

            "position": position_id,

            "minutes": minutes,
            "started": play.get("isStarting", False),

            "captain": general.get("isCaptain", False),

            "goals": goals.get("goalsScoredTotal") or 0,
            "assists": goals.get("assists") or 0,

            "goals_conceded":
                goals.get("opponentGoalsOnThePitch") or 0,

            "participation":
                general.get("participationState"),

            "club_points":
                item["clubsInformation"]["club"]["points"]
        })

    return matches


raw_dir = Path("data/raw/transfermarkt/players/stats/8198.json")
data = parse_stats(raw_dir)
print(data)