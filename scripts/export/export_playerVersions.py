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

def get_country_id(country):

    if not country:
        return None

    if country == "Bosnia-Herzegovina":
        country = "Bosnia and Herzegovina"
    
    if country == "Czechia":
        country = "Czech Republic"
    
    if country == "United States of America" or country == "United States":
        country = "USA"
    
    if country == "South Korea" or country == "Korea, South":
        country = "Republic of Korea"
    
    if country == "North Korea" or country == "Korea, North":
        country = "Korea DPR"
    
    if country == "the Congo":
        country = "Congo"
    
    if country == "Serbia & Montenegro":
        country = "Serbia and Montenegro"

    if country == "Cape Verde":
        country = "Cabo Verde"

    if country == "Guinea-Bissau":
        country = "Guinea Bissau"

    if country == "DR Congo":
        country = "Congo DR"

    if country == "Türkiye":
        country = "Turkey"

    if country == "the Sudan":
        country = "Sudan"
    
    if country == "Cote d'Ivoire":
        country = "Côte d'Ivoire"

    if country == "The Gambia":
        country = "Gambia"
    
    countries_dir = Path(f"config/evowebid")

    countries_file = countries_dir / "countries.csv"

    if not countries_file.exists():
        # print(f"No hay csv para países")
        return 0

    with countries_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            #print(row)
            if row["English:"] == country:
                return int(row["Country ID:"])

    print(f"No se encontró el país {country} en el csv")
    return 0

def get_positions(row):
    positions = {}
    position_keys = ["GK","CB","LB","RB","DMF","CMF","LMF","RMF","AMF","LWF","RWF","SS","CF"]

    for key in position_keys:
        if int(row[key]) != 0:
            positions[key] = int(row[key])

    return positions

def get_abilities(row):
    abilities = {
        "offensiveAwareness": int(row["OffensiveAwareness"]),
        "ballControl": int(row["BallControl"]),
        "dribbling": int(row["Dribbling"]),
        "tightPossession": int(row["TightPossession"]),
        "lowPass": int(row["LowPass"]),
        "loftedPass": int(row["LoftedPass"]),
        "finishing": int(row["Finishing"]),
        "heading": int(row["Heading"]),
        "placeKicking": int(row["PlaceKicking"]),
        "curl": int(row["Curl"]),
        "speed": int(row["Speed"]),
        "acceleration": int(row["Acceleration"]),
        "kickingPower": int(row["KickingPower"]),
        "jump": int(row["Jump"]),
        "physicalContact": int(row["PhysicalContact"]),
        "balance": int(row["Balance"]),
        "stamina": int(row["Stamina"]),
        "defensiveAwareness": int(row["DefensiveAwareness"]),
        "ballWinning": int(row["BallWinning"]),
        "aggression": int(row["Aggression"]),
        "gkAwareness": int(row["GKAwareness"]),
        "gkCatching": int(row["GKCatching"]),
        "gkClearing": int(row["GKClearing"]),
        "gkReflexes": int(row["GKReflexes"]),
        "gkReach": int(row["GKReach"])
    }

    return abilities

def get_playing_skills(row):
    
    playing_skills = []
    
    playing_skills_keys = ["ScissorsFeint", "DoubleTouch", "FlipFlap", "MarseilleTurn", "Sombrero", "CrossOverTurn", "CutBehindAndTurn", "ScotchMove", "StepOnSkillcontrol", "HeadingSpecial", "LongRangeDrive", "Chipshotcontrol", "LongRangeShot", "KnuckleShot", "DippingShots", "RisingShots", "AcrobaticFinishing", "HeelTrick", "FirstTimeShot", "OneTouchPass", "ThroughPassing", "WeightedPass", "PinpointCrossing", "OutsideCurler", "Rabona", "NoLookPass", "LowLoftedPass", "GKLowPunt", "GKHighPunt", "LongThrow", "GKLongThrow", "PenaltySpecialist", "GKPenaltySaver", "Gamesmanship", "ManMarking", "TrackBack", "Interception", "AcrobaticClear", "Captaincy", "SuperSub", "FightingSpirit"]
    
    for key in playing_skills_keys:
        if int(row[key]) == 1:
            playing_skills.append(key)
    
    return playing_skills

def get_com_playing_styles(row):
    
    com_playing_styles = []
    
    com_playing_styles_keys = ["Trickster", "MazingRun", "SpeedingBullet", "IncisiveRun", "LongBallExpert", "EarlyCross", "LongRanger"]
    
    for key in com_playing_styles_keys:
        if int(row[key]) == 1:
            com_playing_styles.append(key)
    
    return com_playing_styles

def get_player_data(row):

    #print(row)

    name_slug = slugify_web(row["Name"])
    version_slug = slugify_web(row["Version"])

    playing_style = row["PlayingStyle"]
    overall = row["Overall"]

    playing_skills = get_playing_skills(row)
    com_playing_styles = get_com_playing_styles(row)

    weight = row["Weight"]
    marketValue = row["MarketValue"]
    reputation = row["Reputation"]
    boots = row["Boots"]
    gloves = row["Gloves"]
    shirtName = row["Shirt"]
    nationalShirtName = row["ShirtNational"]

    player_version_data = {}

    player_version_data["id"] = int(row["\ufeffId"])
    player_version_data["player"] = int(row["PlayerId"])
    player_version_data["slug"] = f"{name_slug}-{version_slug}"
    player_version_data["country"] = get_country_id(row["Country"])
    player_version_data["version"] = row["Version"]
    player_version_data["fromSeason"] = row["FromSeason"]
    player_version_data["toSeason"] = row["ToSeason"]

    if playing_style:
        player_version_data["playingStyle"] = playing_style

    player_version_data["mainPosition"] = row["POS"]
    player_version_data["positions"] = get_positions(row)

    if overall:
        player_version_data["overall"] = int(overall)

    player_version_data["abilities"] = get_abilities(row)
    player_version_data["weakFootUsage"] = int(row["WeakFootUsage"])
    player_version_data["weakFootAccuracy"] = int(row["WeakFootAcc"])
    player_version_data["form"] = int(row["Form"])
    player_version_data["injuryResistance"] = int(row["InjuryResistance"])

    if playing_skills:
        player_version_data["playingSkills"] = playing_skills

    if com_playing_styles:
        player_version_data["comPlayingStyles"] = com_playing_styles

    if weight:
        player_version_data["weight"] = int(weight)

    if marketValue:
        player_version_data["marketValue"] = int(marketValue)

    if reputation:
        player_version_data["reputation"] = int(reputation)

    if boots:
        player_version_data["boots"] = boots

    if gloves:
        player_version_data["gloves"] = gloves

    if shirtName:
        player_version_data["shirtName"] = shirtName

    if nationalShirtName:
        player_version_data["nationalShirtName"] = nationalShirtName

    return player_version_data

def main():

    players_dir = Path(f"config")
    output_dir = Path("data/published/playerVersions")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    players_file = players_dir / "PlayerAppearances.csv"
    
    if not players_file.exists():
        print(f"No hay csv con los jugadores")
        return None
    
    with players_file.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:

            if not row["Add"]:
                continue

            player_version_data = get_player_data(row)

            output_path = output_dir / f"{player_version_data['id']}-{player_version_data['slug']}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    player_version_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

    publish_directory("playerVersions")

if __name__ == "__main__":
    main()