import requests
from pathlib import Path
import yaml

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch(url: str, output_path: Path):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    output_path.write_text(r.text, encoding="utf-8")

def main():
    competitions = yaml.safe_load(
        Path("config/competitions.yml").read_text(encoding="utf-8")
    )["competitions"]

    raw_dir = Path("data/raw/transfermarkt")
    raw_dir.mkdir(parents=True, exist_ok=True)

    for comp in competitions:
        for url in comp["sources"]:
            filename = f"{comp['name']}_{url.split('/')[-1]}.html"
            print("Descargando ", filename, "...")
            fetch(url, raw_dir / filename)

if __name__ == "__main__":
    main()
