from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
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


# Positions considered outfield players.
OUTFIELD_POSITIONS = [
    "AMF",
    "CB",
    "CF",
    "CMF",
    "DMF",
    "LB",
    "LMF",
    "LWF",
    "RB",
    "RMF",
    "RWF",
    "SS",
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

    data = data.dropna(subset=columns)

    return data


def calculate_common_intercepts(data):
    print("\nPosition-specific intercepts:")

    intercepts = {}

    for position in data[POSITION_COLUMN].unique():
        position_data = data[data[POSITION_COLUMN] == position]

        x = position_data[ABILITY_COLUMNS].copy() - 25
        y = position_data[TARGET_COLUMN]

        model = LinearRegression(
            fit_intercept=True,
            positive=True,
        )

        model.fit(x, y)

        intercepts[position] = model.intercept_

        print(f"  {position}: {model.intercept_:+.6f}")

    print("\nSimplified intercepts:")
    print("  Outfield: -8")
    print("  GK:       +8")

    return -8, 8


def train_position_model(
    data,
    position,
    common_outfield_intercept,
    common_gk_intercept,
):
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
        ABILITY_COLUMNS
    ].copy()

    y = position_data[TARGET_COLUMN]

    # PES-style transformation for abilities only.
    # Weak Foot remains on its original 1–4 scale.
    x[ABILITY_COLUMNS] = (
        x[ABILITY_COLUMNS] - 25
    )

    # Cross-validation.
    kfold = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    # Metrics for the original linear model.
    fold_mae = []
    fold_exact_matches = []
    fold_within_one = []

    # Metrics for the model with quadratic correction.
    fold_quadratic_mae = []
    fold_quadratic_exact_matches = []
    fold_quadratic_within_one = []

    for train_index, test_index in kfold.split(x):

        x_train = x.iloc[train_index]
        x_test = x.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        # --------------------------------------------------
        # Model A: original linear model
        # --------------------------------------------------

        model = LinearRegression(
            fit_intercept=True,
            positive=True,
        )

        model.fit(x_train, y_train)

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

        # --------------------------------------------------
        # Model B: linear model + quadratic correction
        # --------------------------------------------------

        # Calculate the Ability Score using only the
        # ability coefficients learned in this fold.
        ability_weights = pd.Series(
            model.coef_,
            index=x.columns,
        )[ABILITY_COLUMNS]

        ability_score_train = (
            x_train[ABILITY_COLUMNS]
            .mul(ability_weights, axis=1)
            .sum(axis=1)
        )

        ability_score_test = (
            x_test[ABILITY_COLUMNS]
            .mul(ability_weights, axis=1)
            .sum(axis=1)
        )

        # Center the score around the training mean.
        score_mean = ability_score_train.mean()

        centered_train = (
            ability_score_train - score_mean
        ) / 100

        centered_test = (
            ability_score_test - score_mean
        ) / 100

        # The quadratic feature represents curvature
        # in the original model's prediction errors.
        quadratic_train = centered_train ** 2
        quadratic_test = centered_test ** 2

        # Learn the correction from training residuals.
        train_predictions = model.predict(x_train)

        train_residuals = (
            y_train - train_predictions
        )

        quadratic_model = LinearRegression(
            fit_intercept=False,
        )

        quadratic_model.fit(
            quadratic_train.to_frame(
                name="quadratic_ability_score"
            ),
            train_residuals,
        )

        # Apply the learned correction to test players.
        quadratic_correction = (
            quadratic_model.predict(
                quadratic_test.to_frame(
                    name="quadratic_ability_score"
                )
            )
        )

        corrected_predictions = (
            predictions + quadratic_correction
        )

        rounded_corrected_predictions = (
            corrected_predictions.round()
        )

        quadratic_mae = mean_absolute_error(
            y_test,
            rounded_corrected_predictions,
        )

        quadratic_exact_matches = (
            rounded_corrected_predictions == y_test
        ).mean() * 100

        quadratic_within_one = (
            abs(
                rounded_corrected_predictions - y_test
            ) <= 1
        ).mean() * 100

        fold_quadratic_mae.append(
            quadratic_mae
        )

        fold_quadratic_exact_matches.append(
            quadratic_exact_matches
        )

        fold_quadratic_within_one.append(
            quadratic_within_one
        )

    print()
    print("=" * 70)
    print(f"POSITION: {position}")
    print("=" * 70)

    print(f"Players: {len(position_data)}")

    print()
    print("5-Fold Cross-Validation:")

    print()
    print("Model A: Original linear model")

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
    print("Model B: Linear + quadratic correction")

    print(
        f"  MAE:            "
        f"{sum(fold_quadratic_mae) / len(fold_quadratic_mae):.3f}"
    )

    print(
        f"  Exact matches:  "
        f"{sum(fold_quadratic_exact_matches) / len(fold_quadratic_exact_matches):.1f}%"
    )

    print(
        f"  Within ±1:      "
        f"{sum(fold_quadratic_within_one) / len(fold_quadratic_within_one):.1f}%"
    )

    # ------------------------------------------------------
    # Final model with common intercept
    # ------------------------------------------------------

    if position == "GK":
        common_intercept = common_gk_intercept
    else:
        common_intercept = common_outfield_intercept

    # We fix the intercept and train only the ability weights.
    final_model = LinearRegression(
        fit_intercept=False,
        positive=True,
    )

    y_adjusted = y - common_intercept

    final_model.fit(x, y_adjusted)

    # Simplify weights to two decimal places.
    final_model.coef_ = final_model.coef_.round(2)

    final_weights = pd.Series(
        final_model.coef_,
        index=x.columns,
    )

    print()
    print("Model intercept:")
    print(
        f"  {common_intercept:+.6f}"
    )

    print()
    print("Final Ability Weights:")

    for ability in ABILITY_COLUMNS:
        weight = final_weights[ability]

        if weight > 0:
            print(
                f"  {ability}: {weight:.6f}"
            )

    # Calculate the weighted Ability Score,
    # excluding Weak Foot.
    ability_score = (
        x[ABILITY_COLUMNS]
        .mul(final_weights[ABILITY_COLUMNS], axis=1)
        .sum(axis=1)
        / 100
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

    # Residual relative to the common-intercept model.
    residual = (
        y
        - (
            ability_score * 100
            + common_intercept
        )
    )

    print()
    print("Residual mean:")
    print(
        f"  {residual.mean():+.6f}"
    )

    # Divide players into ten groups by weighted
    # Ability Score and inspect the mean residual.
    ability_groups = pd.qcut(
        ability_score,
        q=10,
        duplicates="drop",
    )

    print()
    print("OVR and residual by Ability Score:")

    for group in ability_groups.cat.categories:
        mask = ability_groups == group

        group_ability_score = ability_score[mask]
        group_ovr = y[mask]
        group_residuals = residual[mask]

        print(
            f"  {group}: "
            f"players = {len(group_residuals)}, "
            f"mean score = {group_ability_score.mean():.3f}, "
            f"mean OVR = {group_ovr.mean():.3f}, "
            f"mean residual = {group_residuals.mean():+.3f}"
        )


def main():
    print(
        f"Loading data from:\n{CSV_PATH}"
    )

    df = load_data()

    print(f"Rows loaded: {len(df)}")

    data = prepare_data(df)

    print(
        f"Rows after cleaning: {len(data)}"
    )

    positions = sorted(
        data[POSITION_COLUMN].unique()
    )

    print()
    print("Positions found:")
    print(", ".join(positions))

    # Calculate the common intercepts once,
    # before training the individual position models.
    (
        common_outfield_intercept,
        common_gk_intercept,
    ) = calculate_common_intercepts(data)

    for position in positions:
        train_position_model(
            data,
            position,
            common_outfield_intercept,
            common_gk_intercept,
        )


if __name__ == "__main__":
    main()