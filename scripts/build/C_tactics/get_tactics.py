import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def get_tactic(coach: dict, team: dict):
    processed_dir = Path("data/processed/tactics")

    json_file = processed_dir / f"{slugify(coach['coach'])}_{slugify(team['name'])}.json"

    if not json_file.exists():
        print(f"No hay json para {team['name']}")
        return
    
    # Obtener los entrenadores del json
    with json_file.open(encoding="utf-8") as f:
        all_tactics = json.load(f)
    
    if len(all_tactics) == 0:
        tactic = {"tactic": "UNKNOWN"}

    else:
        tactic = all_tactics[0]

    result_dir = Path("data/built/tactics")
    result_dir.mkdir(parents=True, exist_ok=True)

    output_path = result_dir / f"{team['ID_pes']}_{slugify(team['name'])}.yml"

    output = {
        "team": {
            "id": team["ID_pes"],
            "name": team["name"],
            "coach": coach["coach"],
            "tactic": tactic["tactic"]
        },
    }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            output,
            f,
            allow_unicode=True,
            sort_keys=False
        )
    
    print(f"Generado {output_path.name}")

def main():
    teams = yaml.safe_load(
        Path("config/teams_debug.yml").read_text(encoding="utf-8")
    )["teams"]

    coach_dir = Path("data/built/coaches")

    for team in teams:

        if not team["ID_transfermarkt"]:
            #print("No hay ID para", team["name"])
            continue

        coach_path = coach_dir / f"{team['ID_pes']}_{team['name']}.yml"

        if not coach_path.exists():
            print(f"No hay fichero de entrenador para {team['name']}")
            continue

        coach = yaml.safe_load(
            Path(coach_path).read_text(encoding="utf-8")
        )["team"]
        
        get_tactic(coach, team)

if __name__ == "__main__":
    main()
