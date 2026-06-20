from collections import defaultdict, Counter
import json
from pathlib import Path
import yaml
import re
import sys

sys.path.append(str(Path(__file__).parent))

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

def calc_presence(club, career):
    season_count = club.get("derived", {}).get("season_count", 0)
    matches = club.get("stats", {}).get("matches", 0)
    minutes = club.get("stats", {}).get("minutes", 0)

    season_score = season_count / career["seasons"] if career["seasons"] else 0
    match_score = matches / career["matches"] if career["matches"] else 0
    minute_score = minutes / career["minutes"] if career["minutes"] else 0

    presence_score = season_score * 0.4 + match_score * 0.3 + minute_score * 0.3
    return presence_score

def calc_sporting(club):
    pass

def calc_titles(club):
    pass

def calc_individual(club):
    pass

def calculate_score(player_id):

    normalized_file = Path(f"data/processed/players/normalized/{player_id}.json")

    if not normalized_file.exists():
        print(f"No hay json para {player_id}")
        return
    
    with normalized_file.open(encoding="utf-8") as f:
        player_data = json.load(f)
    
    career = build_career_stats(player_data)

    clubs = initialize_clubs()

    for club_id, club_data in player_data.get("clubs", {}).items():

        presence_score = calc_presence(club_data, career) or 0.0
        sporting_score = calc_sporting(club_data) or 0.0
        titles_score = calc_titles(club_data) or 0.0
        individual_score = calc_individual(club_data) or 0.0
        total_score = presence_score * 0.35 + sporting_score * 0.35 + titles_score * 0.20 + individual_score * 0.10

        print(presence_score, sporting_score, titles_score, individual_score, total_score)

        continue
        clubs[club_id]["importance"]["presence"] = presence_score
        clubs[club_id]["importance"]["sporting"] = sporting_score
        clubs[club_id]["importance"]["titles"] = titles_score
        clubs[club_id]["importance"]["individual"] = individual_score
        clubs[club_id]["importance"]["total"] = total_score

        for position, count in club.get("positions", {}).items():
            clubs[club_id]["positions"][position] += count
    
    data = {
        "player_id": player_id,
        "profile": player_data.get("player"),
        "clubs": clubs
    }

    # print(data)
    # return data

def main():

    teams = yaml.safe_load(
        Path("config/teams_debug.yml").read_text(encoding="utf-8")
    )["teams"]

    player_dir = Path("data/processed/players")
    output_dir = Path("data/built/players/scores")
    output_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        json_file = player_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

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
