from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def get_html_files(team: dict, raw_dir: Path) -> list[Path]:
    prefix = f"{team['ID_pes']}_{slugify(team['name'])}_players_"
    return sorted(raw_dir.glob(f"{prefix}*.html"))

def parse_table(html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table.items tbody tr")

    base_url = "https://www.transfermarkt.com"

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 12:
            continue

        name = cols[3].get_text(strip=True)
        team = cols[4].get_text(strip=True)
        matches = cols[7].get_text(strip=True)
        link = cols[3].select_one('a[href]')
        if link:
            url = link["href"]

            parts = url.strip("/").split("/")

            name_transfermarkt = parts[0]
            ID_transfermarkt = parts[-1]
        
        data.append({
            "name": name,
            "matches": matches,
            "ID_transfermarkt": ID_transfermarkt,
            "name_transfermarkt": name_transfermarkt,
            "team": team,
        })

    return data

def obtain_json(team: dict, processed_dir: Path):
    raw_dir = Path("data/raw/transfermarkt/teams")

    html_files = get_html_files(team, raw_dir)

    if not html_files:
        print(f"No hay HTML para {team['name']}")
        return
    
    print(f"Procesando {team['name']} ({len(html_files)} ficheros)")

    all_rows = []

    for html_file in html_files:
        print("  -", html_file.name)
        rows = parse_table(html_file)
        all_rows.extend(rows)

    output_path = processed_dir / f"{team['ID_pes']}_{slugify(team['name'])}.json"
    output_path.write_text(
        json.dumps(all_rows, indent=4, ensure_ascii=False),
        encoding="utf-8"
    ) 

def main(yml = "teams"):
    teams = yaml.safe_load(
        Path(f"config/{yml}.yml").read_text(encoding="utf-8")
    )["teams"]

    processed_dir = Path("data/processed/players")
    processed_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:

        if not team["ID_transfermarkt"]:
            # print("No hay ID_transfermarkt para", team["name"])
            continue
        
        obtain_json(team, processed_dir)

if __name__ == "__main__":
    main()
