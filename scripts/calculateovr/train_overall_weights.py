from pathlib import Path

import numpy as np
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


def analyze_theoretical_ability_score(data):
    """Analyze theoretical PES Ability Scores for wide players."""

    # Theoretical weights supplied for the two position groups.
    theoretical_weights = {
        "LWF": {
            "offensive_awareness": 17,
            "ball_control": 19,
            "dribbling": 15,
            "speed": 15,
            "acceleration": 15,
            "finishing": 11,
            "lofted_pass": 9,
            "tight_possession": 7,
            "stamina": 6,
            WEAK_FOOT_COLUMN: 47,
        },
        "RWF": {
            "offensive_awareness": 17,
            "ball_control": 19,
            "dribbling": 15,
            "speed": 15,
            "acceleration": 15,
            "finishing": 11,
            "lofted_pass": 9,
            "tight_possession": 7,
            "stamina": 6,
            WEAK_FOOT_COLUMN: 47,
        },
        "LMF": {
            "speed": 24,
            "acceleration": 21,
            "dribbling": 17,
            "ball_control": 15,
            "stamina": 13,
            "lofted_pass": 12,
            WEAK_FOOT_COLUMN: 56,
        },
        "RMF": {
            "speed": 24,
            "acceleration": 21,
            "dribbling": 17,
            "ball_control": 15,
            "stamina": 13,
            "lofted_pass": 12,
            WEAK_FOOT_COLUMN: 56,
        },
    }

    position_bonuses = {
        "LWF": 10,
        "RWF": 10,
        "LMF": 8,
        "RMF": 8,
    }

    print()
    print("=" * 70)
    print("THEORETICAL ABILITY SCORE")
    print("=" * 70)

    for position, weights in theoretical_weights.items():

        position_data = data[
            data[POSITION_COLUMN] == position
        ].copy()

        if position_data.empty:
            print(f"\nSkipping {position}: no players found.")
            continue

        # Sum the weighted standard attributes.
        # Each attribute is transformed using (value - 25).
        ability_sum = pd.Series(
            0.0,
            index=position_data.index,
        )

        for attribute, weight in weights.items():

            if attribute == WEAK_FOOT_COLUMN:
                continue

            ability_sum += (
                position_data[attribute] - 25
            ) * weight

        # Weak Foot uses its original 1-4 scale.
        weak_foot_weight = weights[WEAK_FOOT_COLUMN]

        score = (
            ability_sum
            + position_data[WEAK_FOOT_COLUMN]
            * weak_foot_weight
        ) / 100

        # Position bonus is added directly to the Ability Score.
        bonus = position_bonuses[position]

        score_with_bonus = score + bonus
        ovr = position_data[TARGET_COLUMN]

        # Diagnostics for the theoretical score itself.
        correlation = score.corr(ovr)

        slope, intercept = np.polyfit(
            score,
            ovr,
            1,
        )

        predicted_ovr = slope * score + intercept

        linear_fit_mae = mean_absolute_error(
            ovr,
            predicted_ovr,
        )

        # Direct comparison between the theoretical Ability Score
        # and the actual OVR.
        direct_error = score_with_bonus - ovr
        direct_absolute_error = direct_error.abs()

        direct_mae = direct_absolute_error.mean()
        mean_error = direct_error.mean()

        exact_match = (
            direct_absolute_error.round(10) < 0.5
        ).mean() * 100

        within_one = (
            direct_absolute_error <= 1
        ).mean() * 100

        print()
        print("-" * 70)
        print(f"Position: {position}")
        print(f"Players: {len(position_data)}")
        print(f"Position bonus: +{bonus}")

        print()
        print("  Weak Foot = original value")

        print(
            f"    Score range: "
            f"{score.min():.3f} - "
            f"{score.max():.3f}"
        )
        print(f"    Mean score:  {score.mean():.3f}")
        print(
            f"    Mean + bonus: "
            f"{score_with_bonus.mean():.3f}"
        )

        print()
        print("    Direct comparison with OVR:")
        print(f"      Mean error:      {mean_error:+.3f}")
        print(f"      Direct MAE:      {direct_mae:.3f}")
        print(f"      Exact match:     {exact_match:.1f}%")
        print(f"      Within ±1 OVR:   {within_one:.1f}%")

        print()
        print("    Linear diagnostic:")
        print(f"      Correlation:      {correlation:.4f}")
        print(f"      Slope:            {slope:.4f}")
        print(f"      Intercept:        {intercept:.4f}")
        print(f"      Linear fit MAE:   {linear_fit_mae:.3f}")


def analyze_implied_curved_score(data):
    """Analyze the Curved Score implied by the 60/40 OVR formula."""

    theoretical_weights = {
        "LWF": {
            "offensive_awareness": 17,
            "ball_control": 19,
            "dribbling": 15,
            "speed": 15,
            "acceleration": 15,
            "finishing": 11,
            "lofted_pass": 9,
            "tight_possession": 7,
            "stamina": 6,
            WEAK_FOOT_COLUMN: 47,
        },
        "RWF": {
            "offensive_awareness": 17,
            "ball_control": 19,
            "dribbling": 15,
            "speed": 15,
            "acceleration": 15,
            "finishing": 11,
            "lofted_pass": 9,
            "tight_possession": 7,
            "stamina": 6,
            WEAK_FOOT_COLUMN: 47,
        },
        "LMF": {
            "speed": 24,
            "acceleration": 21,
            "dribbling": 17,
            "ball_control": 15,
            "stamina": 13,
            "lofted_pass": 12,
            WEAK_FOOT_COLUMN: 56,
        },
        "RMF": {
            "speed": 24,
            "acceleration": 21,
            "dribbling": 17,
            "ball_control": 15,
            "stamina": 13,
            "lofted_pass": 12,
            WEAK_FOOT_COLUMN: 56,
        },
    }

    position_bonuses = {
        "LWF": 10,
        "RWF": 10,
        "LMF": 8,
        "RMF": 8,
    }

    # --------------------------------------------------
    # Shared regression groups
    #
    # LWF + RWF must use exactly the same Curved Score
    # weights.
    #
    # LMF + RMF must use exactly the same Curved Score
    # weights.
    # --------------------------------------------------

    shared_position_groups = {
        "LWF + RWF": ["LWF", "RWF"],
        "LMF + RMF": ["LMF", "RMF"],
    }

    print()
    print("=" * 70)
    print("IMPLIED CURVED SCORE")
    print("=" * 70)

    for position, weights in theoretical_weights.items():

        position_data = data[
            data[POSITION_COLUMN] == position
        ].copy()

        if position_data.empty:
            continue

        # Calculate Ability Score without position bonus.
        ability_sum = pd.Series(
            0.0,
            index=position_data.index,
        )

        for attribute, weight in weights.items():

            if attribute == WEAK_FOOT_COLUMN:
                continue

            ability_sum += (
                position_data[attribute] - 25
            ) * weight

        # Weak Foot uses its original 1-4 scale.
        weak_foot_weight = weights[WEAK_FOOT_COLUMN]

        ability_score = (
            ability_sum
            + position_data[WEAK_FOOT_COLUMN]
            * weak_foot_weight
        ) / 100

        bonus = position_bonuses[position]
        ovr = position_data[TARGET_COLUMN]

        # --------------------------------------------------
        # Hypothesis 1:
        #
        # OVR = 0.6 * (A + B) + 0.4 * C
        # --------------------------------------------------

        curved_score_h1 = (
            ovr
            - 0.6 * (ability_score + bonus)
        ) / 0.4

        # --------------------------------------------------
        # Hypothesis 2:
        #
        # OVR = 0.6 * A + 0.4 * C + B
        # --------------------------------------------------

        curved_score_h2 = (
            ovr
            - 0.6 * ability_score
            - bonus
        ) / 0.4

        print()
        print("-" * 70)
        print(f"Position: {position}")
        print(f"Players: {len(position_data)}")
        print(f"Position bonus: +{bonus}")
        print()
        print("  Weak Foot = original value")

        # --------------------------------------------------
        # Analyze both hypotheses
        # --------------------------------------------------

        for hypothesis_name, curved_score in [
            ("Hypothesis 1", curved_score_h1),
            ("Hypothesis 2", curved_score_h2),
        ]:

            correlation = ability_score.corr(
                curved_score
            )

            slope, intercept = np.polyfit(
                ability_score,
                curved_score,
                1,
            )

            predicted_curved_score = (
                slope * ability_score
                + intercept
            )

            linear_fit_mae = mean_absolute_error(
                curved_score,
                predicted_curved_score,
            )

            print()
            print(f"    {hypothesis_name}:")

            print(
                f"      C range: "
                f"{curved_score.min():.3f} - "
                f"{curved_score.max():.3f}"
            )

            print(
                f"      C mean:   "
                f"{curved_score.mean():.3f}"
            )

            print(
                f"      C correlation: "
                f"{correlation:.4f}"
            )

            print(
                f"      C slope:       "
                f"{slope:.4f}"
            )

            print(
                f"      C intercept:   "
                f"{intercept:.4f}"
            )

            print(
                f"      C linear MAE:  "
                f"{linear_fit_mae:.3f}"
            )

        # --------------------------------------------------
        # Quadratic fit for Hypothesis 2
        # --------------------------------------------------

        quadratic_coefficients = np.polyfit(
            ability_score,
            curved_score_h2,
            2,
        )

        predicted_curved_score = np.polyval(
            quadratic_coefficients,
            ability_score,
        )

        quadratic_fit_mae = mean_absolute_error(
            curved_score_h2,
            predicted_curved_score,
        )

        print()
        print("    Hypothesis 2 quadratic fit:")

        print(
            f"      C = "
            f"{quadratic_coefficients[0]:.4f} × A² "
            f"+ {quadratic_coefficients[1]:.4f} × A "
            f"+ {quadratic_coefficients[2]:.4f}"
        )

        print(
            f"      C quadratic MAE: "
            f"{quadratic_fit_mae:.3f}"
        )

    # ======================================================
    # SHARED CURVED SCORE REGRESSION
    #
    # This is the new experiment.
    #
    # LWF + RWF:
    #     one single model
    #     one single set of weights
    #
    # LMF + RMF:
    #     one single model
    #     one single set of weights
    # ======================================================

    print()
    print("=" * 70)
    print("SHARED CURVED SCORE REGRESSION")
    print("=" * 70)

    for group_name, positions in shared_position_groups.items():

        group_data = data[
            data[POSITION_COLUMN].isin(positions)
        ].copy()

        if group_data.empty:
            print(
                f"\nSkipping {group_name}: "
                f"no players found."
            )
            continue

        # --------------------------------------------------
        # Build the theoretical Ability Score for every
        # player in the shared group.
        #
        # LWF/RWF use the same theoretical weights.
        # LMF/RMF use the same theoretical weights.
        # --------------------------------------------------

        group_ability_score = pd.Series(
            0.0,
            index=group_data.index,
        )

        for position in positions:

            position_mask = (
                group_data[POSITION_COLUMN] == position
            )

            position_weights = theoretical_weights[
                position
            ]

            position_ability_sum = pd.Series(
                0.0,
                index=group_data.index,
            )

            for attribute, weight in (
                position_weights.items()
            ):

                if attribute == WEAK_FOOT_COLUMN:
                    continue

                position_ability_sum += (
                    group_data[attribute] - 25
                ) * weight

            weak_foot_weight = position_weights[
                WEAK_FOOT_COLUMN
            ]

            position_score = (
                position_ability_sum
                + group_data[WEAK_FOOT_COLUMN]
                * weak_foot_weight
            ) / 100

            group_ability_score.loc[
                position_mask
            ] = position_score.loc[position_mask]

        # --------------------------------------------------
        # Calculate implied Curved Score using Hypothesis 2.
        #
        # OVR = 0.6 * A + 0.4 * C + B
        #
        # Important:
        # the position bonus is still position-specific.
        # --------------------------------------------------

        group_bonuses = group_data[
            POSITION_COLUMN
        ].map(position_bonuses)

        group_ovr = group_data[
            TARGET_COLUMN
        ]

        group_curved_score = (
            group_ovr
            - 0.6 * group_ability_score
            - group_bonuses
        ) / 0.4

        # --------------------------------------------------
        # Build regression features.
        #
        # The feature list comes from the first position
        # in the group because left/right positions share
        # the same attribute structure.
        # --------------------------------------------------

        reference_weights = theoretical_weights[
            positions[0]
        ]

        curved_score_features = group_data[
            [
                attribute
                for attribute in reference_weights
                if attribute != WEAK_FOOT_COLUMN
            ]
        ].copy()

        curved_score_features = (
            curved_score_features - 25
        )

        curved_score_features[
            WEAK_FOOT_COLUMN
        ] = group_data[
            WEAK_FOOT_COLUMN
        ]

        # --------------------------------------------------
        # Train ONE model for the entire group.
        # --------------------------------------------------

        curved_score_model = LinearRegression(
            fit_intercept=True,
            positive=False,
        )

        curved_score_model.fit(
            curved_score_features,
            group_curved_score,
        )

        predicted_curved_score = (
            curved_score_model.predict(
                curved_score_features
            )
        )

        # --------------------------------------------------
        # Combined metrics
        # --------------------------------------------------

        combined_mae = mean_absolute_error(
            group_curved_score,
            predicted_curved_score,
        )

        combined_correlation = np.corrcoef(
            group_curved_score,
            predicted_curved_score,
        )[0, 1]

        print()
        print("-" * 70)
        print(f"Shared group: {group_name}")
        print(f"Positions: {', '.join(positions)}")
        print(f"Players: {len(group_data)}")

        print()
        print("Combined shared model:")

        print(
            f"  C regression MAE: "
            f"{combined_mae:.3f}"
        )

        print(
            f"  C correlation:    "
            f"{combined_correlation:.4f}"
        )

        print()
        print("Shared learned weights:")

        for attribute, coefficient in zip(
            curved_score_features.columns,
            curved_score_model.coef_,
        ):
            print(
                f"  {attribute}: "
                f"{coefficient:.4f}"
            )

        print(
            f"  Intercept: "
            f"{curved_score_model.intercept_:+.4f}"
        )

        # --------------------------------------------------
        # Per-position diagnostics using the SAME model.
        # --------------------------------------------------

        print()
        print("MAE by position using shared weights:")

        for position in positions:

            position_mask = (
                group_data[POSITION_COLUMN] == position
            )

            position_true = group_curved_score[
                position_mask
            ]

            position_predictions = pd.Series(
                predicted_curved_score,
                index=group_data.index,
            )[position_mask]

            position_mae = mean_absolute_error(
                position_true,
                position_predictions,
            )

            position_correlation = np.corrcoef(
                position_true,
                position_predictions,
            )[0, 1]

            print(
                f"  {position}: "
                f"MAE = {position_mae:.3f}, "
                f"correlation = {position_correlation:.4f}, "
                f"players = {position_mask.sum()}"
            )


def main():
    print(
        f"Loading data from:\n{CSV_PATH}"
    )

    df = load_data()

    print(f"Rows loaded: {len(df)}")

    data = prepare_data(df)

    print(f"Rows after cleaning: {len(data)}")

    analyze_theoretical_ability_score(data)

    analyze_implied_curved_score(data)

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