import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/intervention_history.csv"
MODEL_PATH = "models/action_model_v2.joblib"


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)


# ============================================================
# CREATE PAYMENT-LEVEL OUTCOMES
# ============================================================

retry = (
    df[df["action"] == "RETRY"]
    [
        [
            "payment_id",
            "recovery_success",
        ]
    ]
    .rename(
        columns={
            "recovery_success":
                "retry_success"
        }
    )
)


reminder = (
    df[df["action"] == "SEND_REMINDER"]
    [
        [
            "payment_id",
            "recovery_success",
        ]
    ]
    .rename(
        columns={
            "recovery_success":
                "reminder_success"
        }
    )
)


payments = (
    df.drop_duplicates(
        subset=["payment_id"]
    )
    .copy()
)


payments = payments.merge(
    retry,
    on="payment_id",
    how="left",
)


payments = payments.merge(
    reminder,
    on="payment_id",
    how="left",
)


# ============================================================
# DETERMINE ACTUAL BEST ACTION
# ============================================================

def determine_actual_best(row):

    retry_result = row["retry_success"]

    reminder_result = row[
        "reminder_success"
    ]

    if retry_result == 1 and reminder_result == 0:
        return "RETRY"

    if reminder_result == 1 and retry_result == 0:
        return "SEND_REMINDER"

    if retry_result == 1 and reminder_result == 1:

        # Both worked.
        # Prefer the cheaper intervention.

        return "SEND_REMINDER"

    # Neither worked.

    return "NO_RECOVERY"


payments[
    "actual_best_action"
] = payments.apply(
    determine_actual_best,
    axis=1,
)


# ============================================================
# RECOVERAI PREDICTION
# ============================================================

predictions = []


for _, payment in payments.iterrows():

    scores = []


    for action in [
        "RETRY",
        "SEND_REMINDER",
    ]:

        candidate = payment[
            [
                "amount",
                "payment_method",
                "failure_reason",
                "attempt_number",
                "customer_success_rate",
            ]
        ].copy()

        candidate["action"] = action


        candidate_df = pd.DataFrame(
            [candidate]
        )


        probability = (
            model.predict_proba(
                candidate_df
            )[0][1]
        )


        scores.append({
            "action":
                action,

            "probability":
                probability,
        })


    best = max(
        scores,
        key=lambda x:
            x["probability"],
    )


    predictions.append({
        "payment_id":
            payment["payment_id"],

        "predicted_action":
            best["action"],

        "predicted_probability":
            best["probability"],
    })


prediction_df = pd.DataFrame(
    predictions
)


payments = payments.merge(
    prediction_df,
    on="payment_id",
)


# ============================================================
# EVALUATE
# ============================================================

evaluated = payments[
    payments["actual_best_action"] !=
    "NO_RECOVERY"
].copy()


evaluated[
    "correct"
] = (
    evaluated["predicted_action"]
    ==
    evaluated["actual_best_action"]
)


overall_accuracy = (
    evaluated["correct"].mean()
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 80)
print("              RECOVERAI BEST-ACTION EVALUATION")
print("=" * 80)

print()

print(
    f"Total payments          : "
    f"{len(payments):,}"
)

print(
    f"Payments with recovery  : "
    f"{len(evaluated):,}"
)

print()

print(
    f"Best-action accuracy    : "
    f"{overall_accuracy:.2%}"
)


# ============================================================
# BREAKDOWN
# ============================================================

print()
print("=" * 80)
print("                 PERFORMANCE BY FAILURE")
print("=" * 80)

print()

breakdown = (
    evaluated
    .groupby("failure_reason")
    .agg(
        payments=(
            "payment_id",
            "count",
        ),

        correct=(
            "correct",
            "sum",
        ),

        accuracy=(
            "correct",
            "mean",
        ),
    )
    .sort_values(
        "accuracy",
        ascending=False,
    )
)


for reason, row in breakdown.iterrows():

    print(
        f"{reason:20}"
        f" payments={int(row['payments']):4d}"
        f" | correct={int(row['correct']):4d}"
        f" | accuracy="
        f"{row['accuracy']:.2%}"
    )


# ============================================================
# ACTION DISTRIBUTION
# ============================================================

print()
print("=" * 80)
print("                 ACTION DISTRIBUTION")
print("=" * 80)

print()

print(
    "Predicted:"
)

print(
    payments[
        "predicted_action"
    ].value_counts()
)


print()

print(
    "Actual best:"
)

print(
    payments[
        "actual_best_action"
    ].value_counts()
)


print()
print("=" * 80)