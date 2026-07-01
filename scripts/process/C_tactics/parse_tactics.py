from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def merge_tactics(rows: list[dict]) -> dict:    
    merged = {}

    for row in rows:
        tactic = row["tactic"]

        if tactic not in merged:
            merged[tactic] = {
                "tactic": tactic,
                "matches": 0,
            }

        merged[tactic]["matches"] += 1
        
    return merged

def parse_table(html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table.items tbody tr")

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 10:
            continue
        
        tactic = cols[9].get_text(strip=True)

        # Eliminar si se desconoce la táctica
        if tactic == "?" or tactic == "":
            continue

        data.append({
            "tactic": tactic,
        })

    return data

def obtain_json(coach: dict, team: dict, processed_dir: Path):
    raw_dir = Path("data/raw/transfermarkt/coaches")

    html_file = raw_dir / f"{slugify(coach['coach'])}_{slugify(team['name'])}.html"

    if not html_file.exists():
        print(f"No hay HTML para {team['name']}")
        return

    print(f"Procesando {html_file}")

    all_rows = []

    rows = parse_table(html_file)
    all_rows.extend(rows)

    merged = merge_tactics(all_rows)

    # Convertimos a lista y ordenamos por partidos
    result = sorted(
        merged.values(),
        key=lambda x: (
            x["matches"],
        ),
    reverse=True
    )

    output_path = processed_dir / f"{slugify(coach['coach'])}_{slugify(team['name'])}.json"
    output_path.write_text(
        json.dumps(result, indent=4, ensure_ascii=False),
        encoding="utf-8"
    ) 

def main():
    teams = yaml.safe_load(
        Path("config/teams_debug.yml").read_text(encoding="utf-8")
    )["teams"]

    coach_dir = Path("data/built/coaches")

    processed_dir = Path("data/processed/tactics")
    processed_dir.mkdir(parents=True, exist_ok=True)

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

        obtain_json(coach, team, processed_dir)

if __name__ == "__main__":
    main()
