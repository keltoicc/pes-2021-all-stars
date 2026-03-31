import requests
from pathlib import Path
import yaml
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def fetch(url: str, output_path: Path):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    output_path.write_text(r.text, encoding="utf-8")

def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    raw_dir = Path("data/raw/transfermarkt/teams")
    raw_dir.mkdir(parents=True, exist_ok=True)

    for team in teams:
        for url in team["source_coach"]:
            filename = f"{slugify(team['name'])}_coaches.html"
            print("Descargando ", filename, "...")
            try:
                fetch(url, raw_dir / filename)
            except:
                print("TIMEOUT")

if __name__ == "__main__":
    main()
