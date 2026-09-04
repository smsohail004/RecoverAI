import joblib
import pandas as pd

from agent.action_policy import choose_best_action
from agent.recovery_tools import (
    retry_payment,
    send_payment_reminder,
    escalate_payment,
    do_nothing,
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/recovery_model.joblib"


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "amount",
    "payment_method",
    "failure_reason",
    "attempt_number",
    "customer_success_rate",
]


# ============================================================
# CORE RECOVERAI ENGINE
# ============================================================

def analyze_payment(payment):

    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    payment_df = pd.DataFrame([payment])

    probability = model.predict_proba(
        payment_df
    )[0][1]


    # --------------------------------------------------------
    # Action optimization
    # --------------------------------------------------------

    decision = choose_best_action(
        amount=payment["amount"],
        base_probability=probability,
        failure_reason=payment["failure_reason"],
        attempt_number=payment["attempt_number"],
    )


    action = decision["action"]


    # --------------------------------------------------------
    # Execute bounded action
    # --------------------------------------------------------

    if action == "RETRY":

        tool_result = retry_payment(
            payment["payment_id"],
            payment["amount"],
        )

    elif action == "SEND_REMINDER":

        tool_result = send_payment_reminder(
            payment["payment_id"],
            payment["amount"],
        )

    elif action == "ESCALATE":

        tool_result = escalate_payment(
            payment["payment_id"],
            decision["reason"],
        )

    else:

        tool_result = do_nothing(
            payment["payment_id"],
            decision["reason"],
        )


    # --------------------------------------------------------
    # Expected recovery
    # --------------------------------------------------------

    expected_recovery = (
        payment["amount"] * probability
    )


    # --------------------------------------------------------
    # Return complete decision
    # --------------------------------------------------------

    return {

        "payment_id":
            payment["payment_id"],

        "amount":
            payment["amount"],

        "failure_reason":
            payment["failure_reason"],

        "recovery_probability":
            probability,

        "expected_recovery":
            expected_recovery,

        "recommended_action":
            action,

        "reason":
            decision["reason"],

        "action_candidates":
            decision["candidates"],

        "tool_result":
            tool_result,
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    demo_payment = {

        "payment_id":
            "pay_demo_002",

        "amount":
            7500.00,

        "payment_method":
            "CARD",

        "failure_reason":
            "CARD_EXPIRED",

        "attempt_number":
            1,

        "customer_success_rate":
            0.88,
    }


    result = analyze_payment(
        demo_payment
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print()

    print("=" * 75)
    print("                    RECOVERAI CORE")
    print("=" * 75)

    print()

    print(
        f"Payment ID            : "
        f"{result['payment_id']}"
    )

    print(
        f"Amount                : "
        f"₹{result['amount']:,.2f}"
    )

    print(
        f"Failure reason        : "
        f"{result['failure_reason']}"
    )

    print()

    print(
        f"Recovery probability  : "
        f"{result['recovery_probability']:.2%}"
    )

    print(
        f"Expected recovery     : "
        f"₹{result['expected_recovery']:,.2f}"
    )

    print()

    print(
        f"RECOMMENDED ACTION    : "
        f"{result['recommended_action']}"
    )

    print(
        f"Reason                : "
        f"{result['reason']}"
    )

    print()

    print("ACTION ANALYSIS")
    print("-" * 75)

    for action, details in result[
        "action_candidates"
    ].items():

        print(
            f"{action:20}"
            f" probability="
            f"{details['probability']:.2%}"
            f" | expected net="
            f"₹{details['expected_net_recovery']:,.2f}"
        )

    print()

    print("EXECUTION RESULT")
    print("-" * 75)

    print(
        result["tool_result"]
    )

    print()

    print("=" * 75)