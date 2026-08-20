import json
from pathlib import Path
import yaml
import re
import sys
import csv

from .publisher import publish_directory

sys.path.append(str(Path(__file__).parent))

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def slugify_web(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\.", "", name)
    name = re.sub(r"[^\w]+", "-", name)
    return name.strip("-")

def get_country_id(country):

    if not country:
        return None

    if country == "Bosnia-Herzegovina":
        country = "Bosnia and Herzegovina"
    
    if country == "Czechia":
        country = "Czech Republic"
    
    if country == "United States of America" or country == "United States":
        country = "USA"
    
    if country == "South Korea":
        country = "Republic of Korea"
    
    if country == "North Korea":
        country = "Korea DPR"
    
    if country == "the Congo":
        country = "Congo"
    
    if country == "Serbia & Montenegro":
        country = "Serbia and Montenegro"

    if country == "Cape Verde":
        country = "Cabo Verde"

    if country == "Guinea-Bissau":
        country = "Guinea Bissau"

    if country == "DR Congo":
        country = "Congo DR"

    if country == "Türkiye":
        country = "Turkey"
    
    countries_dir = Path(f"config/evowebid")

    countries_file = countries_dir / "countries.csv"

    if not countries_file.exists():
        # print(f"No hay csv para países")
        return 0

    with countries_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            #print(row)
            if row["English:"] == country:
                return int(row["Country ID:"])

    print(f"No se encontró el país {country} en el csv")
    return 0

def get_team_id(team_id):

    teams = yaml.safe_load(
            Path(f"config/teams.yml").read_text(encoding="utf-8")
        )["teams"]

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        if team['ID_transfermarkt'] == int(team_id):
            return int(team["ID_pes"])

    # print(f"No se encontró el equipo con ID_transfermarkt {team_id} en el yml")
    return None

def build_player_career(clubs: dict) -> list[dict]:
    career = []

    for team_id, team_data in clubs.items():
        if team_data.get("type") != "club":
            continue

        pes_id = get_team_id(team_id)

        if not pes_id:
            continue
        
        seasons = sorted(set(team_data.get("seasons", [])))

        if not seasons:
            continue

        start = seasons[0]
        previous = seasons[0]

        for season in seasons[1:]:
            if season == previous + 1:
                previous = season
                continue

            career.append({
                "team": pes_id,
                "fromSeason": start,
                "toSeason": previous
            })

            start = season
            previous = season

        career.append({
            "team": pes_id,
            "fromSeason": start,
            "toSeason": previous
        })

    career.sort(key=lambda x: (x["fromSeason"], x["toSeason"], x["team"]))

    return career

def get_player_data(id_transfermarkt) -> dict:

    player_data_dir = Path("data/processed/players/normalized")

    player_file = player_data_dir / f"{id_transfermarkt}.json"

    if not player_file.exists():
        print(f"No hay json para {id_transfermarkt}")
        return {}

    with player_file.open(encoding="utf-8") as f:
        all_data = json.load(f)

    player_data = all_data.get("player", {})
    clubs = all_data.get("clubs", {})

    name = player_data.get("name")

    data = {
        "id": int(id_transfermarkt),

        "name": name,
        "slug": f"{slugify_web(name)}",

        "birthDate": player_data.get("dateOfBirth"),
        "birthPlace": player_data.get("placeOfBirth"),

        "country": get_country_id(player_data.get("nation_1")),
        "secondCountry": get_country_id(player_data.get("nation_2")),

        "height": int(player_data.get("height") * 100) if player_data.get("height") else None,
        "preferredFoot": player_data.get("foot").lower() if player_data.get("foot") else None,

        "career": build_player_career(clubs)
    }

    return {k: v for k, v in data.items() if v is not None}

def main(yml = "teams_debug"):

    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
    )["teams"]

    player_dir = Path("data/built/players/teams")
    output_dir = Path("data/published/players")
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
            all_data = json.load(f)

        all_players = all_data.get("players", [])

        for player in all_players:

            print(f"Exportando {player['player']['name']}")
        
            player_data = get_player_data(player['player']['ID_transfermarkt'])

            output_path = output_dir / f"{player_data['id']}-{player_data['slug']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    player_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

    publish_directory("players")

if __name__ == "__main__":
    main()
