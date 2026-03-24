from bs4 import BeautifulSoup
import json
from pathlib import Path
import yaml
import re

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w]+", "_", name)
    return name.strip("_")

def merge_coaches(rows: list[dict]) -> dict:    
    merged = {}

    for row in rows:
        coach = row["name"]

        if coach not in merged:
            merged[coach] = {
                "name": coach,
                "matches": 0,
                "points": 0,
                "ppp": 0,
            }

        merged[coach]["matches"] += row["matches"]
        merged[coach]["points"] += int(row["ppp"] * row["matches"])
        merged[coach]["ppp"] = round(merged[coach]["points"] / merged[coach]["matches"], 2) if merged[coach]["matches"] > 0 else 0

    return merged

def parse_table(html_path: Path) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table.items tbody tr")

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 10:
            continue
        
        name = cols[2].get_text(strip=True)
        matches = int(cols[8].get_text(strip=True).replace(".", ""))
        if matches == 0:
            ppp = 0.0
        else:
            ppp = float(cols[9].get_text(strip=True).replace(",", "."))

        data.append({
            "name": name,
            "matches": matches,
            "ppp": ppp,
        })

    return data

def obtain_coach(team: dict):
    raw_dir = Path("data/raw/transfermarkt/teams")

    html_file = raw_dir / f"{slugify(team['name'])}_coaches.html"

    if not html_file.exists():
        print(f"No hay HTML para {team['name']}")
        return

    all_rows = []

    rows = parse_table(html_file)
    all_rows.extend(rows)

    merged = merge_coaches(all_rows)

    # Convertimos a lista y ordenamos por puntos, partidos, victorias y diferencia de goles
    all_coaches = sorted(
        merged.values(),
        key=lambda x: (
            x["matches"],
            x["ppp"],
        ),
    reverse=True
    )

    top = all_coaches[0]
    second = all_coaches[1]

    if top["matches"] / second["matches"] >= 1.30:
        return top
    
    subset = all_coaches[:5]

    max_m = max(c["matches"] for c in subset)
    max_ppp = max(c["ppp"] for c in subset)

    def score(c):
        m_norm = c["matches"] / max_m
        ppp_norm = c["ppp"] / max_ppp

        base = 0.70 * m_norm + 0.30 * ppp_norm

        sample_factor = min(1, c["matches"] / 100)
        return base * (0.85 + 0.15 * sample_factor)

    return max(subset, key=score)

def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    for team in teams:
        print(team["name"])
        coach = obtain_coach(team)
        team["coach"] = coach["name"] # type: ignore

if __name__ == "__main__":
    main()
