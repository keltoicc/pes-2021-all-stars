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

def get_team_data(team):

    data = {
        "id": team['ID_pes'],
        "name": team['name'],
        "slug": slugify_web(team['name']),

        "country": team['country'],

        "crest": f"/images/teams/{team['ID_pes']}.png",
    }

    return data

def main(yml = "teams_debug"):

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
