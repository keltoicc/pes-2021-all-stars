import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

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

def main():

    teams = yaml.safe_load(
        Path("config/teams_debug.yml").read_text(encoding="utf-8")
    )["teams"]

    teams_dir = Path("data/processed/players")
    output_dir = Path("data/built/players/teams")
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
        
        players = []

        for player in all_players:

            print(f"{player['ID_transfermarkt']} {player['name']}")
        
            data = obtain_players(str(player['ID_transfermarkt']), str(team['ID_transfermarkt']))

            if not data:
                continue

            players.append(data)

        players.sort(key=lambda x: x["score"], reverse=True)

        output_path = output_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(players, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
