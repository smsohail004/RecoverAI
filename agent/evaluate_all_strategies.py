import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/intervention_history.csv"
MODEL_PATH = "models/action_model.joblib"

RETRY_COST = 5.00
REMINDER_COST = 2.00


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)


print()
print("=" * 80)
print("             RECOVERAI BUSINESS EVALUATION")
print("=" * 80)

print()

print(
    f"Intervention records loaded: {len(df):,}"
)


# ============================================================
# STRATEGY 1 — DO NOTHING
# ============================================================

# One row per payment.

payments = (
    df.drop_duplicates(
        subset=["payment_id"]
    )
    .copy()
)

do_nothing_revenue = 0.0


# ============================================================
# STRATEGY 2 — ALWAYS RETRY
# ============================================================

retry_df = df[
    df["action"] == "RETRY"
].copy()


retry_success = retry_df[
    retry_df["recovery_success"] == 1
]

retry_revenue = retry_success[
    "amount"
].sum()

retry_attempts = len(retry_df)

retry_successes = len(retry_success)

retry_cost = (
    retry_attempts * RETRY_COST
)

retry_net = (
    retry_revenue - retry_cost
)


# ============================================================
# STRATEGY 3 — RULE-BASED
# ============================================================

recoverable_reasons = [
    "BANK_ERROR",
    "NETWORK_ERROR",
    "TIMEOUT",
    "USER_CANCELLED",
]


rule_df = payments[
    payments["failure_reason"].isin(
        recoverable_reasons
    )
    &
    (payments["customer_success_rate"] >= 0.75)
    &
    (payments["attempt_number"] < 4)
].copy()


# Join actual retry outcomes.

rule_retry = rule_df[
    ["payment_id"]
].merge(
    retry_df[
        [
            "payment_id",
            "recovery_success",
            "amount",
        ]
    ],
    on="payment_id",
    how="left",
)


rule_success = rule_retry[
    rule_retry["recovery_success"] == 1
]

rule_revenue = rule_success[
    "amount"
].sum()

rule_attempts = len(rule_retry)

rule_successes = len(rule_success)

rule_cost = (
    rule_attempts * RETRY_COST
)

rule_net = (
    rule_revenue - rule_cost
)


# ============================================================
# STRATEGY 4 — RECOVERAI ACTION MODEL
# ============================================================

candidate_rows = []


for _, payment in payments.iterrows():

    # --------------------------------------------------------
    # Safety rules
    # --------------------------------------------------------

    if payment["failure_reason"] == "FRAUD_SUSPECTED":

        candidate_rows.append({
            "payment_id":
                payment["payment_id"],
            "selected_action":
                "DO_NOT_ACT",
        })

        continue


    if payment["attempt_number"] >= 4:

        candidate_rows.append({
            "payment_id":
                payment["payment_id"],
            "selected_action":
                "DO_NOT_ACT",
        })

        continue


    scores = []


    # --------------------------------------------------------
    # Evaluate each action
    # --------------------------------------------------------

    for action in [
        "RETRY",
        "SEND_REMINDER",
    ]:

        candidate = payment.copy()

        candidate["action"] = action

        candidate_df = pd.DataFrame(
            [candidate]
        )

        probability = model.predict_proba(
            candidate_df
        )[0][1]


        cost = (
            RETRY_COST
            if action == "RETRY"
            else REMINDER_COST
        )


        expected_net = (
            payment["amount"]
            * probability
            - cost
        )


        scores.append({
            "action":
                action,

            "probability":
                probability,

            "expected_net":
                expected_net,
        })


    # --------------------------------------------------------
    # Select highest expected value
    # --------------------------------------------------------

    best = max(
        scores,
        key=lambda x:
            x["expected_net"],
    )


    if best["expected_net"] <= 0:

        selected_action = "DO_NOT_ACT"

    else:

        selected_action = best["action"]


    candidate_rows.append({
        "payment_id":
            payment["payment_id"],

        "selected_action":
            selected_action,
    })


ml_selection = pd.DataFrame(
    candidate_rows
)


# ============================================================
# CONNECT ML DECISIONS TO HISTORICAL OUTCOMES
# ============================================================

ml_results = ml_selection.merge(
    df[
        [
            "payment_id",
            "action",
            "recovery_success",
            "amount",
        ]
    ],
    left_on=[
        "payment_id",
        "selected_action",
    ],
    right_on=[
        "payment_id",
        "action",
    ],
    how="left",
)


# Keep only actual interventions.

ml_results = ml_results[
    ml_results["selected_action"].isin(
        [
            "RETRY",
            "SEND_REMINDER",
        ]
    )
].copy()


ml_success = ml_results[
    ml_results["recovery_success"] == 1
]

ml_revenue = ml_success[
    "amount"
].sum()

ml_attempts = len(
    ml_results
)

ml_successes = len(
    ml_success
)


# Calculate action costs.

ml_results["action_cost"] = (
    ml_results["selected_action"]
    .map({
        "RETRY": RETRY_COST,
        "SEND_REMINDER": REMINDER_COST,
    })
)

ml_cost = ml_results[
    "action_cost"
].sum()

ml_net = (
    ml_revenue - ml_cost
)


# ============================================================
# RESULTS TABLE
# ============================================================

results = pd.DataFrame([
    {
        "strategy":
            "Do Nothing",

        "attempts":
            0,

        "successes":
            0,

        "recovery_rate":
            0,

        "revenue_recovered":
            0,

        "intervention_cost":
            0,

        "net_revenue":
            0,
    },

    {
        "strategy":
            "Always Retry",

        "attempts":
            retry_attempts,

        "successes":
            retry_successes,

        "recovery_rate":
            retry_successes /
            retry_attempts,

        "revenue_recovered":
            retry_revenue,

        "intervention_cost":
            retry_cost,

        "net_revenue":
            retry_net,
    },

    {
        "strategy":
            "Rule-Based",

        "attempts":
            rule_attempts,

        "successes":
            rule_successes,

        "recovery_rate":
            rule_successes /
            rule_attempts
            if rule_attempts
            else 0,

        "revenue_recovered":
            rule_revenue,

        "intervention_cost":
            rule_cost,

        "net_revenue":
            rule_net,
    },

    {
        "strategy":
            "RecoverAI",

        "attempts":
            ml_attempts,

        "successes":
            ml_successes,

        "recovery_rate":
            ml_successes /
            ml_attempts
            if ml_attempts
            else 0,

        "revenue_recovered":
            ml_revenue,

        "intervention_cost":
            ml_cost,

        "net_revenue":
            ml_net,
    },
])


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 80)
print("                    STRATEGY COMPARISON")
print("=" * 80)

print()

for _, row in results.iterrows():

    print(
        f"{row['strategy']:15}"
        f" attempts={int(row['attempts']):4d}"
        f" | successes={int(row['successes']):4d}"
        f" | recovery="
        f"{row['recovery_rate']:.2%}"
        f" | recovered="
        f"₹{row['revenue_recovered']:,.2f}"
        f" | cost="
        f"₹{row['intervention_cost']:,.2f}"
        f" | NET="
        f"₹{row['net_revenue']:,.2f}"
    )


# ============================================================
# RECOVERAI LIFT
# ============================================================

print()
print("=" * 80)
print("                       RECOVERAI LIFT")
print("=" * 80)

print()

baseline_net = rule_net

lift = ml_net - baseline_net

if baseline_net != 0:

    lift_percentage = (
        lift /
        abs(baseline_net)
    )

else:

    lift_percentage = 0


print(
    f"Rule-Based net revenue : "
    f"₹{baseline_net:,.2f}"
)

print(
    f"RecoverAI net revenue  : "
    f"₹{ml_net:,.2f}"
)

print(
    f"Net revenue lift       : "
    f"₹{lift:,.2f}"
)

print(
    f"Relative lift          : "
    f"{lift_percentage:.2%}"
)

print()

print("=" * 80)