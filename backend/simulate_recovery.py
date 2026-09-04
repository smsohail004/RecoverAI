import os
import sys
import random
from datetime import datetime

import joblib
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "payments.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "batch_recovery_results.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "recovery_model.joblib"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

MAX_RECOVERY_ATTEMPTS = 3

HIGH_CONFIDENCE_THRESHOLD = 0.75

MODERATE_CONFIDENCE_THRESHOLD = 0.50


random.seed(RANDOM_SEED)


# ============================================================
# LOAD DATA AND MODEL
# ============================================================

print()
print("=" * 70)
print("          RECOVERAI BATCH REVENUE RECOVERY SIMULATOR")
print("=" * 70)
print()

df = pd.read_csv(INPUT_PATH)

model = joblib.load(MODEL_PATH)


# ============================================================
# SIMULATE RECOVERY OUTCOME
# ============================================================

def simulate_recovery(probability):
    """
    Simulate whether a recommended recovery
    workflow successfully recovers the payment.

    SIMULATION ONLY.
    No real payment is processed.
    """

    return random.random() < probability


# ============================================================
# DECISION ENGINE
# ============================================================

def decide_recovery_action(row, probability):
    """
    Determine the safest bounded recovery action.
    """

    failure_reason = row["failure_reason"]
    attempt_number = row["attempt_number"]

    # --------------------------------------------------------
    # STOPPING RULE 1: Fraud
    # --------------------------------------------------------

    if failure_reason == "FRAUD_SUSPECTED":

        return (
            "ESCALATE",
            "Fraud-related payment requires human review.",
            True
        )

    # --------------------------------------------------------
    # STOPPING RULE 2: Maximum attempts
    # --------------------------------------------------------

    if attempt_number >= MAX_RECOVERY_ATTEMPTS:

        return (
            "ESCALATE",
            "Maximum automated recovery attempts reached.",
            True
        )

    # --------------------------------------------------------
    # HIGH CONFIDENCE
    # --------------------------------------------------------

    if probability >= HIGH_CONFIDENCE_THRESHOLD:

        return (
            "RETRY",
            "High predicted recovery probability.",
            False
        )

    # --------------------------------------------------------
    # MODERATE CONFIDENCE
    # --------------------------------------------------------

    if probability >= MODERATE_CONFIDENCE_THRESHOLD:

        return (
            "SEND_REMINDER",
            "Moderate recovery probability. Reminder preferred.",
            False
        )

    # --------------------------------------------------------
    # LOW CONFIDENCE STOPPING RULE
    # --------------------------------------------------------

    return (
        "DO_NOT_ACT",
        "Low predicted recovery probability. Intervention stopped.",
        True
    )


# ============================================================
# PROCESS FAILED PAYMENTS
# ============================================================

failed_df = df[
    df["status"] == "FAILED"
].copy()


results = []


for _, payment in failed_df.iterrows():

    # --------------------------------------------------------
    # Prepare features for ML model
    # --------------------------------------------------------

    payment_features = pd.DataFrame([
        {
            "amount": payment["amount"],
            "payment_method": payment["payment_method"],
            "failure_reason": payment["failure_reason"],
            "attempt_number": payment["attempt_number"],
            "customer_success_rate":
                payment["customer_success_rate"],
        }
    ])

    # --------------------------------------------------------
    # Predict recovery probability
    # --------------------------------------------------------

    probability = model.predict_proba(
        payment_features
    )[0][1]


    # --------------------------------------------------------
    # Expected recovery value
    # --------------------------------------------------------

    expected_recovery = (
        payment["amount"] * probability
    )


    # --------------------------------------------------------
    # Decide bounded recovery action
    # --------------------------------------------------------

    action, reason, stopped = decide_recovery_action(
        payment,
        probability
    )


    # --------------------------------------------------------
    # Execute simulated recovery
    # --------------------------------------------------------

    recovery_attempted = False

    recovery_success = False

    recovered_amount = 0.0


    if action in ["RETRY", "SEND_REMINDER"]:

        recovery_attempted = True

        recovery_success = simulate_recovery(
            probability
        )

        if recovery_success:

            recovered_amount = payment["amount"]


    # --------------------------------------------------------
    # Store audit-style result
    # --------------------------------------------------------

    results.append(
        {
            "timestamp": datetime.now().isoformat(),

            "payment_id": payment["payment_id"],

            "amount": payment["amount"],

            "payment_method":
                payment["payment_method"],

            "failure_reason":
                payment["failure_reason"],

            "attempt_number":
                payment["attempt_number"],

            "customer_success_rate":
                payment["customer_success_rate"],

            "predicted_probability":
                probability,

            "expected_recovery":
                expected_recovery,

            "recommended_action":
                action,

            "decision_reason":
                reason,

            "workflow_stopped":
                stopped,

            "recovery_attempted":
                recovery_attempted,

            "recovery_success":
                recovery_success,

            "recovered_amount":
                recovered_amount,

            "environment":
                "SIMULATION",
        }
    )


# ============================================================
# CREATE RESULTS DATASET
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# BATCH METRICS
# ============================================================

total_failed_payments = len(results_df)

total_revenue_at_risk = (
    results_df["amount"].sum()
)

recovery_attempts = (
    results_df["recovery_attempted"] == True
).sum()

successful_recoveries = (
    results_df["recovery_success"] == True
).sum()

stopped_workflows = (
    results_df["workflow_stopped"] == True
).sum()

money_recovered = (
    results_df["recovered_amount"].sum()
)


if recovery_attempts > 0:

    recovery_success_rate = (
        successful_recoveries
        / recovery_attempts
    ) * 100

else:

    recovery_success_rate = 0


if total_revenue_at_risk > 0:

    revenue_recovery_rate = (
        money_recovered
        / total_revenue_at_risk
    ) * 100

else:

    revenue_recovery_rate = 0


# ============================================================
# ACTION BREAKDOWN
# ============================================================

action_counts = (
    results_df[
        "recommended_action"
    ]
    .value_counts()
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()

print("BATCH RECOVERY RESULTS")
print("-" * 70)

print(
    f"Failed payments analyzed       : "
    f"{total_failed_payments:,}"
)

print(
    f"Total revenue at risk          : "
    f"Rs. {total_revenue_at_risk:,.2f}"
)

print(
    f"Recovery workflows executed    : "
    f"{recovery_attempts:,}"
)

print(
    f"Successful recoveries          : "
    f"{successful_recoveries:,}"
)

print(
    f"Workflows safely stopped       : "
    f"{stopped_workflows:,}"
)

print()

print(
    f"Money recovered (simulation)   : "
    f"Rs. {money_recovered:,.2f}"
)

print(
    f"Recovery success rate          : "
    f"{recovery_success_rate:.2f}%"
)

print(
    f"Revenue recovery rate          : "
    f"{revenue_recovery_rate:.2f}%"
)

print()

print("ACTION BREAKDOWN")
print("-" * 70)

for action, count in action_counts.items():

    print(
        f"{action:<20} : {count:,}"
    )


print()

print("STOPPING RULES")
print("-" * 70)

print(
    f"Maximum automated attempts     : "
    f"{MAX_RECOVERY_ATTEMPTS}"
)

print(
    "Fraud suspected payments       : "
    "ESCALATE"
)

print(
    "Low confidence payments        : "
    "DO_NOT_ACT"
)


print()

print("OUTPUT")
print("-" * 70)

print(
    f"Batch results saved to:"
)

print(
    OUTPUT_PATH
)


print()
print("=" * 70)

print(
    "SIMULATION COMPLETE — "
    "NO REAL PAYMENTS WERE PROCESSED"
)

print("=" * 70)
print()