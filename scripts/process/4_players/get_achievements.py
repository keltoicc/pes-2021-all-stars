import json
from pathlib import Path

# Directorio donde están los JSON de jugadores
PLAYERS_DIR = Path("data/processed/players/normalized")

achievement_titles = set()

for json_file in PLAYERS_DIR.glob("*.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Leyendo {json_file}...")

        achievements = data.get("achievements", [])

        for achievement in achievements:
            title = achievement.get("title")
            if title:
                achievement_titles.add(title.strip().lower())

    except Exception as e:
        print(f"Error procesando {json_file}: {e}")

# Mostrar resultados ordenados alfabéticamente
print(f"Total de títulos diferentes: {len(achievement_titles)}\n")

for title in sorted(achievement_titles):
    print(title)

output_file = Path("config/achievement_titles.txt")

with open(output_file, "w", encoding="utf-8") as f:
    for title in sorted(achievement_titles):
        f.write(title + "\n")

print(f"Guardados {len(achievement_titles)} títulos en {output_file}")