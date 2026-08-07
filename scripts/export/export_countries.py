import json
from pathlib import Path
import re
import sys
import csv

from publisher import publish_directory

sys.path.append(str(Path(__file__).parent))

def slugify_web(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\.", "", name)
    name = re.sub(r"[^\w]+", "-", name)
    return name.strip("-")

def main():

    countries_dir = Path(f"config/evowebid")
    output_dir = Path("data/published/countries")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    countries_file = countries_dir / "countries.csv"
    
    if not countries_file.exists():
        print(f"No hay csv para países")
        return None
    
    with countries_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:

            name = row["English:"]

            country_data = {
                "id": int(row["Country ID:"]),
                "name": name,
                "slug": slugify_web(name),
                "code": row["SHORT_NAME:"],
            }

            output_path = output_dir / f"{country_data['id']}-{country_data['slug']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    country_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

    publish_directory("countries")

if __name__ == "__main__":
    main()