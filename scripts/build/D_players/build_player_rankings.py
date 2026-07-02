from collections import defaultdict, Counter
import json
from pathlib import Path
import yaml
import re
import sys
import math

sys.path.append(str(Path(__file__).parent))

from build.D_players.mappings.achievements import TITLE_POINTS
from build.D_players.mappings.achievements import INDIVIDUAL_AWARD_POINTS
from build.D_players.mappings.achievements import NATIONAL_WORLD_TITLE
from build.D_players.mappings.achievements import NATIONAL_CONTINENTAL_TITLE
from build.D_players.mappings.achievements import CLUB_INTERNATIONAL_TITLE
from build.D_players.mappings.achievements import CLUB_NATIONAL_TITLE
from build.D_players.mappings.achievements import MINOR_TITLE

MAX_SEASONS = 10
MAX_MATCHES = 300
MAX_MINUTES = 25000

TITLE_WEIGHTS = {
    "NATIONAL_WORLD_TITLE": 70,
    "NATIONAL_CONTINENTAL_TITLE": 60,
    "CLUB_INTERNATIONAL_TITLE": 65,
    "CLUB_NATIONAL_TITLE": 25,
    "MINOR_TITLE": 10,
}

DEFAULT_INDIVIDUAL_AWARD_POINTS = 10

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def initialize_clubs():

    return defaultdict(
        lambda: {
            "importance": {
                "presence": 0.0,
                "sporting": 0.0,
                "titles": 0.0,
                "individual": 0.0,
                "total": 0.0
            },

            "positions": Counter(),
        }
    )

def build_career_stats(player_data):
    clubs = player_data.get("clubs", {})

    seasons = set()
    matches = 0
    minutes = 0

    for club in clubs.values():
        seasons.update(club.get("seasons", []))

        stats = club.get("stats", {})
        matches += stats.get("matches", 0)
        minutes += stats.get("minutes", 0)

    return {
        "seasons": len(seasons),
        "matches": matches,
        "minutes": minutes
    }

def get_title_category(title):

    if title in NATIONAL_WORLD_TITLE:
        return "NATIONAL_WORLD_TITLE"

    if title in NATIONAL_CONTINENTAL_TITLE:
        return "NATIONAL_CONTINENTAL_TITLE"

    if title in CLUB_INTERNATIONAL_TITLE:
        return "CLUB_INTERNATIONAL_TITLE"

    if title in CLUB_NATIONAL_TITLE:
        return "CLUB_NATIONAL_TITLE"

    if title in MINOR_TITLE:
        return "MINOR_TITLE"

    return None

def get_title_weight(title):
    if title in TITLE_POINTS:
        return TITLE_POINTS[title]

    category = get_title_category(title)

    if category is None:
        print(f"El premio {title} no está clasificado en ninguna categoría")
        return 0

    return TITLE_WEIGHTS[category]

def get_individual_award_weight(title):
    return INDIVIDUAL_AWARD_POINTS.get(
        title,
        DEFAULT_INDIVIDUAL_AWARD_POINTS
    )

def calc_presence(club):
    season_count = club.get("derived", {}).get("season_count", 0)
    matches = club.get("stats", {}).get("matches", 0)
    minutes = club.get("stats", {}).get("minutes", 0)

    season_score = min(season_count / MAX_SEASONS, 1.0)
    match_score = min(matches / MAX_MATCHES, 1.0)
    minute_score = min(minutes / MAX_MINUTES, 1.0)

    presence_score = season_score * 0.4 + match_score * 0.2 + minute_score * 0.4
    return presence_score

def calc_sporting(club):
    matches = club.get("stats", {}).get("matches", 0)

    if matches == 0:
        return 0.0

    starts = club.get("stats", {}).get("starts", 0)
    captain_matches = club.get("stats", {}).get("captain_matches", 0)
    minutes = club.get("stats", {}).get("minutes", 0)
    contributions_per_90 = club.get("derived", {}).get("contributions_per_90", 0)

    starter_rate = starts / matches
    captain_rate = captain_matches / matches
    minutes_per_match = minutes / matches

    captain_score = min(captain_rate * 4, 1.0)
    minutes_score = min(minutes_per_match / 90, 1.0)

    protagonism_score = (starter_rate * 0.5 + minutes_score * 0.3 + captain_score * 0.2)

    impact_score = min(contributions_per_90 / 0.8, 1.0)

    sporting_score = protagonism_score * 0.7 + impact_score * 0.3

    return sporting_score

def calc_titles(club):

    team_titles = (
        club.get("awards", {})
            .get("team_titles", {})
    )

    raw_score = 0

    for title, count in team_titles.items():

        weight = get_title_weight(title)

        raw_score += weight * count

    return min(
        math.log1p(raw_score) / math.log1p(500),
        1.0
    )

def calc_individual(club):

    individual_titles = (
        club.get("awards", {})
            .get("individual_titles", {})
    )

    raw_score = 0

    for title, count in individual_titles.items():

        weight = get_individual_award_weight(title)

        raw_score += weight * count

    return min(
        math.log1p(raw_score) / math.log1p(300),
        1.0
    )

def calculate_score(player_id):

    normalized_file = Path(f"data/processed/players/normalized/{player_id}.json")

    if not normalized_file.exists():
        print(f"No hay json para {player_id}")
        return
    
    with normalized_file.open(encoding="utf-8") as f:
        player_data = json.load(f)
    
    # print(player_data.get("player", {}).get("short_name"))
    
    career = build_career_stats(player_data)

    clubs = initialize_clubs()

    for club_id, club_data in player_data.get("clubs", {}).items():

        presence_score = calc_presence(club_data) or 0.0
        sporting_score = calc_sporting(club_data) or 0.0
        titles_score = calc_titles(club_data) or 0.0
        individual_score = calc_individual(club_data) or 0.0
        total_score = presence_score * 0.35 + sporting_score * 0.35 + titles_score * 0.20 + individual_score * 0.10

        # print(f"Puntuaciones para {club_id}: {presence_score}, {sporting_score}, {titles_score}, {individual_score}, {total_score}")

        clubs[club_id]["importance"]["presence"] = presence_score
        clubs[club_id]["importance"]["sporting"] = sporting_score
        clubs[club_id]["importance"]["titles"] = titles_score
        clubs[club_id]["importance"]["individual"] = individual_score
        clubs[club_id]["importance"]["total"] = total_score

        matches = club_data.get("stats", {}).get("matches", 0)
        
        positions = {}

        for position, count in club_data.get("positions", {}).items():
            if count >= 10 or (matches > 0 and count / matches >= 0.2):
                positions[position] = count

        if not positions:
            player = player_data.get("player", {})

            for field in ("position_1", "position_2", "position_3"):
                position = player.get(field)

                if position:
                    positions[position] = None
                
            if not positions:
                position_group = player.get("position_group")
                positions[position_group] = None
        
        clubs[club_id]["positions"] = positions
            
    data = {
        "player_id": player_id,
        "profile": player_data.get("player"),
        "clubs": clubs
    }

    # print(data)
    return data

def main(yml = "teams"):

    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
    )["teams"]

    teams_dir = Path("data/processed/players")
    output_dir = Path("data/built/players/scores")
    output_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        json_file = teams_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        if not json_file.exists():
            print(f"No hay json para {team['name']}")
            continue

        # Obtener los jugadores del json
        with json_file.open(encoding="utf-8") as f:
            all_players = json.load(f)
        
        for player in all_players:

            print(f"{player['ID_transfermarkt']} {player['name']}")
        
            data = calculate_score(player['ID_transfermarkt'])

            if not data:
                continue

            output_path = output_dir / f"{player['ID_transfermarkt']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
