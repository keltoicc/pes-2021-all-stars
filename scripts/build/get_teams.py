import json
from pathlib import Path
import yaml

def compute_offset(comp: dict, competitions_by_name: dict) -> int:
    offset = 0
    current = comp

    while not current.get("primary", True):
        parent = competitions_by_name[current["relegated_from"]]
        offset += parent["teams"]
        current = parent

    return offset 

def get_teams(comp: dict, offset: int):
    processed_dir = Path("data/processed/competitions")

    if comp["primary"] == False:
        json_file = processed_dir / f"{comp['relegated_from']}_{comp['ranking']['type']}.json"

    else:
        json_file = processed_dir / f"{comp['name']}_{comp['ranking']['type']}.json"
    
    if not json_file.exists():
        print(f"No hay json para {comp['name']}")
        return
    
    # Obtener los equipos del json
    with json_file.open(encoding="utf-8") as f:
        ranking = json.load(f)
        
    start = offset
    end = offset + comp["teams"]
    selected = ranking[start:end]

    result_dir = Path("data/processed/teams")
    result_dir.mkdir(parents=True, exist_ok=True)

    output_path = result_dir / f"{comp['name']}.yml"

    output = {
        "competition": {
            "id": comp["ID"],
            "name": comp["name"],
        },
        "teams": []
    }

    for idx, team in enumerate(selected, start=offset + 1):
        output["teams"].append({
            "rank": idx,
            "club": team["club"],
            "points": team["points"],
        })
    
    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            output,
            f,
            allow_unicode=True,
            sort_keys=False
        )
    
    print(f"Generado {output_path.name}")



def main():
    competitions = yaml.safe_load(
        Path("config/competitions.yml").read_text(encoding="utf-8")
    )["competitions"]

    competitions_by_name = {
        comp["name"]: comp
        for comp in competitions
    }

    for comp in competitions:
        
        offset = compute_offset(comp, competitions_by_name)
        get_teams(comp, offset)


if __name__ == "__main__":
    main()
