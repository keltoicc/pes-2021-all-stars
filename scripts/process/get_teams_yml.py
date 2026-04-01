import csv
import yaml
from pathlib import Path

input_csv = Path("config/evowebid/teams_id.csv")
output_yml = Path("config/teams.yml")

teams = []

with open(input_csv, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    
    for row in reader:
        id_raw = row.get("ID:", "").strip()
        name = row.get("Team name:", "").strip()

        # Ignorar filas sin ID válido o sin nombre
        if not id_raw.isdigit() or not name:
            continue

        team = {
            "ID_pes": int(id_raw),
            "name": name,
            "source_coach": []
        }

        teams.append(team)

data = {"teams": teams}

with open(output_yml, "w", encoding="utf-8") as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True)