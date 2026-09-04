import pandas as pd


# ---------------------------------
# Load payment data
# ---------------------------------

DATA_PATH = "data/payments.csv"

df = pd.read_csv(DATA_PATH)


# ---------------------------------
# Basic statistics
# ---------------------------------

total_payments = len(df)

successful_payments = (df["status"] == "SUCCESS").sum()

failed_payments = (df["status"] == "FAILED").sum()


# ---------------------------------
# Revenue calculations
# ---------------------------------

total_revenue = df["amount"].sum()

failed_df = df[df["status"] == "FAILED"].copy()

revenue_at_risk = failed_df["amount"].sum()


# ---------------------------------
# Identify potentially recoverable
# payments
# ---------------------------------

recoverable_reasons = [
    "BANK_ERROR",
    "NETWORK_ERROR",
    "TIMEOUT",
    "USER_CANCELLED"
]

recoverable_df = failed_df[
    failed_df["failure_reason"].isin(recoverable_reasons)
].copy()

potentially_recoverable = recoverable_df["amount"].sum()


# ---------------------------------
# High-priority opportunities
# ---------------------------------

high_priority_df = recoverable_df[
    recoverable_df["customer_success_rate"] >= 0.75
].copy()

high_priority_revenue = high_priority_df["amount"].sum()


# ---------------------------------
# Display results
# ---------------------------------

print()
print("=" * 65)
print("              RECOVERAI REVENUE ANALYSIS")
print("=" * 65)

print()

print(f"Total payments analyzed       : {total_payments:,}")
print(f"Successful payments           : {successful_payments:,}")
print(f"Failed payments               : {failed_payments:,}")

print()

print(f"Total payment value           : ₹{total_revenue:,.2f}")
print(f"Revenue at risk               : ₹{revenue_at_risk:,.2f}")

print()

print(
    f"Potentially recoverable       : "
    f"₹{potentially_recoverable:,.2f}"
)

print(
    f"High-priority recovery value  : "
    f"₹{high_priority_revenue:,.2f}"
)

print()

print(
    f"Recovery opportunities        : "
    f"{len(recoverable_df):,}"
)

print(
    f"High-priority opportunities   : "
    f"{len(high_priority_df):,}"
)

print()

print("=" * 65)


# ---------------------------------
# Failure breakdown
# ---------------------------------

print()
print("FAILURE BREAKDOWN")
print("-" * 65)

failure_summary = (
    failed_df
    .groupby("failure_reason")
    .agg(
        transactions=("payment_id", "count"),
        revenue=("amount", "sum")
    )
    .sort_values("revenue", ascending=False)
)

print(failure_summary.to_string())

print()