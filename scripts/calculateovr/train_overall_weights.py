from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error


# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = (
    PROJECT_ROOT
    / "config"
    / "calculateovr"
    / "pes2021-all-players.csv"
)


# Columns
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


def load_data():
    """Load and validate the player data."""

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        POSITION_COLUMN,
        TARGET_COLUMN,
        *ABILITY_COLUMNS,
        WEAK_FOOT_COLUMN,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in CSV: {', '.join(missing_columns)}"
        )

    return df


def prepare_data(df):
    """Prepare the data used by the regression models."""

    columns = [
        POSITION_COLUMN,
        TARGET_COLUMN,
        *ABILITY_COLUMNS,
        WEAK_FOOT_COLUMN,
    ]

    data = df[columns].copy()

    # Convert numeric columns to numeric values.
    numeric_columns = [
        TARGET_COLUMN,
        *ABILITY_COLUMNS,
        WEAK_FOOT_COLUMN,
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    # Remove rows with missing values.
    data = data.dropna(subset=columns)

    return data


def analyze_weak_foot_residuals(data, position):
    """Analyze residuals by weak foot and average ability."""

    position_data = data[
        data[POSITION_COLUMN] == position
    ].copy()

    x = position_data[ABILITY_COLUMNS].copy()
    y = position_data[TARGET_COLUMN]

    # Keep the original ability values for analysis.
    average_ability = x.mean(axis=1)

    # PES-style transformation for abilities.
    x = x - 25

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=42,
    )

    model = LinearRegression(
        fit_intercept=True,
        positive=True,
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    residuals = y_test - predictions

    # Align the additional data with the test players.
    test_average_ability = average_ability.loc[
        x_test.index
    ]

    weak_foot = position_data.loc[
        x_test.index,
        WEAK_FOOT_COLUMN,
    ]

    print(f"\n{position}:")

    print("  Residuals by weak foot:")

    for value in sorted(weak_foot.unique()):
        group_residuals = residuals[
            weak_foot == value
        ]

        print(
            f"    Weak foot {int(value)}: "
            f"players = {len(group_residuals)}, "
            f"mean residual = {group_residuals.mean():+.3f}"
        )

    # Divide players into five groups by average ability.
    ability_groups = pd.qcut(
        test_average_ability,
        q=5,
        duplicates="drop",
    )

    print("  Residuals by average ability:")

    for group in ability_groups.cat.categories:
        mask = ability_groups == group
        group_residuals = residuals[mask]

        print(
            f"    {group}: "
            f"players = {len(group_residuals)}, "
            f"mean residual = {group_residuals.mean():+.3f}"
        )


def train_position_model(data, position):
    """Train a model for one registered position."""

    position_data = data[
        data[POSITION_COLUMN] == position
    ].copy()

    if len(position_data) < 10:
        print(
            f"\nSkipping {position}: "
            f"only {len(position_data)} players."
        )
        return

    x = position_data[
        [*ABILITY_COLUMNS, WEAK_FOOT_COLUMN]
    ].copy()

    y = position_data[TARGET_COLUMN]

    # PES-style transformation for abilities only.
    # Weak Foot remains on its original 1–4 scale.
    x[ABILITY_COLUMNS] = (
        x[ABILITY_COLUMNS] - 25
    )

    kfold = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    fold_mae = []
    fold_exact_matches = []
    fold_within_one = []
    fold_weak_foot_weights = []

    for train_index, test_index in kfold.split(x):

        x_train = x.iloc[train_index]
        x_test = x.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        model = LinearRegression(
            fit_intercept=True,
            positive=True,
        )

        model.fit(x_train, y_train)

        # Get the Weak Foot coefficient for this fold.
        weak_foot_weight = model.coef_[
            list(x.columns).index(WEAK_FOOT_COLUMN)
        ]

        fold_weak_foot_weights.append(
            weak_foot_weight
        )

        predictions = model.predict(x_test)

        rounded_predictions = predictions.round()

        mae = mean_absolute_error(
            y_test,
            rounded_predictions,
        )

        exact_matches = (
            rounded_predictions == y_test
        ).mean() * 100

        within_one = (
            abs(rounded_predictions - y_test) <= 1
        ).mean() * 100

        fold_mae.append(mae)
        fold_exact_matches.append(exact_matches)
        fold_within_one.append(within_one)

    # ---------------------------------------------------------
    # Final model using all players in this position.
    # ---------------------------------------------------------

    final_model = LinearRegression(
        fit_intercept=True,
        positive=True,
    )

    final_model.fit(x, y)

    final_weights = pd.Series(
        final_model.coef_,
        index=x.columns,
    )

    # Calculate the Ability Score using abilities only.
    #
    # Ability Score =
    #     SUM((ability - 25) * weight) / 100
    ability_score = (
        x[ABILITY_COLUMNS]
        .mul(
            final_weights[ABILITY_COLUMNS],
            axis=1,
        )
        .sum(axis=1)
        / 100
    )

    print()
    print("=" * 70)
    print(f"POSITION: {position}")
    print("=" * 70)

    print(f"Players: {len(position_data)}")

    print()
    print("5-Fold Cross-Validation:")

    print(
        f"  MAE:            "
        f"{sum(fold_mae) / len(fold_mae):.3f}"
    )

    print(
        f"  Exact matches:  "
        f"{sum(fold_exact_matches) / len(fold_exact_matches):.1f}%"
    )

    print(
        f"  Within ±1:      "
        f"{sum(fold_within_one) / len(fold_within_one):.1f}%"
    )

    print()
    print("Weak Foot weight:")

    for fold, weight in enumerate(
        fold_weak_foot_weights,
        start=1,
    ):
        print(
            f"  Fold {fold}: {weight:.6f}"
        )

    weak_foot_weight = (
        sum(fold_weak_foot_weights)
        / len(fold_weak_foot_weights)
    )

    print(
        f"  Mean:    {weak_foot_weight:.6f}"
    )

    print()
    print("Weak Foot linearity:")

    for level in [1, 2, 3, 4]:
        expected_effect = (
            (level - 1) * weak_foot_weight
        )

        print(
            f"  Weak foot {level}: "
            f"expected effect = {expected_effect:+.6f}"
        )

    print()
    print("Final Ability Weights:")

    for ability in ABILITY_COLUMNS:
        weight = final_weights[ability]

        if weight > 0:
            print(
                f"  {ability}: {weight:.6f}"
            )

    print()
    print("Ability Score:")

    print(
        f"  Minimum: {ability_score.min():.3f}"
    )

    print(
        f"  Maximum: {ability_score.max():.3f}"
    )

    print(
        f"  Mean:    {ability_score.mean():.3f}"
    )

    print()
    print("Ability Score vs Overall:")

    analysis = pd.DataFrame({
        "ability_score": ability_score,
        "overall": y,
    })

    analysis["score_group"] = pd.cut(
        analysis["ability_score"],
        bins=20,
    )

    grouped = (
        analysis
        .groupby("score_group", observed=True)
        .agg(
            players=("overall", "count"),
            average_score=("ability_score", "mean"),
            average_overall=("overall", "mean"),
            minimum_overall=("overall", "min"),
            maximum_overall=("overall", "max"),
        )
    )

    print(
        grouped.to_string()
    )


def main():
    print(f"Loading data from:\n{CSV_PATH}")

    df = load_data()

    print(f"Rows loaded: {len(df)}")

    data = prepare_data(df)

    print(f"Rows after cleaning: {len(data)}")

    positions = sorted(
        data[POSITION_COLUMN].unique()
    )

    print()
    print("Positions found:")
    print(", ".join(positions))

    for position in positions:
        analyze_weak_foot_residuals(
            data,
            position,
        )

        train_position_model(
            data,
            position,
        )


if __name__ == "__main__":
    main()