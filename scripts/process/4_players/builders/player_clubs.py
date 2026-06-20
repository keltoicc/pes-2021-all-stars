from collections import defaultdict, Counter

from mappings.achievements import IGNORED_TITLE
from mappings.achievements import INDIVIDUAL_TITLE
from mappings.achievements import NATIONAL_WORLD_TITLE
from mappings.achievements import NATIONAL_CONTINENTAL_TITLE
from mappings.achievements import CLUB_INTERNATIONAL_TITLE
from mappings.achievements import CLUB_NATIONAL_TITLE
from mappings.achievements import MINOR_TITLE

def initialize_clubs():

    return defaultdict(
        lambda: {
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
                "points": 0,
                "clean_sheets": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goal_matches": 0,
                "assist_matches": 0,
                "goal_contributions": 0
            },

            "positions": Counter(),

            "derived": {
                "season_count": 0,
                "points_per_match": 0.0,
                "minutes_per_match": 0.0,
                "win_rate": 0.0,
                "goals_per_90": 0.0,
                "assists_per_90": 0.0,
                "contributions_per_90": 0.0,
                "primary_position": ""
            },

            "competitions": defaultdict(
                lambda: {
                    "matches": 0,
                    "minutes": 0,
                    "goals": 0,
                    "assists": 0
                }
            ),

            "awards": {
                "team_titles": Counter(),
                "individual_titles": Counter()
            }
        }
    )

def initialize_career():
    return {
        "club": {
            "seasons": set(),
            "matches": 0,
            "minutes": 0,
            "goals": 0,
            "assists": 0,
            "goal_contributions": 0,
            "team_titles": 0,
            "individual_titles": 0
        },
        "national": {
            "seasons": set(),
            "matches": 0,
            "minutes": 0,
            "goals": 0,
            "assists": 0,
            "goal_contributions": 0,
            "team_titles": 0,
            "individual_titles": 0
        }
    }

def process_matches(clubs, matches):

    for match in matches:

        club_id = match.get("club_id")

        if club_id is None:
            continue

        club_id = str(club_id)

        club = clubs[club_id]

        season = match.get("season")

        if season is not None:
            club["seasons"].add(season)

        club["stats"]["matches"] += 1

        if match.get("participation"):
            club["stats"]["participations"] += 1

        club["stats"]["minutes"] += match.get("minutes") or 0
        goals = match.get("goals") or 0
        assists = match.get("assists") or 0
        club["stats"]["goals"] += goals
        club["stats"]["assists"] += assists
        club["stats"]["goals_conceded"] += match.get("goals_conceded") or 0
        club["stats"]["points"] += match.get("club_points") or 0
        club["stats"]["goal_contributions"] += goals + assists

        if match.get("started"):
            club["stats"]["starts"] += 1

        if match.get("captain"):
            club["stats"]["captain_matches"] += 1
        
        if (match.get("participation") and (match.get("goals_conceded") or 0) == 0):
            club["stats"]["clean_sheets"] += 1
        
        if match.get("club_points") == 3:
            club["stats"]["wins"] += 1
        
        if match.get("club_points") == 1:
            club["stats"]["draws"] += 1
        
        if match.get("club_points") == 0:
            club["stats"]["losses"] += 1
        
        if match.get("goals") == 0:
            club["stats"]["goal_matches"] += 1
        
        if match.get("assists") == 0:
            club["stats"]["assist_matches"] += 1

        position = match.get("position")

        if position:
            club["positions"][position] += 1

        competition = match.get("competition_type")

        if competition:

            comp = club["competitions"][competition]

            comp["matches"] += 1
            comp["minutes"] += match.get("minutes") or 0
            comp["goals"] += match.get("goals") or 0
            comp["assists"] += match.get("assists") or 0

def process_achievements(clubs, achievements):
    for achievement in achievements:
        
        club_list = []

        title = achievement.get("title")

        if title in IGNORED_TITLE:
            continue

        club_id = achievement.get("club_id")

        if club_id is None:
            season = achievement.get("season_id")
            
            if season is None:
                continue
            
            for club, values in clubs.items():
                if season in values["seasons"]:
                    club_list.append(club)

        else:
            club_id = str(club_id)
            club_list.append(club_id)

        for club_id in club_list:
            club = clubs[club_id]

            if title in INDIVIDUAL_TITLE:
                club["awards"]["individual_titles"][title] += 1
            
            elif title in NATIONAL_WORLD_TITLE or title in NATIONAL_CONTINENTAL_TITLE or title in CLUB_INTERNATIONAL_TITLE or title in CLUB_NATIONAL_TITLE or title in MINOR_TITLE:
                club["awards"]["team_titles"][title] += 1

            else:
                print(f"Unknown title: {title} for club_id: {club_id}")

def finalize_clubs(clubs):

    for club in clubs.values():

        club["seasons"] = sorted(club["seasons"])

        club["derived"]["season_count"] = len(club["seasons"])

        participations = club["stats"]["participations"]
        wins = club["stats"]["wins"]
        minutes = club["stats"]["minutes"]
        positions = club["positions"]

        if participations:
            club["derived"]["points_per_match"] = round(club["stats"]["points"] / participations, 3)
            club["derived"]["minutes_per_match"] = round(minutes / participations, 1)
            club["derived"]["win_rate"] = round(wins / participations, 4)

        if minutes:
            club["derived"]["goals_per_90"] = round(club["stats"]["goals"] * 90 / minutes, 3)
            club["derived"]["assists_per_90"] = round(club["stats"]["assists"] * 90 / minutes, 3)
            club["derived"]["contributions_per_90"] = round(club["stats"]["goal_contributions"] * 90 / minutes, 3)
        
        if positions:
            club["derived"]["primary_position"] = (positions.most_common(1)[0][0])

        club["positions"] = dict(club["positions"])
        
        club["competitions"] = dict(club["competitions"])

def is_national_team(club):
    competitions = club.get("competitions", {})

    return any(
        "national" in competition.lower()
        for competition in competitions
    )

def build_career(clubs):

    career = initialize_career()

    for club in clubs.values():

        target = (
            career["national"]
            if is_national_team(club)
            else career["club"]
        )

        target["seasons"].update(
            club.get("seasons", [])
        )

        stats = club.get("stats", {})

        target["matches"] += stats.get("matches", 0)
        target["minutes"] += stats.get("minutes", 0)
        target["goals"] += stats.get("goals", 0)
        target["assists"] += stats.get("assists", 0)
        target["goal_contributions"] += stats.get(
            "goal_contributions", 0
        )

        awards = club.get("awards", {})

        target["team_titles"] += sum(
            awards.get("team_titles", {}).values()
        )

        target["individual_titles"] += sum(
            awards.get("individual_titles", {}).values()
        )

    for scope in ("club", "national"):
        career[scope]["season_count"] = len(
            career[scope]["seasons"]
        )

        del career[scope]["seasons"]

    return career

def build_player_clubs(player_data):

    matches = player_data["matches"]
    achievements = player_data["achievements"]

    clubs = initialize_clubs()

    process_matches(clubs, matches)

    process_achievements(clubs, achievements)

    finalize_clubs(clubs)

    return dict(clubs)