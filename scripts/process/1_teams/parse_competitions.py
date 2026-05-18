from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml

def parse_table(html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table.items tbody tr")

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 9:
            continue

        club = cols[2].get_text(strip=True)
        matches = int(cols[3].get_text(strip=True).replace(".", ""))
        wins = int(cols[4].get_text(strip=True).replace(".", ""))
        goal_diff = int(cols[7].get_text(strip=True).replace(".", ""))
        points = int(cols[8].get_text(strip=True).replace(".", ""))

        data.append({
            "club": club,
            "matches": matches,
            "wins": wins,
            "goal_diff": goal_diff,
            "points": points,
        })

    return data

def get_html_files(comp: dict, raw_dir: Path) -> list[Path]:
    prefix = f"{comp['name']}_{comp['ranking']['type']}_"
    return sorted(raw_dir.glob(f"{prefix}*.html"))

def merge_clubs(rows: list[dict]) -> dict:
    merged = {}

    for row in rows:
        club = row["club"]

        if club not in merged:
            merged[club] = {
                "club": club,
                "matches": 0,
                "wins": 0,
                "goal_diff": 0,
                "points": 0,
            }

        merged[club]["matches"] += row["matches"]
        merged[club]["wins"] += row["wins"]
        merged[club]["goal_diff"] += row["goal_diff"]
        merged[club]["points"] += row["points"]

    return merged

def obtain_json(comp: dict, processed_dir: Path):
    raw_dir = Path("data/raw/transfermarkt/competitions")

    html_files = get_html_files(comp, raw_dir)

    if not html_files:
        print(f"No hay HTML para {comp['name']}")
        return

    print(f"Procesando {comp['name']} ({len(html_files)} ficheros)")

    all_rows = []

    for html_file in html_files:
        print("  -", html_file.name)
        rows = parse_table(html_file)
        all_rows.extend(rows)

    merged = merge_clubs(all_rows)

    # Convertimos a lista y ordenamos por puntos, partidos, victorias y diferencia de goles
    result = sorted(
        merged.values(),
        key=lambda x: (
            x["points"],
            x["matches"],
            x["wins"],
            x["goal_diff"],
        ),
    reverse=True
    )

    output_path = processed_dir / f"{comp['name']}_{comp['ranking']['type']}.json"
    output_path.write_text(
        json.dumps(result, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )  

def main():
    competitions = yaml.safe_load(
        Path("config/competitions.yml").read_text(encoding="utf-8")
    )["competitions"]

    processed_dir = Path("data/processed/competitions")
    processed_dir.mkdir(parents=True, exist_ok=True)

    for comp in competitions:
        print(comp["name"])
        
        if comp["primary"] == False:
            print("Segunda División de", comp["relegated_from"], ". No es necesario generar json.")

        else:
            obtain_json(comp, processed_dir)

if __name__ == "__main__":
    main()
