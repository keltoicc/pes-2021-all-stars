import requests
from pathlib import Path
import yaml
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def fetch(url: str, output_path: Path):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    output_path.write_text(r.text, encoding="utf-8")

def get_urls(player: dict, team: dict, output_dir: Path):

    profile_path = output_dir / "profile"
    profile_path.mkdir(parents=True, exist_ok=True)
    filename = f"{player['ID_transfermarkt']}.json"
    print("Descargando", filename, "(", player['name'], ")")
    
    url = "https://tmapi-alpha.transfermarkt.technology/players?ids[]=" + str(player['ID_transfermarkt'])

    try:
        fetch(url, profile_path / filename)
    except requests.RequestException as e:
        print(f"ERROR request: {e}")
    
    stats_path = output_dir / "stats"
    stats_path.mkdir(parents=True, exist_ok=True)
    print("Descargando ", filename, "...")

    url = "https://www.transfermarkt.com/ceapi/performance-game/" + str(player['ID_transfermarkt'])

    try:
        fetch(url, stats_path / filename)
    except requests.RequestException as e:
        print(f"ERROR request: {e}")
    
    achievements_path = output_dir / "achievements"
    achievements_path.mkdir(parents=True, exist_ok=True)
    filename = f"{player['ID_transfermarkt']}.html"
    print("Descargando ", filename, "...")
    
    url = "https://www.transfermarkt.com/" + player['name_transfermarkt'] + "/erfolge/spieler/" + str(player['ID_transfermarkt'])

    try:
        fetch(url, achievements_path / filename)
    except requests.RequestException as e:
        print(f"ERROR request: {e}")

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
        
        json_file = player_dir / f"{team['ID_pes']}_{team['name']}.json"

        if not json_file.exists():
            print(f"No hay json para {team['name']}")
            continue
        
        # Obtener los jugadores del json
        with json_file.open(encoding="utf-8") as f:
            all_players = json.load(f)
        
        output_dir = Path("data/raw/transfermarkt/players")
        output_dir.mkdir(parents=True, exist_ok=True)

        for player in all_players:
            
            get_urls(player, team, output_dir)

if __name__ == "__main__":
    main()
