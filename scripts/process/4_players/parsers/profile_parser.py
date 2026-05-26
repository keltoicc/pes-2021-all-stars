import json

from mappings.positions import POSITION_MAP
from mappings.nations import NATIONS_MAP

def parse_profile(profile_path):

    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    player = data.get("data", [{}])[0]

    nationality = player.get("nationalityDetails", {})
    attributes = player.get("attributes", {})
    market_value = player.get("marketValueDetails", {})

    highest_value = market_value.get("highest", {})

    return {
        "short_name": player.get("shortName"),

        "nation_1":
            NATIONS_MAP.get(nationality.get("nationalities", {}).get("nationalityId")),

        "nation_2":
            NATIONS_MAP.get(nationality.get("nationalities", {}).get("secondNationalityId")),

        "height":
            attributes.get("height"),

        "position_group":
            attributes.get("positionGroup"),

        "position_1":
            POSITION_MAP.get(attributes.get("positionId")),

        "position_2":
            POSITION_MAP.get(attributes.get("firstSidePositionId")),

        "position_3":
            POSITION_MAP.get(attributes.get("secondSidePositionId")),

        "former_clubs":
            attributes.get("formerClubsNote"),

        "market_value":
            highest_value.get("value"),

        "prime_date":
            highest_value.get("determined")
    }