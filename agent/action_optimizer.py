import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/action_model.joblib"

ACTION_COSTS = {
    "RETRY": 5.00,
    "SEND_REMINDER": 2.00,
}


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# SCORE ONE ACTION
# ============================================================

def score_action(payment, action):

    candidate = payment.copy()

    candidate["action"] = action

    candidate_df = pd.DataFrame(
        [candidate]
    )

    probability = model.predict_proba(
        candidate_df
    )[0][1]

    expected_revenue = (
        payment["amount"] * probability
    )

    cost = ACTION_COSTS[action]

    expected_net_recovery = (
        expected_revenue - cost
    )

    return {
        "action": action,
        "probability": probability,
        "expected_revenue": expected_revenue,
        "cost": cost,
        "expected_net_recovery":
            expected_net_recovery,
    }


# ============================================================
# FIND BEST ACTION
# ============================================================

def optimize_payment(payment):

    # --------------------------------------------------------
    # Hard safety rule
    # --------------------------------------------------------

    if payment["failure_reason"] == "FRAUD_SUSPECTED":

        return {
            "best_action": "ESCALATE",
            "reason":
                "Fraud-related payment requires review.",
            "scores": [],
        }


    # --------------------------------------------------------
    # Retry limit
    # --------------------------------------------------------

    if payment["attempt_number"] >= 4:

        return {
            "best_action": "ESCALATE",
            "reason":
                "Maximum retry threshold reached.",
            "scores": [],
        }


    # --------------------------------------------------------
    # Score available actions
    # --------------------------------------------------------

    scores = []

    for action in [
        "RETRY",
        "SEND_REMINDER",
    ]:

        scores.append(
            score_action(
                payment,
                action,
            )
        )


    # --------------------------------------------------------
    # Find maximum expected net recovery
    # --------------------------------------------------------

    best = max(
        scores,
        key=lambda x:
            x["expected_net_recovery"],
    )


    # --------------------------------------------------------
    # Don't act on negative value
    # --------------------------------------------------------

    if best["expected_net_recovery"] <= 0:

        best_action = "DO_NOT_ACT"

    else:

        best_action = best["action"]


    return {
        "best_action": best_action,
        "reason":
            "Selected action with the highest "
            "expected net recovery.",
        "scores": scores,
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    payment = {

        "payment_id":
            "pay_demo_003",

        "amount":
            10000.00,

        "payment_method":
            "CARD",

        "failure_reason":
            "CARD_EXPIRED",

        "attempt_number":
            1,

        "customer_success_rate":
            0.88,
    }


    result = optimize_payment(
        payment
    )


    print()
    print("=" * 75)
    print("              RECOVERAI ACTION OPTIMIZER")
    print("=" * 75)

    print()

    print(
        f"Payment             : "
        f"{payment['payment_id']}"
    )

    print(
        f"Amount              : "
        f"₹{payment['amount']:,.2f}"
    )

    print(
        f"Failure             : "
        f"{payment['failure_reason']}"
    )

    print()

    print("ACTION SCORES")
    print("-" * 75)

    for score in result["scores"]:

        print(
            f"{score['action']:18}"
            f" P(success)="
            f"{score['probability']:.2%}"
            f" | expected revenue="
            f"₹{score['expected_revenue']:,.2f}"
            f" | cost="
            f"₹{score['cost']:,.2f}"
            f" | net="
            f"₹{score['expected_net_recovery']:,.2f}"
        )

    print()

    print(
        f"BEST ACTION        : "
        f"{result['best_action']}"
    )

    print(
        f"REASON             : "
        f"{result['reason']}"
    )

    print()

    print("=" * 75)