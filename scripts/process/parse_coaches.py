from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def merge_coaches(rows: list[dict]) -> dict:    
    merged = {}

    for row in rows:
        coach = row["name"]

        if coach not in merged:
            merged[coach] = {
                "name": coach,
                "matches": 0,
                "ppp": 0,
            }

        merged[coach]["matches"] += row["matches"]
        merged[coach]["ppp"] += row["ppp"]

    return merged

def parse_table(html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table.items tbody tr")

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 10:
            continue
        
        name = cols[2].get_text(strip=True)
        matches = int(cols[8].get_text(strip=True).replace(".", ""))
        if matches == 0:
            ppp = 0.0
        else:
            ppp = float(cols[9].get_text(strip=True).replace(",", "."))

        data.append({
            "name": name,
            "matches": matches,
            "ppp": ppp,
        })

    return data

def obtain_json(team: dict, processed_dir: Path):
    raw_dir = Path("data/raw/transfermarkt/teams")

    html_file = raw_dir / f"{slugify(team['name'])}_coaches.html"

    if not html_file.exists():
        print(f"No hay HTML para {team['name']}")
        return

    all_rows = []

    rows = parse_table(html_file)
    all_rows.extend(rows)

    merged = merge_coaches(all_rows)

    print(merged)

def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    processed_dir = Path("data/processed/teams/coaches")
    processed_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        print(team["name"])

        obtain_json(team, processed_dir)

if __name__ == "__main__":
    main()
