import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# -----------------------------
# Configuration
# -----------------------------

NUM_PAYMENTS = 10_000

fake = Faker("en_IN")

random.seed(42)
np.random.seed(42)


# -----------------------------
# Payment configuration
# -----------------------------

PAYMENT_METHODS = [
    "UPI",
    "CARD",
    "NETBANKING",
    "WALLET"
]

FAILURE_REASONS = [
    "BANK_ERROR",
    "NETWORK_ERROR",
    "INSUFFICIENT_FUNDS",
    "CARD_EXPIRED",
    "LIMIT_EXCEEDED",
    "FRAUD_SUSPECTED",
    "USER_CANCELLED",
    "TIMEOUT"
]


# -----------------------------
# Generate payment records
# -----------------------------

payments = []

start_date = datetime.now() - timedelta(days=90)

for i in range(NUM_PAYMENTS):

    payment_id = f"pay_{i + 1:06d}"
    customer_id = f"cust_{random.randint(1, 3000):05d}"

    amount = round(
        float(np.random.lognormal(mean=7.5, sigma=0.8)),
        2
    )

    amount = max(100, min(amount, 100000))

    payment_method = random.choice(PAYMENT_METHODS)

    timestamp = start_date + timedelta(
        minutes=random.randint(0, 90 * 24 * 60)
    )

    successful = random.random() < 0.87

    if successful:

        status = "SUCCESS"
        failure_reason = None

        attempt_number = 1

    else:

        status = "FAILED"

        failure_reason = random.choices(
            FAILURE_REASONS,
            weights=[
                22,
                18,
                15,
                8,
                10,
                5,
                12,
                10
            ],
            k=1
        )[0]

        attempt_number = random.randint(1, 4)

    customer_success_rate = round(
        random.uniform(0.45, 0.99),
        3
    )

    payments.append(
        {
            "payment_id": payment_id,
            "customer_id": customer_id,
            "amount": amount,
            "currency": "INR",
            "payment_method": payment_method,
            "status": status,
            "failure_reason": failure_reason,
            "attempt_number": attempt_number,
            "customer_success_rate": customer_success_rate,
            "timestamp": timestamp
        }
    )


# -----------------------------
# Create DataFrame
# -----------------------------

df = pd.DataFrame(payments)

df = df.sort_values("timestamp")

# -----------------------------
# Save dataset
# -----------------------------

output_path = "data/payments.csv"

df.to_csv(output_path, index=False)

print("=" * 60)
print("RECOVERAI PAYMENT DATASET GENERATED")
print("=" * 60)

print(f"Total payments: {len(df):,}")
print(f"Successful payments: {(df['status'] == 'SUCCESS').sum():,}")
print(f"Failed payments: {(df['status'] == 'FAILED').sum():,}")

failed_revenue = df.loc[
    df["status"] == "FAILED",
    "amount"
].sum()

print(f"Revenue represented by failed payments: ₹{failed_revenue:,.2f}")

print()
print(f"Dataset saved to: {output_path}")
print()
print("First 5 records:")
print(df.head().to_string(index=False))  
python data\generate_payments.py
