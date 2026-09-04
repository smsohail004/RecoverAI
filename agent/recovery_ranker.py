import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/payments_with_recovery.csv"
MODEL_PATH = "models/recovery_model.joblib"

OUTPUT_PATH = "data/recovery_opportunities.csv"


# ============================================================
# LOAD DATA AND MODEL
# ============================================================

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)


# ============================================================
# SELECT FAILED PAYMENTS
# ============================================================

failed_df = df[
    df["status"] == "FAILED"
].copy()


# ============================================================
# FEATURES USED BY THE MODEL
# ============================================================

FEATURES = [
    "amount",
    "payment_method",
    "failure_reason",
    "attempt_number",
    "customer_success_rate",
]


X = failed_df[FEATURES]


# ============================================================
# PREDICT RECOVERY PROBABILITY
# ============================================================

failed_df["predicted_recovery_probability"] = (
    model.predict_proba(X)[:, 1]
)


# ============================================================
# EXPECTED RECOVERY VALUE
# ============================================================

failed_df["expected_recovery_value"] = (
    failed_df["amount"]
    * failed_df["predicted_recovery_probability"]
)


# ============================================================
# INITIAL ACTION POLICY
# ============================================================

def choose_action(row):

    probability = row[
        "predicted_recovery_probability"
    ]

    reason = row[
        "failure_reason"
    ]

    attempts = row[
        "attempt_number"
    ]


    # ----------------------------------------
    # Never automatically recover suspected
    # fraud.
    # ----------------------------------------

    if reason == "FRAUD_SUSPECTED":
        return "ESCALATE"


    # ----------------------------------------
    # Don't keep retrying indefinitely.
    # ----------------------------------------

    if attempts >= 4:
        return "ESCALATE"


    # ----------------------------------------
    # High-confidence opportunities.
    # ----------------------------------------

    if probability >= 0.75:
        return "RECOVER"


    # ----------------------------------------
    # Medium-confidence opportunities.
    # ----------------------------------------

    if probability >= 0.50:
        return "REVIEW"


    # ----------------------------------------
    # Low-confidence opportunities.
    # ----------------------------------------

    return "DO_NOT_ACT"


failed_df["recommended_action"] = (
    failed_df.apply(
        choose_action,
        axis=1
    )
)


# ============================================================
# RANK RECOVERY OPPORTUNITIES
# ============================================================

ranked_df = failed_df.sort_values(
    "expected_recovery_value",
    ascending=False
)


# ============================================================
# SAVE RESULTS
# ============================================================

ranked_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

recover_df = ranked_df[
    ranked_df["recommended_action"] == "RECOVER"
]

review_df = ranked_df[
    ranked_df["recommended_action"] == "REVIEW"
]

escalate_df = ranked_df[
    ranked_df["recommended_action"] == "ESCALATE"
]

do_not_act_df = ranked_df[
    ranked_df["recommended_action"] == "DO_NOT_ACT"
]


expected_revenue = recover_df[
    "expected_recovery_value"
].sum()


actual_recovered_revenue = recover_df.loc[
    recover_df["recovery_success"] == 1,
    "amount"
].sum()


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 75)
print("              RECOVERAI DECISION ENGINE")
print("=" * 75)

print()

print(
    f"Failed payments analyzed      : "
    f"{len(ranked_df):,}"
)

print(
    f"Automatic recovery candidates : "
    f"{len(recover_df):,}"
)

print(
    f"Human-review candidates       : "
    f"{len(review_df):,}"
)

print(
    f"Escalated payments             : "
    f"{len(escalate_df):,}"
)

print(
    f"Do-not-act payments             : "
    f"{len(do_not_act_df):,}"
)

print()

print(
    f"Expected recovery value       : "
    f"₹{expected_revenue:,.2f}"
)

print(
    f"Historical recovery value     : "
    f"₹{actual_recovered_revenue:,.2f}"
)

print()

print("=" * 75)
print("TOP 10 RECOVERY OPPORTUNITIES")
print("=" * 75)

columns_to_show = [
    "payment_id",
    "amount",
    "failure_reason",
    "attempt_number",
    "predicted_recovery_probability",
    "expected_recovery_value",
    "recommended_action",
]

display_df = ranked_df[
    columns_to_show
].head(10).copy()


display_df[
    "predicted_recovery_probability"
] = (
    display_df[
        "predicted_recovery_probability"
    ] * 100
).round(2)


display_df[
    "expected_recovery_value"
] = (
    display_df[
        "expected_recovery_value"
    ].round(2)
)


print(
    display_df.to_string(
        index=False
    )
)


print()

print("=" * 75)

print(
    f"Results saved to: "
    f"{OUTPUT_PATH}"
)

print("=" * 75)