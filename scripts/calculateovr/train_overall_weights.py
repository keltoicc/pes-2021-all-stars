
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error


# ======================================================
# PATHS
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "config"
    / "calculateovr"
    / "pes2021-all-players.csv"
)


# ======================================================
# COLUMNS
# ======================================================

POSITION_COLUMN = "registered_position"
TARGET_COLUMN = "overall_rating"
WEAK_FOOT_COLUMN = "weak_foot_accuracy"

ABILITY_COLUMNS = [
    "offensive_awareness",
    "ball_control",
    "dribbling",
    "tight_possession",
    "low_pass",
    "lofted_pass",
    "finishing",
    "heading",
    "place_kicking",
    "curl",
    "speed",
    "acceleration",
    "kicking_power",
    "jump",
    "physical_contact",
    "balance",
    "stamina",
    "defensive_awareness",
    "ball_winning",
    "aggression",
    "gk_awareness",
    "gk_catching",
    "gk_clearing",
    "gk_reflexes",
    "gk_reach",
]


# ======================================================
# POSITION-SPECIFIC WEIGHTS
#
# Weak Foot Accuracy is handled separately with
# baseline 1 instead of 25.
#
# Goalkeepers use two composite attributes:
#   GK Awareness = (GK Awareness + GK Reach) // 2
#   GK Reflexes  = (GK Catching + GK Clearing
#                   + GK Reflexes) // 3
# ======================================================

POSITION_WEIGHTS = {
    "GK": {
        "jump": 11,
        "physical_contact": 11,
        "gk_awareness_composite": 50,
        "gk_reflexes_composite": 48,
    },
    "CB": {
        "heading": 22,
        "speed": 10,
        "jump": 19,
        "physical_contact": 19,
        "stamina": 9,
        "defensive_awareness": 25,
        "ball_winning": 17,
        "aggression": 8,
        WEAK_FOOT_COLUMN: 23,
    },
    "LB": {
        "offensive_awareness": 6,
        "ball_control": 9,
        "dribbling": 9,
        "tight_possession": 5,
        "lofted_pass": 14,
        "speed": 16,
        "acceleration": 14,
        "jump": 11,
        "physical_contact": 8,
        "balance": 4,
        "stamina": 14,
        "defensive_awareness": 14,
        "ball_winning": 8,
        "aggression": 5,
        WEAK_FOOT_COLUMN: 56,
    },
    "RB": {
        "offensive_awareness": 6,
        "ball_control": 9,
        "dribbling": 9,
        "tight_possession": 5,
        "lofted_pass": 14,
        "speed": 16,
        "acceleration": 14,
        "jump": 11,
        "physical_contact": 8,
        "balance": 4,
        "stamina": 14,
        "defensive_awareness": 14,
        "ball_winning": 8,
        "aggression": 5,
        WEAK_FOOT_COLUMN: 56,
    },
    "DMF": {
        "offensive_awareness": 7,
        "ball_control": 18,
        "dribbling": 10,
        "tight_possession": 5,
        "low_pass": 18,
        "lofted_pass": 19,
        "curl": 12,
        "speed": 3,
        "acceleration": 3,
        "jump": 5,
        "physical_contact": 9,
        "balance": 4,
        "stamina": 14,
        "defensive_awareness": 7,
        "ball_winning": 3,
        "aggression": 1,
        WEAK_FOOT_COLUMN: 23,
    },
    "CMF": {
        "offensive_awareness": 5,
        "ball_control": 23,
        "dribbling": 16,
        "tight_possession": 8,
        "low_pass": 23,
        "lofted_pass": 21,
        "speed": 4,
        "acceleration": 6,
        "physical_contact": 3,
        "balance": 2,
        "stamina": 17,
        "defensive_awareness": 3,
        WEAK_FOOT_COLUMN: 23,
    },
    "LMF": {
        "offensive_awareness": 7,
        "ball_control": 15,
        "dribbling": 17,
        "tight_possession": 8,
        "low_pass": 7,
        "lofted_pass": 12,
        "curl": 4,
        "speed": 24,
        "acceleration": 21,
        "stamina": 13,
        WEAK_FOOT_COLUMN: 56,
    },
    "RMF": {
        "offensive_awareness": 7,
        "ball_control": 15,
        "dribbling": 17,
        "tight_possession": 8,
        "low_pass": 7,
        "lofted_pass": 12,
        "curl": 4,
        "speed": 24,
        "acceleration": 21,
        "stamina": 13,
        WEAK_FOOT_COLUMN: 56,
    },
    "AMF": {
        "offensive_awareness": 14,
        "ball_control": 23,
        "dribbling": 17,
        "tight_possession": 7,
        "low_pass": 21,
        "lofted_pass": 14,
        "finishing": 17,
        "speed": 5,
        "acceleration": 7,
        "physical_contact": 2,
        "balance": 3,
        "stamina": 3,
        WEAK_FOOT_COLUMN: 37,
    },
    "LWF": {
        "offensive_awareness": 17,
        "ball_control": 19,
        "dribbling": 15,
        "tight_possession": 7,
        "low_pass": 5,
        "lofted_pass": 9,
        "finishing": 11,
        "speed": 15,
        "acceleration": 15,
        "kicking_power": 5,
        "physical_contact": 2,
        "balance": 4,
        "stamina": 6,
        WEAK_FOOT_COLUMN: 47,
    },
    "RWF": {
        "offensive_awareness": 17,
        "ball_control": 19,
        "dribbling": 15,
        "tight_possession": 7,
        "low_pass": 5,
        "lofted_pass": 9,
        "finishing": 11,
        "speed": 15,
        "acceleration": 15,
        "kicking_power": 5,
        "physical_contact": 2,
        "balance": 4,
        "stamina": 6,
        WEAK_FOOT_COLUMN: 47,
    },
    "SS": {
        "offensive_awareness": 15,
        "ball_control": 19,
        "dribbling": 13,
        "tight_possession": 6,
        "low_pass": 9,
        "lofted_pass": 9,
        "finishing": 14,
        "speed": 9,
        "acceleration": 21,
        "kicking_power": 6,
        "physical_contact": 2,
        "balance": 5,
        "stamina": 4,
        WEAK_FOOT_COLUMN: 37,
    },
    "CF": {
        "offensive_awareness": 31,
        "ball_control": 23,
        "dribbling": 9,
        "tight_possession": 5,
        "finishing": 36,
        "heading": 3,
        "speed": 5,
        "acceleration": 5,
        "kicking_power": 3,
        "jump": 3,
        "physical_contact": 8,
        "balance": 2,
        WEAK_FOOT_COLUMN: 38,
    },
}


# ======================================================
# POSITION BONUSES
# ======================================================

POSITION_BONUSES = {
    "GK": 8,
    "CB": 8,
    "LB": 9,
    "RB": 9,
    "DMF": 9,
    "CMF": 8,
    "LMF": 8,
    "RMF": 8,
    "AMF": 8,
    "LWF": 10,
    "RWF": 10,
    "SS": 9,
    "CF": 8,
}


# ======================================================
# DATA LOADING
# ======================================================

def load_data():
    """Load and validate the player dataset."""

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        POSITION_COLUMN,
        TARGET_COLUMN,
        *ABILITY_COLUMNS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in CSV: "
            + ", ".join(missing_columns)
        )

    return df


def prepare_data(df):
    """Convert numeric columns and remove incomplete rows."""

    data = df.copy()

    numeric_columns = [
        TARGET_COLUMN,
        *ABILITY_COLUMNS,
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    # Retain only rows with all fields required by the formula.
    data = data.dropna(
        subset=[
            POSITION_COLUMN,
            TARGET_COLUMN,
            *ABILITY_COLUMNS,
        ]
    ).copy()

    # The formula expects integer-valued game attributes.
    non_integer_columns = [
        column
        for column in numeric_columns
        if not (data[column] % 1 == 0).all()
    ]

    if non_integer_columns:
        raise ValueError(
            "Expected integer values in: "
            + ", ".join(non_integer_columns)
        )

    for column in numeric_columns:
        data[column] = data[column].astype("int64")

    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype("int64")

    return data


# ======================================================
# INTEGER ATTRIBUTE HELPERS
# ======================================================

def get_gk_awareness_composite(player):
    """Average GK Awareness and GK Reach using integer division."""

    return (
        int(player["gk_awareness"])
        + int(player["gk_reach"])
    ) // 2


def get_gk_reflexes_composite(player):
    """Average GK Catching, GK Clearing and GK Reflexes."""

    return (
        int(player["gk_catching"])
        + int(player["gk_clearing"])
        + int(player["gk_reflexes"])
    ) // 3


def get_attribute_value(player, attribute):
    """Return a normal or composite attribute value."""

    if attribute == "gk_awareness_composite":
        return get_gk_awareness_composite(player)

    if attribute == "gk_reflexes_composite":
        return get_gk_reflexes_composite(player)

    return int(player[attribute])


# ======================================================
# WEIGHTED AVERAGE
# ======================================================

def calculate_weighted_average(player, position):
    """
    Calculate the position-specific weighted average.

    Normal abilities use baseline 25.
    Weak Foot Accuracy uses baseline 1.

    Round the positive weighted sum to the nearest integer
    using integer arithmetic.
    """

    weighted_sum = 0

    for attribute, weight in POSITION_WEIGHTS[position].items():

        value = get_attribute_value(player, attribute)

        baseline = 1 if attribute == WEAK_FOOT_COLUMN else 25

        weighted_sum += (value - baseline) * weight

    return (weighted_sum + 50) // 100


# ======================================================
# SUM AVERAGE AND CURVE
# ======================================================

def calculate_sum_average(player):
    """
    Calculate the mean of 22 contributors:

    - 20 outfield abilities
    - 2 goalkeeper composites

    Weak Foot Accuracy is excluded.
    """

    outfield_abilities = [
        "offensive_awareness",
        "ball_control",
        "dribbling",
        "tight_possession",
        "low_pass",
        "lofted_pass",
        "finishing",
        "heading",
        "place_kicking",
        "curl",
        "speed",
        "acceleration",
        "kicking_power",
        "jump",
        "physical_contact",
        "balance",
        "stamina",
        "defensive_awareness",
        "ball_winning",
        "aggression",
    ]

    contributor_sum = sum(
        int(player[attribute])
        for attribute in outfield_abilities
    )

    contributor_sum += get_gk_awareness_composite(player)
    contributor_sum += get_gk_reflexes_composite(player)

    # Follow the supplied implementation's integer operations:
    # first scale by 100 and divide by 22, then round.
    scaled_average = contributor_sum * 100 // 22

    return (scaled_average + 50) // 100


def map_rating(sum_average):
    """Apply the supplied non-linear curve."""

    if sum_average <= 61:
        return sum_average - 9

    if sum_average == 62:
        return sum_average - 6

    if sum_average == 63:
        return sum_average - 4

    if sum_average == 64:
        return sum_average - 2

    if sum_average == 65:
        return sum_average

    if sum_average == 66:
        return sum_average + 1

    if sum_average == 67:
        return sum_average + 3

    if sum_average == 68:
        return sum_average + 5

    if sum_average == 69:
        return sum_average + 6

    if sum_average == 70:
        return sum_average + 7

    if sum_average == 71:
        return sum_average + 8

    if sum_average <= 73:
        return sum_average + 10

    if sum_average <= 75:
        return sum_average + 12

    if sum_average <= 77:
        return sum_average + 13

    return sum_average + 14


# ======================================================
# FINAL OVERALL
# ======================================================

def calculate_overall(player):
    """Calculate the registered-position Overall."""

    position = player[POSITION_COLUMN]

    if position not in POSITION_WEIGHTS:
        raise ValueError(
            f"Unsupported registered position: {position}"
        )

    # Step 1: weighted average.
    base = calculate_weighted_average(
        player,
        position,
    )

    # Goalkeepers skip the curved blend.
    if position == "GK":
        final_rating = base + POSITION_BONUSES["GK"]

    else:
        # Step 2: registered-position bonus.
        base += POSITION_BONUSES[position]

        # Step 3: calculate and map the sum average.
        sum_average = calculate_sum_average(player)
        curved = map_rating(sum_average)

        # Step 4: 60/40 blend with integer rounding.
        final_rating = (
            base * 60
            + curved * 40
            + 50
        ) // 100

    # Minimum Overall is 40.
    return max(40, final_rating)


# ======================================================
# VALIDATION
# ======================================================

def print_metrics(name, actual, calculated):
    """Print comparison metrics for a subset of players."""

    errors = calculated - actual
    absolute_errors = errors.abs()

    mae = mean_absolute_error(
        actual,
        calculated,
    )

    exact_matches = (
        errors == 0
    ).mean() * 100

    within_one = (
        absolute_errors <= 1
    ).mean() * 100

    print()
    print(name)
    print(f"  Players:          {len(actual)}")
    print(f"  MAE:              {mae:.4f}")
    print(f"  Exact matches:    {exact_matches:.2f}%")
    print(f"  Within ±1:        {within_one:.2f}%")
    print(f"  Mean error:       {errors.mean():+.4f}")
    print(f"  Maximum error:    {absolute_errors.max()}")
    print(f"  Maximum over:     {errors.max():+}")
    print(f"  Maximum under:    {errors.min():+}")


def validate_formula(data):
    """Calculate the formula for every player and compare it with the CSV."""

    data = data.copy()

    supported_positions = set(POSITION_WEIGHTS)
    found_positions = set(data[POSITION_COLUMN].unique())

    unsupported_positions = sorted(
        found_positions - supported_positions
    )

    if unsupported_positions:
        raise ValueError(
            "Positions without configured weights: "
            + ", ".join(unsupported_positions)
        )

    data["calculated_overall"] = data.apply(
        calculate_overall,
        axis=1,
    )

    data["overall_error"] = (
        data["calculated_overall"]
        - data[TARGET_COLUMN]
    )

    print()
    print("=" * 70)
    print("KONAMI OVERALL FORMULA VALIDATION")
    print("=" * 70)

    print(f"Players tested: {len(data)}")

    print_metrics(
        "ALL PLAYERS",
        data[TARGET_COLUMN],
        data["calculated_overall"],
    )

    print()
    print("=" * 70)
    print("RESULTS BY POSITION")
    print("=" * 70)

    for position in sorted(found_positions):

        position_data = data[
            data[POSITION_COLUMN] == position
        ]

        print_metrics(
            f"POSITION: {position}",
            position_data[TARGET_COLUMN],
            position_data["calculated_overall"],
        )

    # Show a sample of mismatches to help investigate
    # potential discrepancies in the formula.
    mismatches = data[
        data["overall_error"] != 0
    ].copy()

    mismatches["absolute_error"] = (
        mismatches["overall_error"].abs()
    )

    mismatches = mismatches.sort_values(
        "absolute_error",
        ascending=False,
    )

    print()
    print("=" * 70)
    print("LARGEST MISMATCHES")
    print("=" * 70)

    if mismatches.empty:
        print("All calculated Overalls match the CSV exactly.")

    else:
        display_columns = [
            POSITION_COLUMN,
            TARGET_COLUMN,
            "calculated_overall",
            "overall_error",
        ]

        # Preserve any identifying columns available in the CSV.
        for candidate in ["player_id", "player_name", "name"]:
            if candidate in data.columns:
                display_columns.insert(
                    0,
                    candidate,
                )

        print(
            mismatches[display_columns]
            .head(30)
            .to_string(index=False)
        )

    # Save all comparisons beside the source CSV.
    output_path = (
        PROJECT_ROOT
        / "config"
        / "calculateovr"
        / "overall_validation_results.csv"
    )

    data.to_csv(
        output_path,
        index=False,
    )

    print()
    print(f"Full results saved to:\n{output_path}")


# ======================================================
# MAIN
# ======================================================

def main():
    print(f"Loading data from:\n{CSV_PATH}")

    df = load_data()

    print(f"Rows loaded: {len(df)}")

    data = prepare_data(df)

    print(f"Rows after cleaning: {len(data)}")

    validate_formula(data)


if __name__ == "__main__":
    main()
