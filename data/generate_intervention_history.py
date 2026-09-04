import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/payments_with_recovery.csv"
OUTPUT_PATH = "data/intervention_history.csv"

np.random.seed(123)


# ============================================================
# LOAD FAILED PAYMENTS
# ============================================================

df = pd.read_csv(INPUT_PATH)

df = df[
    df["status"] == "FAILED"
].copy()


# ============================================================
# ACTIONS
# ============================================================

actions = [
    "RETRY",
    "SEND_REMINDER",
]


# ============================================================
# GENERATE HISTORICAL INTERVENTIONS
# ============================================================

records = []


for _, payment in df.iterrows():

    for action in actions:

        probability = 0.50

        reason = payment[
            "failure_reason"
        ]

        customer_rate = payment[
            "customer_success_rate"
        ]

        attempts = payment[
            "attempt_number"
        ]


        # ----------------------------------------------------
        # Failure-specific effects
        # ----------------------------------------------------

        if action == "RETRY":

            if reason == "BANK_ERROR":
                probability += 0.25

            elif reason == "NETWORK_ERROR":
                probability += 0.22

            elif reason == "TIMEOUT":
                probability += 0.18

            elif reason == "USER_CANCELLED":
                probability += 0.05

            elif reason == "INSUFFICIENT_FUNDS":
                probability -= 0.15

            elif reason == "LIMIT_EXCEEDED":
                probability -= 0.20

            elif reason == "CARD_EXPIRED":
                probability -= 0.30

            elif reason == "FRAUD_SUSPECTED":
                probability = 0.01


        elif action == "SEND_REMINDER":

            if reason == "USER_CANCELLED":
                probability += 0.18

            elif reason == "INSUFFICIENT_FUNDS":
                probability += 0.15

            elif reason == "CARD_EXPIRED":
                probability += 0.22

            elif reason == "LIMIT_EXCEEDED":
                probability += 0.10

            elif reason == "BANK_ERROR":
                probability -= 0.08

            elif reason == "NETWORK_ERROR":
                probability -= 0.05

            elif reason == "TIMEOUT":
                probability -= 0.05

            elif reason == "FRAUD_SUSPECTED":
                probability = 0.01


        # ----------------------------------------------------
        # Customer history
        # ----------------------------------------------------

        probability += (
            customer_rate - 0.70
        ) * 0.50


        # ----------------------------------------------------
        # Repeated attempts
        # ----------------------------------------------------

        probability -= (
            attempts - 1
        ) * 0.07


        # ----------------------------------------------------
        # Clamp probability
        # ----------------------------------------------------

        probability = np.clip(
            probability,
            0.01,
            0.97
        )


        # ----------------------------------------------------
        # Generate outcome
        # ----------------------------------------------------

        outcome = int(
            np.random.random() < probability
        )


        records.append({

            "payment_id":
                payment["payment_id"],

            "amount":
                payment["amount"],

            "payment_method":
                payment["payment_method"],

            "failure_reason":
                reason,

            "attempt_number":
                attempts,

            "customer_success_rate":
                customer_rate,

            "action":
                action,

            "recovery_success":
                outcome,

            "simulated_probability":
                probability,
        })


# ============================================================
# CREATE DATAFRAME
# ============================================================

history = pd.DataFrame(
    records
)


# ============================================================
# SAVE
# ============================================================

history.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 75)
print("          RECOVERAI INTERVENTION HISTORY")
print("=" * 75)

print()

print(
    f"Failed payments          : "
    f"{len(df):,}"
)

print(
    f"Intervention records     : "
    f"{len(history):,}"
)

print()

print("Action distribution:")

print(
    history["action"]
    .value_counts()
    .to_string()
)

print()

print("Recovery rate by action:")

rates = (
    history
    .groupby("action")[
        "recovery_success"
    ]
    .mean()
    .sort_values(
        ascending=False
    )
)

for action, rate in rates.items():

    print(
        f"  {action:20}"
        f"{rate:.2%}"
    )

print()

print(
    f"Dataset saved to: "
    f"{OUTPUT_PATH}"
)

print()

print("=" * 75)