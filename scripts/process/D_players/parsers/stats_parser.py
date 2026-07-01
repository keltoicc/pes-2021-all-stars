from pathlib import Path
import json

from mappings.positions import POSITION_MAP
from mappings.competitions import COMPETITION_MAP


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
            "season": item["gameInformation"]["seasonId"],
            "competition_type": COMPETITION_MAP.get(item["gameInformation"]["competitionTypeId"]),

            "club_id": item["clubsInformation"]["club"]["clubId"],
            "opponent_id": item["clubsInformation"]["opponent"]["clubId"],

            "position": POSITION_MAP.get(position_id),

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