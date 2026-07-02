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

import scrape.D_players.fetch_teams_players as fetch_teams_players
import process.D_players.parse_teams_players as parse_teams_players
import scrape.D_players.fetch_players_api as fetch_players_api
import process.D_players.parse_players as parse_players
import build.D_players.build_player_rankings as build_player_rankings
import build.D_players.obtain_players_per_team as obtain_players_per_team

# YML = "teams"
YML = "teams_debug"

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
        fetch_coaches.main(YML)

        print("Procesando entrenadores de cada equipo...")
        parse_coaches.main(YML)

        print("Obteniendo los entrenadores de cada equipo...")
        get_coaches.main(YML)
    
    except Exception as e:
        print(f"Error al obtener los entrenadores: {e}")

def obtain_tactics_by_coach():
    
    try:
        print("Obteniendo tácticas de cada entrenador en el equipo objetivo...")
        fetch_tactics.main(YML)

        print("Procesando tácticas de cada entrenador...")
        parse_tactics.main(YML)

        print("Obteniendo las tácticas de cada equipo...")
        get_tactics.main(YML)
    
    except Exception as e:
        print(f"Error al obtener las tácticas: {e}")

def obtain_players_by_team():
    
    try:

        print("Actualizando los datos de los jugadores...")
        fetch_players_api.main(YML)

        # Aunque el flujo lógico es obtener primero los jugadores con más partidos,
        # hacemos así para actualizar los datos de los jugadores que ya tenemos
        # por si alguno se retiró desde la última vez que se ejecutó el script.

        print("Obteniendo los jugadores con más partidos de cada equipo...")
        fetch_teams_players.main(YML)

        print("Procesando los jugadores con más partidos de cada equipo...")
        parse_teams_players.main(YML)

        # Aunque muchos jugadores serían redundantes, nos aseguramos que todos estén
        # actualizados con los datos más recientes.

        print("Obteniendo los datos de los jugadores...")
        fetch_players_api.main(YML)

        print("Procesando los datos de los jugadores...")
        parse_players.main(YML)

        print("Asignando un score a los jugadores...")
        build_player_rankings.main(YML)

        print("Seleccionando jugadores para cada equipo...")
        obtain_players_per_team.main(YML)

    except Exception as e:
        print(f"Error al obtener los jugadores: {e}")

def main():

    # obtain_teams_by_competition()

    # obtain_coaches_by_team()

    # obtain_tactics_by_coach()

    obtain_players_by_team()


if __name__ == "__main__":
    main()
