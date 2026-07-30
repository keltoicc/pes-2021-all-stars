import json
from pathlib import Path
import yaml
import re
import sys

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

def get_squad_data(team, squad_name = "All-Time"):

    team_slug = slugify_web(team['name'])

    data = {
        "id": team['ID_pes'],

        "team": team['ID_pes'],

        "name": squad_name,
        "slug": f"{team_slug}-{slugify_web(squad_name)}"
    }

    return data

def main(yml = "teams_debug"):

    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
    )["teams"]

    teams_dir = Path("data/processed/players")
    tactics_dir = Path("data/built/tactics")
    output_dir = Path("data/published/squads")
    output_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        if not team["ID_transfermarkt"]:
            continue

        squad_data = get_squad_data(team)

        output_path = output_dir / f"{squad_data['id']}-{squad_data['slug']}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                squad_data,
                f,
                indent=4,
                ensure_ascii=False
            )

    publish_directory("squads")

if __name__ == "__main__":
    main()
