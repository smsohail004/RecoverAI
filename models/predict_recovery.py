import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/recovery_model.joblib"


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# EXAMPLE PAYMENT
# ============================================================

payment = {
    "amount": 4999.00,
    "payment_method": "UPI",
    "failure_reason": "BANK_ERROR",
    "attempt_number": 1,
    "customer_success_rate": 0.91,
}


# Convert the payment into a DataFrame.

payment_df = pd.DataFrame([payment])


# ============================================================
# PREDICT RECOVERY PROBABILITY
# ============================================================

recovery_probability = model.predict_proba(
    payment_df
)[0][1]


# ============================================================
# EXPECTED RECOVERY VALUE
# ============================================================

expected_recovery = (
    payment["amount"] *
    recovery_probability
)


# ============================================================
# PRIORITY
# ============================================================

if recovery_probability >= 0.75:
    priority = "HIGH"

elif recovery_probability >= 0.50:
    priority = "MEDIUM"

else:
    priority = "LOW"


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 65)
print("                 RECOVERAI PREDICTION")
print("=" * 65)

print()

print(
    f"Payment amount          : "
    f"₹{payment['amount']:,.2f}"
)

print(
    f"Payment method          : "
    f"{payment['payment_method']}"
)

print(
    f"Failure reason          : "
    f"{payment['failure_reason']}"
)

print(
    f"Attempt number          : "
    f"{payment['attempt_number']}"
)

print(
    f"Customer success rate   : "
    f"{payment['customer_success_rate']:.0%}"
)

print()

print("-" * 65)

print(
    f"Recovery probability    : "
    f"{recovery_probability:.2%}"
)

print(
    f"Expected recovery value : "
    f"₹{expected_recovery:,.2f}"
)

print(
    f"Priority                : "
    f"{priority}"
)

print()

print("=" * 65)