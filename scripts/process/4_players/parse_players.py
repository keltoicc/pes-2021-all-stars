from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def get_player_data(player: dict, team: dict, output_dir: Path):
    pass

def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    player_dir = Path("data/processed/players")

    raw_dir = Path("data/raw/transfermarkt/teams")
    raw_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            print("No hay ID_transfermarkt para", team["name"])
            continue
        
        json_file = player_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        if not json_file.exists():
            print(f"No hay json para {team['name']}")
            continue
        
        # Obtener los jugadores del json
        with json_file.open(encoding="utf-8") as f:
            all_players = json.load(f)
        
        output_dir = player_dir / slugify(team['name'])
        output_dir.mkdir(parents=True, exist_ok=True)

        for player in all_players:
            
            get_player_data(player, team, output_dir)

if __name__ == "__main__":
    main()
