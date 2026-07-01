from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

import scrape.A_teams.fetch_competitions as fetch_competitions
import process.A_teams.parse_competitions as parse_competitions
import build.A_teams.get_teams as get_teams

import scrape.B_coaches.fetch_coaches as fetch_coaches
import process.B_coaches.parse_coaches as parse_coaches
import build.B_coaches.get_coaches as get_coaches

import scrape.C_tactics.fetch_tactics as fetch_tactics
import process.C_tactics.parse_tactics as parse_tactics
import build.C_tactics.get_tactics as get_tactics

def obtain_teams_by_competition():

    try:
        print("Obteniendo clasificaciones de competiciones...")
        fetch_competitions.main()

        print("Generando la clasificación histórica de las competiciones...")
        parse_competitions.main()

        print("Obteniendo los equipos de cada competición...")
        get_teams.main()

    except Exception as e:
        print(f"Error al obtener los equipos por competición: {e}")

def obtain_coaches_by_team():
    
    try:
        print("Obteniendo entrenadores de cada equipo...")
        fetch_coaches.main()

        print("Procesando entrenadores de cada equipo...")
        parse_coaches.main()

        print("Obteniendo los entrenadores de cada equipo...")
        get_coaches.main()
    
    except Exception as e:
        print(f"Error al obtener los entrenadores: {e}")

def obtain_tactics_by_coach():
    
    try:
        print("Obteniendo tácticas de cada entrenador en el equipo objetivo...")
        fetch_tactics.main()

        print("Procesando tácticas de cada entrenador...")
        parse_tactics.main()

        print("Obteniendo las tácticas de cada equipo...")
        get_tactics.main()
    
    except Exception as e:
        print(f"Error al obtener las tácticas: {e}")

def main():
    
    # obtain_teams_by_competition()

    # obtain_coaches_by_team()

    obtain_tactics_by_coach()


if __name__ == "__main__":
    main()
