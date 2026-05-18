import json


def parse_profile(profile_path):
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "shortName": data.get("shortName"),
        "date_of_birth": data.get("dateOfBirth"),
        "place_of_birth": data.get("placeOfBirth"),
        "height": data.get("height"),
        "preferred_foot": data.get("foot"),
        "nationality": data.get("nationality")
    }