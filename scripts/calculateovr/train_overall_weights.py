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


# Decimal precisions to compare during cross-validation.
ROUNDING_DECIMALS_TO_TEST = [2, 3, 4, 5]

# Number of decimal places used in the final model.
WEIGHT_DECIMALS = 2

INTEGER_WEIGHT_SCALE = 100


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


def calculate_metrics(y_true, predictions):
    """Calculate metrics after rounding predicted OVR."""

    rounded_predictions = pd.Series(
        predictions,
        index=y_true.index,
    ).round()

    mae = mean_absolute_error(
        y_true,
        rounded_predictions,
    )

    exact_matches = (
        rounded_predictions == y_true
    ).mean() * 100

    within_one = (
        abs(rounded_predictions - y_true) <= 1
    ).mean() * 100

    return mae, exact_matches, within_one


def print_metrics(name, metrics):
    """Print the averaged cross-validation metrics."""

    mae, exact_matches, within_one = metrics

    print()
    print(name)

    print(f"  MAE:            {mae:.3f}")
    print(f"  Exact matches:  {exact_matches:.1f}%")
    print(f"  Within ±1:      {within_one:.1f}%")

def train_position_model(data, position):
    """Train and compare models for one registered position."""

    position_data = data[
        data[POSITION_COLUMN] == position
    ].copy()

    if len(position_data) < 10:
        print(
            f"\nSkipping {position}: "
            f"only {len(position_data)} players."
        )
        return

    # --------------------------------------------------
    # Model inputs
    # --------------------------------------------------

    x = position_data[ABILITY_COLUMNS].copy()

    # PES-style transformation for abilities.
    x = x - 25

    # Model B adds Weak Foot Accuracy as an additional
    # predictor on its original 1-4 scale.
    x_with_weak_foot = x.copy()
    x_with_weak_foot[WEAK_FOOT_COLUMN] = (
        position_data[WEAK_FOOT_COLUMN]
    )

    y = position_data[TARGET_COLUMN]

    kfold = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    # --------------------------------------------------
    # Model A: abilities only
    # --------------------------------------------------

    fold_a_mae = []
    fold_a_exact = []
    fold_a_within_one = []

    # --------------------------------------------------
    # Model B: abilities + Weak Foot Accuracy
    # --------------------------------------------------

    fold_b_mae = []
    fold_b_exact = []
    fold_b_within_one = []

    weak_foot_coefficients = []

    # --------------------------------------------------
    # Rounded-weight models for Model A
    # --------------------------------------------------

    rounded_metrics = {
        decimals: {
            "mae": [],
            "exact": [],
            "within_one": [],
        }
        for decimals in ROUNDING_DECIMALS_TO_TEST
    }

    integer_mae = []
    integer_exact = []
    integer_within_one = []

    for train_index, test_index in kfold.split(x):

        x_train = x.iloc[train_index]
        x_test = x.iloc[test_index]

        x_wf_train = x_with_weak_foot.iloc[train_index]
        x_wf_test = x_with_weak_foot.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        # --------------------------------------------------
        # Model A: abilities only
        # --------------------------------------------------

        model_a = LinearRegression(
            fit_intercept=True,
            positive=True,
        )

        model_a.fit(x_train, y_train)

        predictions_a = model_a.predict(x_test)

        metrics_a = calculate_metrics(
            y_test,
            predictions_a,
        )

        fold_a_mae.append(metrics_a[0])
        fold_a_exact.append(metrics_a[1])
        fold_a_within_one.append(metrics_a[2])

        # --------------------------------------------------
        # Model B: abilities + Weak Foot Accuracy
        # --------------------------------------------------

        model_b = LinearRegression(
            fit_intercept=True,
            positive=True,
        )

        model_b.fit(x_wf_train, y_train)

        predictions_b = model_b.predict(x_wf_test)

        metrics_b = calculate_metrics(
            y_test,
            predictions_b,
        )

        fold_b_mae.append(metrics_b[0])
        fold_b_exact.append(metrics_b[1])
        fold_b_within_one.append(metrics_b[2])

        weak_foot_coefficients.append(
            model_b.coef_[
                x_wf_train.columns.get_loc(
                    WEAK_FOOT_COLUMN
                )
            ]
        )

        # --------------------------------------------------
        # Integer weights: Model A
        # --------------------------------------------------

        integer_weights = (
            model_a.coef_ * INTEGER_WEIGHT_SCALE
        ).round().astype(int)

        predictions_integer = (
            x_test.to_numpy() @ integer_weights
            / INTEGER_WEIGHT_SCALE
            + model_a.intercept_
        )

        metrics_integer = calculate_metrics(
            y_test,
            predictions_integer,
        )

        integer_mae.append(metrics_integer[0])
        integer_exact.append(metrics_integer[1])
        integer_within_one.append(metrics_integer[2])

        # --------------------------------------------------
        # Rounded weights: Model A
        # --------------------------------------------------

        for decimals in ROUNDING_DECIMALS_TO_TEST:

            rounded_weights = model_a.coef_.round(
                decimals
            )

            predictions = (
                x_test.to_numpy() @ rounded_weights
                + model_a.intercept_
            )

            metrics = calculate_metrics(
                y_test,
                predictions,
            )

            rounded_metrics[decimals]["mae"].append(
                metrics[0]
            )

            rounded_metrics[decimals]["exact"].append(
                metrics[1]
            )

            rounded_metrics[decimals]["within_one"].append(
                metrics[2]
            )

    # --------------------------------------------------
    # Display cross-validation results
    # --------------------------------------------------

    print()
    print("=" * 70)
    print(f"POSITION: {position}")
    print("=" * 70)

    print(f"Players: {len(position_data)}")

    print()
    print("5-Fold Cross-Validation:")

    print_metrics(
        "Model A: Abilities only",
        (
            sum(fold_a_mae) / len(fold_a_mae),
            sum(fold_a_exact) / len(fold_a_exact),
            sum(fold_a_within_one) / len(fold_a_within_one),
        ),
    )

    print_metrics(
        "Model B: Abilities + Weak Foot",
        (
            sum(fold_b_mae) / len(fold_b_mae),
            sum(fold_b_exact) / len(fold_b_exact),
            sum(fold_b_within_one) / len(fold_b_within_one),
        ),
    )

    print()
    print(
        "Weak Foot coefficient in Model B:"
    )
    print(
        f"  Mean: {sum(weak_foot_coefficients) / len(weak_foot_coefficients):+.6f}"
    )

    print_metrics(
        "Integer weights (Model A)",
        (
            sum(integer_mae) / len(integer_mae),
            sum(integer_exact) / len(integer_exact),
            sum(integer_within_one) / len(integer_within_one),
        ),
    )

    for decimals in ROUNDING_DECIMALS_TO_TEST:

        metrics = rounded_metrics[decimals]

        print_metrics(
            (
                f"Weights rounded to {decimals} decimals "
                f"(Model A)"
            ),
            (
                sum(metrics["mae"]) / len(metrics["mae"]),
                sum(metrics["exact"]) / len(metrics["exact"]),
                sum(metrics["within_one"]) / len(
                    metrics["within_one"]
                ),
            ),
        )

    # --------------------------------------------------
    # Final model: Model B
    # --------------------------------------------------

    final_model = LinearRegression(
        fit_intercept=True,
        positive=True,
    )

    final_model.fit(
        x_with_weak_foot,
        y,
    )

    final_weights = pd.Series(
        final_model.coef_.round(WEIGHT_DECIMALS),
        index=x_with_weak_foot.columns,
    )

    final_intercept = final_model.intercept_

    print()
    print("Final Model B:")

    print(f"  Intercept: {final_intercept:+.6f}")

    print()
    print("Final Ability Weights:")

    for ability in ABILITY_COLUMNS:
        weight = final_weights[ability]

        if weight > 0:
            print(
                f"  {ability}: "
                f"{weight:.{WEIGHT_DECIMALS}f}"
            )

    print()
    print("Weak Foot Weight:")

    print(
        f"  {WEAK_FOOT_COLUMN}: "
        f"{final_weights[WEAK_FOOT_COLUMN]:.{WEIGHT_DECIMALS}f}"
    )

    # --------------------------------------------------
    # Final model diagnostics
    # --------------------------------------------------

    predictions = (
        x_with_weak_foot.to_numpy()
        @ final_weights.to_numpy()
        + final_intercept
    )

    residual = y - predictions

    # Ability Score using the ability weights only.
    # Weak Foot is kept separate for now because we are
    # still investigating its transformation.
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
    print("Ability Score:")

    print(f"  Minimum: {ability_score.min():.3f}")
    print(f"  Maximum: {ability_score.max():.3f}")
    print(f"  Mean:    {ability_score.mean():.3f}")

    print()
    print("Residual mean (real OVR - predicted OVR):")
    print(f"  {residual.mean():+.6f}")

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

    print(f"Rows after cleaning: {len(data)}")

    positions = sorted(
        data[POSITION_COLUMN].unique()
    )

    print()
    print("Positions found:")
    print(", ".join(positions))

    for position in positions:
        train_position_model(
            data,
            position,
        )


if __name__ == "__main__":
    main()