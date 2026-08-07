import json
from pathlib import Path
import yaml
import re
import sys
import csv

from publisher import publish_directory

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

def get_country_id(country, team_name):

    if not country:
        return None

    if country == "Europe" or country == "Africa" or country == "North, Central America and Caribbean" or country == "South America" or country == "Asia":
        country = team_name

    if country == "Bosnia-Herzegovina":
        country = "Bosnia and Herzegovina"

    if country == "Czechia":
        country = "Czech Republic"

    if country == "United States of America":
        country = "USA"

    if country == "South Korea":
        country = "Republic of Korea"

    if country == "North Korea":
        country = "Korea DPR"

    if country == "the Congo":
        country = "Congo"
    
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

def get_team_data(team):

    data = {
        "id": team['ID_pes'],
        "name": team['name'],
        "slug": slugify_web(team['name']),

        "country": get_country_id(team['country'], team['name']),

        "crest": f"/images/teams/{team['ID_pes']}.png",
    }

    return data

def main(yml = "teams"):

    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
    )["teams"]

    teams_dir = Path("data/processed/players")
    tactics_dir = Path("data/built/tactics")
    output_dir = Path("data/published/teams")
    output_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        team_data = get_team_data(team)

        output_path = output_dir / f"{team_data['id']}-{team_data['slug']}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                team_data,
                f,
                indent=4,
                ensure_ascii=False
            )

    publish_directory("teams")

if __name__ == "__main__":
    main()
