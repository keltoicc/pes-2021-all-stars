from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml

def parse_table(html_path: Path):
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

def get_file():
    pass

def main():
    competitions = yaml.safe_load(
        Path("config/competitions.yml").read_text(encoding="utf-8")
    )["competitions"]

    processed_dir = Path("data/processed/competitions")
    processed_dir.mkdir(parents=True, exist_ok=True)

    filePath = Path("data/raw/transfermarkt/ENGLAND_D1_LEAGUE_all_time_table_1.html")

    data = parse_table(filePath)

    print(data)


if __name__ == "__main__":
    main()
