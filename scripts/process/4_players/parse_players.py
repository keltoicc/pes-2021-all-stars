from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re
import sys

sys.path.append(str(Path(__file__).parent))

from parsers.profile_parser import parse_profile
from parsers.stats_parser import parse_stats
from parsers.achievement_parser import parse_achievements

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def build_player(player_id):

    base_path = "data/raw/transfermarkt/players"

    profile_file = Path(f"{base_path}/profile/{player_id}.json")
    stats_file = Path(f"{base_path}/stats/{player_id}.json")
    achievements_file = Path(f"{base_path}/achievements/{player_id}.html")

    if not profile_file.exists() or not stats_file.exists() or not achievements_file.exists():
        print(f"No hay json para {player_id}")
        return

    profile = parse_profile(profile_file)

    stats = parse_stats(stats_file)

    achievements = parse_achievements(achievements_file)

    return {
        "player": profile,
        "matches": stats,
        "achievements": achievements
    }

def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    player_dir = Path("data/processed/players")
    output_dir = Path("data/processed/players/normalized")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = Path("data/raw/transfermarkt/teams")
    raw_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            #print("No hay ID_transfermarkt para", slugify(team["name"]))
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
            
            data = build_player(player['ID_transfermarkt'])

            output_path = output_dir / f"{player['ID_transfermarkt']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
