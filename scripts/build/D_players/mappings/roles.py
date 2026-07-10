from collections import defaultdict

TACTICAL_ROLES = [
    "GOALKEEPER",

    "CENTER_BACK",
    "SWEEPER",
    "WIDE_CENTER_BACK",
    "FULLBACK",
    "WING_BACK",

    "DEFENSIVE_MID",
    "CENTRAL_MID",
    "ATTACKING_MID",

    "WIDE_MID",
    "WINGER",

    "SECOND_STRIKER",
    "STRIKER"
]

GROUP_TO_ROLES = {
    "GOALKEEPER": {
        "GOALKEEPER": 1.0
    },

    "DEFENDER": {
        "CENTER_BACK": 0.3,
        "WIDE_CENTER_BACK": 0.25,
        "FULLBACK": 0.2,
        "WING_BACK": 0.15,
        "SWEEPER": 0.1,
    },

    "MIDFIELDER": {
        "CENTRAL_MID": 0.4,
        "DEFENSIVE_MID": 0.25,
        "ATTACKING_MID": 0.2,
        "WIDE_MID": 0.1,
        "WINGER": 0.05
    },

    "FORWARD": {
        "STRIKER": 0.55,
        "SECOND_STRIKER": 0.25,
        "WINGER": 0.2
    }
}

ROLE_MAP = {
    "GOALKEEPER": {
        "GK": 1.0
    },

    "CENTER_BACK": {
        "CB": 1.0,
        "SW": 0.8
    },

    "SWEEPER": {
        "SW": 1.0,
        "CB": 0.5
    },

    "WIDE_CENTER_BACK": {
        "CB": 1.0,
        "LB": 0.8,
        "RB": 0.8,
        "SW": 0.7,
    },
    
    "FULLBACK": {
        "LB": 1.0,
        "RB": 1.0
    },

    "WING_BACK": {
        "LB": 0.7,
        "RB": 0.7,
        "LM": 0.4,
        "RM": 0.4
    },

    "DEFENSIVE_MID": {
        "DMF": 1.0,
        "CMF": 0.6
    },

    "CENTRAL_MID": {
        "CMF": 1.0,
        "AMF": 0.7,
        "DMF": 0.5
    },

    "ATTACKING_MID": {
        "AMF": 1.0,
        "SS": 0.6,
        "CMF": 0.4
    },

    "WIDE_MID": {
        "LM": 1.0,
        "RM": 1.0,
        "LW": 0.6,
        "RW": 0.6
    },

    "WINGER": {
        "LW": 1.0,
        "RW": 1.0,
        "LM": 0.7,
        "RM": 0.7,
    },

    "SECOND_STRIKER": {
        "SS": 1.0,
        "AMF": 0.6,
        "CF": 0.4
    },

    "STRIKER": {
        "CF": 1.0,
        "SS": 0.5
    }
}

POSITION_TO_ROLES = defaultdict(dict)

for role, positions in ROLE_MAP.items():
    for position, weight in positions.items():
        POSITION_TO_ROLES[position][role] = weight

POSITION_TO_ROLES = dict(POSITION_TO_ROLES)