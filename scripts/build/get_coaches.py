import json
from pathlib import Path
import yaml

def get_coach(team: dict):
    processed_dir = Path("data/processed/coaches")

    json_file = processed_dir / f"{team['name']}.json"

    if not json_file.exists():
        print(f"No hay json para {team['name']}")
        return

    # Obtener los entrenadores del json
    with json_file.open(encoding="utf-8") as f:
        all_coaches = json.load(f)
    
    if len(all_coaches) == 1:
        coach = all_coaches[0]
        return

    top = all_coaches[0]
    second = all_coaches[1]

    if top["matches"] / second["matches"] >= 1.30:
        coach = top
    
    else:
        subset = all_coaches[:5]

        max_m = max(c["matches"] for c in subset)
        max_ppp = max(c["ppp"] for c in subset)

        def score(c):
            m_norm = c["matches"] / max_m
            ppp_norm = c["ppp"] / max_ppp

            base = 0.70 * m_norm + 0.30 * ppp_norm

            sample_factor = min(1, c["matches"] / 100)
            return base * (0.85 + 0.15 * sample_factor)
        
        coach = max(subset, key=score)
    
    result_dir = Path("data/built/coaches")
    result_dir.mkdir(parents=True, exist_ok=True)

    output_path = result_dir / f"{team['ID_pes']}_{team['name']}.yml"

    output = {
        "team": {
            "id": team["ID_pes"],
            "name": team["name"],
            "coach": coach["name"]
        },
    }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            output,
            f,
            allow_unicode=True,
            sort_keys=False
        )
    
    print(f"Generado {output_path.name}")


def main():
    teams = yaml.safe_load(
        Path("config/teams.yml").read_text(encoding="utf-8")
    )["teams"]

    for team in teams:
        get_coach(team)


if __name__ == "__main__":
    main()
