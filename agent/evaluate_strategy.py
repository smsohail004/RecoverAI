import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/payments_with_recovery.csv"
MODEL_PATH = "models/recovery_model.joblib"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)


# We only evaluate failed payments.

df = df[
    df["status"] == "FAILED"
].copy()


# ============================================================
# STRATEGY A — SIMPLE BASELINE
# ============================================================

recoverable_reasons = [
    "BANK_ERROR",
    "NETWORK_ERROR",
    "TIMEOUT",
    "USER_CANCELLED",
]

baseline_mask = (
    df["failure_reason"].isin(
        recoverable_reasons
    )
    &
    (df["customer_success_rate"] >= 0.75)
)

df["baseline_selected"] = baseline_mask


# ============================================================
# STRATEGY B — RECOVERAI ML
# ============================================================

FEATURES = [
    "amount",
    "payment_method",
    "failure_reason",
    "attempt_number",
    "customer_success_rate",
]

X = df[FEATURES]

df["ml_probability"] = model.predict_proba(X)[:, 1]

df["ml_expected_recovery"] = (
    df["amount"] * df["ml_probability"]
)


# Automatically select high-confidence opportunities.

df["ml_selected"] = (
    (df["ml_probability"] >= 0.75)
    &
    (df["failure_reason"] != "FRAUD_SUSPECTED")
    &
    (df["attempt_number"] < 4)
)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_strategy(
    dataframe,
    selection_column,
    strategy_name
):

    selected = dataframe[
        dataframe[selection_column] == True
    ].copy()

    selected_count = len(selected)

    if selected_count == 0:
        return {
            "strategy": strategy_name,
            "selected": 0,
            "successful": 0,
            "recovery_rate": 0,
            "revenue_recovered": 0,
            "revenue_attempted": 0,
        }

    successful = selected[
        selected["recovery_success"] == 1
    ]

    successful_count = len(successful)

    recovery_rate = (
        successful_count /
        selected_count
    )

    revenue_recovered = successful[
        "amount"
    ].sum()

    revenue_attempted = selected[
        "amount"
    ].sum()

    return {
        "strategy": strategy_name,
        "selected": selected_count,
        "successful": successful_count,
        "recovery_rate": recovery_rate,
        "revenue_recovered": revenue_recovered,
        "revenue_attempted": revenue_attempted,
    }


# ============================================================
# EVALUATE BOTH
# ============================================================

baseline_results = evaluate_strategy(
    df,
    "baseline_selected",
    "Baseline Rule",
)

ml_results = evaluate_strategy(
    df,
    "ml_selected",
    "RecoverAI ML",
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

results = pd.DataFrame(
    [
        baseline_results,
        ml_results,
    ]
)


print()
print("=" * 75)
print("             RECOVERAI STRATEGY EVALUATION")
print("=" * 75)

print()

for _, row in results.iterrows():

    print(f"STRATEGY: {row['strategy']}")
    print("-" * 75)

    print(
        f"Payments selected       : "
        f"{int(row['selected']):,}"
    )

    print(
        f"Successful recoveries   : "
        f"{int(row['successful']):,}"
    )

    print(
        f"Recovery rate           : "
        f"{row['recovery_rate']:.2%}"
    )

    print(
        f"Revenue attempted       : "
        f"₹{row['revenue_attempted']:,.2f}"
    )

    print(
        f"Revenue recovered       : "
        f"₹{row['revenue_recovered']:,.2f}"
    )

    print()


# ============================================================
# COMPARISON
# ============================================================

baseline_revenue = (
    baseline_results["revenue_recovered"]
)

ml_revenue = (
    ml_results["revenue_recovered"]
)

revenue_difference = (
    ml_revenue -
    baseline_revenue
)


baseline_rate = (
    baseline_results["recovery_rate"]
)

ml_rate = (
    ml_results["recovery_rate"]
)


print("=" * 75)
print("                    BUSINESS IMPACT")
print("=" * 75)

print()

print(
    f"Revenue recovered by baseline : "
    f"₹{baseline_revenue:,.2f}"
)

print(
    f"Revenue recovered by RecoverAI: "
    f"₹{ml_revenue:,.2f}"
)

print(
    f"Revenue difference             : "
    f"₹{revenue_difference:,.2f}"
)

print()

print(
    f"Baseline recovery rate        : "
    f"{baseline_rate:.2%}"
)

print(
    f"RecoverAI recovery rate       : "
    f"{ml_rate:.2%}"
)

print()

print("=" * 75)