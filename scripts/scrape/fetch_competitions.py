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
        if comp["primary"] == False:
            print("Segunda División de ", comp["relegated_from"], ". No se descarga nada")
            continue
        counter = 1
        for url in comp["sources"]:
            filename = f"{comp['name']}_{comp['ranking']['type']}_{counter}.html"
            print("Descargando ", filename, "...")
            try:
                fetch(url, raw_dir / filename)
            except:
                print("TIMEOUT")
            counter += 1

if __name__ == "__main__":
    main()
