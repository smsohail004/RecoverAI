import numpy as np
import pandas as pd


# -----------------------------------------
# Configuration
# -----------------------------------------

INPUT_PATH = "data/payments.csv"
OUTPUT_PATH = "data/payments_with_recovery.csv"

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)


# -----------------------------------------
# Load existing payment dataset
# -----------------------------------------

df = pd.read_csv(INPUT_PATH)


# -----------------------------------------
# Recovery probability function
# -----------------------------------------

def calculate_recovery_probability(row):
    """
    Estimate the probability that a recovery
    attempt will succeed.

    This is our synthetic ground-truth
    generation logic.

    Later, the ML model will try to learn
    these relationships from historical data.
    """

    # Start with a neutral probability
    probability = 0.50

    failure_reason = row["failure_reason"]

    customer_success_rate = row["customer_success_rate"]

    attempt_number = row["attempt_number"]

    payment_method = row["payment_method"]

    amount = row["amount"]


    # -----------------------------------------
    # Failure reason effect
    # -----------------------------------------

    reason_effects = {
        "BANK_ERROR": 0.25,
        "NETWORK_ERROR": 0.22,
        "TIMEOUT": 0.18,
        "USER_CANCELLED": 0.10,
        "INSUFFICIENT_FUNDS": -0.05,
        "LIMIT_EXCEEDED": -0.12,
        "CARD_EXPIRED": -0.20,
        "FRAUD_SUSPECTED": -0.45,
    }

    probability += reason_effects.get(
        failure_reason,
        0
    )


    # -----------------------------------------
    # Customer history effect
    # -----------------------------------------

    # A customer with a strong payment history
    # is generally more likely to recover.

    probability += (
        customer_success_rate - 0.70
    ) * 0.60


    # -----------------------------------------
    # Attempt number effect
    # -----------------------------------------

    # Repeated failures reduce the chance
    # that another attempt will work.

    probability -= (
        attempt_number - 1
    ) * 0.08


    # -----------------------------------------
    # Payment method effect
    # -----------------------------------------

    method_effects = {
        "UPI": 0.04,
        "CARD": 0.00,
        "NETBANKING": -0.02,
        "WALLET": 0.02,
    }

    probability += method_effects.get(
        payment_method,
        0
    )


    # -----------------------------------------
    # Transaction amount effect
    # -----------------------------------------

    # Very large transactions are slightly
    # harder to recover automatically.

    if amount > 50000:
        probability -= 0.05

    elif amount > 25000:
        probability -= 0.02


    # -----------------------------------------
    # Keep probability in valid range
    # -----------------------------------------

    probability = np.clip(
        probability,
        0.02,
        0.97
    )

    return probability


# -----------------------------------------
# Calculate recovery probability
# -----------------------------------------

df["true_recovery_probability"] = np.nan

failed_mask = df["status"] == "FAILED"

df.loc[
    failed_mask,
    "true_recovery_probability"
] = df.loc[
    failed_mask
].apply(
    calculate_recovery_probability,
    axis=1
)


# -----------------------------------------
# Simulate recovery attempts
# -----------------------------------------

df["recovery_attempted"] = False

df["recovery_success"] = np.nan


# For our historical simulation, every failed
# payment receives a simulated recovery attempt.
#
# IMPORTANT:
# This is synthetic experimentation only.
# It does NOT represent a recommendation to
# automatically retry real payments.

df.loc[
    failed_mask,
    "recovery_attempted"
] = True


# -----------------------------------------
# Generate recovery outcomes
# -----------------------------------------

random_values = np.random.random(
    failed_mask.sum()
)

recovery_probabilities = df.loc[
    failed_mask,
    "true_recovery_probability"
].values


recovery_results = (
    random_values < recovery_probabilities
)


df.loc[
    failed_mask,
    "recovery_success"
] = recovery_results.astype(int)


# -----------------------------------------
# Save enriched dataset
# -----------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# -----------------------------------------
# Display results
# -----------------------------------------

failed_df = df[
    df["recovery_attempted"] == True
]

successful_recoveries = (
    failed_df["recovery_success"] == 1
).sum()

failed_recoveries = (
    failed_df["recovery_success"] == 0
).sum()

recovered_revenue = failed_df.loc[
    failed_df["recovery_success"] == 1,
    "amount"
].sum()

attempted_revenue = failed_df["amount"].sum()

recovery_rate = (
    successful_recoveries /
    len(failed_df)
) * 100


print()
print("=" * 65)
print("       RECOVERAI RECOVERY OUTCOME SIMULATOR")
print("=" * 65)

print()

print(
    f"Failed payments available : "
    f"{len(failed_df):,}"
)

print(
    f"Recovery attempts         : "
    f"{len(failed_df):,}"
)

print(
    f"Successful recoveries     : "
    f"{successful_recoveries:,}"
)

print(
    f"Unsuccessful recoveries   : "
    f"{failed_recoveries:,}"
)

print()

print(
    f"Simulated recovery rate   : "
    f"{recovery_rate:.2f}%"
)

print(
    f"Revenue attempted         : "
    f"₹{attempted_revenue:,.2f}"
)

print(
    f"Simulated revenue recovered: "
    f"₹{recovered_revenue:,.2f}"
)

print()

print(
    f"Dataset saved to: "
    f"{OUTPUT_PATH}"
)

print()

print("=" * 65)