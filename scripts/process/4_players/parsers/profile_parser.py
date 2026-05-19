import json

from mappings.positions import POSITION_MAP

def parse_profile(profile_path):
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "short_name": data.get("data", [{}])[0].get("shortName"),
        "nation_1": data.get("data", [{}])[0].get("nationalityDetails").get("nationalities").get("nationalityId"),
        "nation_2": data.get("data", [{}])[0].get("nationalityDetails").get("nationalities").get("secondNationalityId"),
        "height": data.get("data", [{}])[0].get("attributes").get("height"),
        "position_group": data.get("data", [{}])[0].get("attributes").get("positionGroup"),
        "position_1": POSITION_MAP.get(data.get("data", [{}])[0].get("attributes").get("positionId")),
        "position_2": POSITION_MAP.get(data.get("data", [{}])[0].get("attributes").get("firstSidePositionId")),
        "position_3": POSITION_MAP.get(data.get("data", [{}])[0].get("attributes").get("secondSidePositionId")),
        "former_clubs": data.get("data", [{}])[0].get("attributes").get("formerClubsNote"),
        "market_value": data.get("data", [{}])[0].get("marketValueDetails").get("highest").get("value"),
        "prime_date": data.get("data", [{}])[0].get("marketValueDetails").get("highest").get("determined")
    }