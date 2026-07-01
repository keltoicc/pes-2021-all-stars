from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

import scrape.A_teams.fetch_competitions as fetch_competitions
import process.A_teams.parse_competitions as parse_competitions

def main():
    
    print("Obteniendo clasificaciones de competiciones...")
    fetch_competitions.main()

    print("Generando la clasificación histórica de las competiciones...")
    parse_competitions.main()


if __name__ == "__main__":
    main()
