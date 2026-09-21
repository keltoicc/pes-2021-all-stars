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

def get_first_line(value):
    if not value:
        return ""
    return value.splitlines()[0].strip()

def main():

    managers_dir = Path(f"config/evowebid")
    output_dir = Path("data/published/managers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    managers_file = managers_dir / "managers.csv"
    
    if not managers_file.exists():
        print(f"No hay csv para entrenadores")
        return None
    
    with managers_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:

            name = get_first_line(row["Real name in-game:"])
            if not name:
                name = get_first_line(row["Proposed in-game name:"])

            manager_data = {
                "id": int(row["Base ID:"]),
                "name": name,
                "slug": slugify_web(name)
            }

            output_path = output_dir / f"{manager_data['id']}-{manager_data['slug']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    manager_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

    publish_directory("managers")

if __name__ == "__main__":
    main()