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

    stadiums_dir = Path(f"config/evowebid")
    output_dir = Path("data/published/stadiums")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stadiums_file = stadiums_dir / "stadiums.csv"
    
    if not stadiums_file.exists():
        print(f"No hay csv para países")
        return None
    
    with stadiums_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:

            name = row["Name:"]

            stadium_data = {
                "id": int(row["\ufeffID:"]),
                "name": name,
                "slug": slugify_web(name),
            }

            output_path = output_dir / f"{stadium_data['id']}-{stadium_data['slug']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    stadium_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

    publish_directory("stadiums")

if __name__ == "__main__":
    main()