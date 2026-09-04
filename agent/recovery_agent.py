
import joblib
import pandas as pd

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

model = joblib.load(MODEL_PATH)


# ============================================================
# AGENT
# ============================================================

def analyze_payment(payment):

    # --------------------------------------------------------
    # Prepare payment for ML model
    # --------------------------------------------------------

    payment_df = pd.DataFrame([payment])

    probability = model.predict_proba(
        payment_df
    )[0][1]

    amount = payment["amount"]

    failure_reason = payment["failure_reason"]

    attempt_number = payment["attempt_number"]

    # --------------------------------------------------------
    # Expected recovery
    # --------------------------------------------------------

    expected_recovery = (
        amount * probability
    )

    # --------------------------------------------------------
    # Decision + guardrails
    # --------------------------------------------------------

    if failure_reason == "FRAUD_SUSPECTED":

        action = "ESCALATE"

        reason = (
            "Fraud-related failure requires human review."
        )

    elif attempt_number >= 4:

        action = "ESCALATE"

        reason = (
            "Maximum retry threshold reached."
        )

    elif probability >= 0.75:

        action = "RECOVER"

        reason = (
            "High predicted recovery probability."
        )

    elif probability >= 0.50:

        action = "REVIEW"

        reason = (
            "Moderate recovery probability."
        )

    else:

        action = "DO_NOT_ACT"

        reason = (
            "Low predicted recovery probability."
        )

    # --------------------------------------------------------
    # Execute bounded action
    # --------------------------------------------------------

    if action == "RECOVER":

        tool_result = retry_payment(
            payment["payment_id"],
            amount
        )

    elif action == "REVIEW":

        tool_result = send_payment_reminder(
            payment["payment_id"],
            amount
        )

    elif action == "ESCALATE":

        tool_result = escalate_payment(
            payment["payment_id"],
            reason
        )

    else:

        tool_result = do_nothing(
            payment["payment_id"],
            reason
        )

    # --------------------------------------------------------
    # Return complete decision
    # --------------------------------------------------------

    return {
        "probability": probability,
        "expected_recovery": expected_recovery,
        "action": action,
        "reason": reason,
        "tool_result": tool_result,
    }


# ============================================================
# DEMO PAYMENT
# ============================================================

test_payment = {
    "payment_id": "pay_demo_001",
    "amount": 4999.00,
    "payment_method": "UPI",
    "failure_reason": "BANK_ERROR",
    "attempt_number": 1,
    "customer_success_rate": 0.91,
}


# ============================================================
# RUN AGENT
# ============================================================

result = analyze_payment(
    test_payment
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()

print("=" * 70)
print("              RECOVERAI AUTONOMOUS AGENT")
print("=" * 70)

print()

print(
    f"Payment ID           : "
    f"{test_payment['payment_id']}"
)

print(
    f"Amount               : "
    f"₹{test_payment['amount']:,.2f}"
)

print(
    f"Failure              : "
    f"{test_payment['failure_reason']}"
)

print(
    f"Attempt number       : "
    f"{test_payment['attempt_number']}"
)

print()

print("-" * 70)

print(
    f"Recovery probability : "
    f"{result['probability']:.2%}"
)

print(
    f"Expected recovery    : "
    f"₹{result['expected_recovery']:,.2f}"
)

print(
    f"Decision             : "
    f"{result['action']}"
)

print(
    f"Reason               : "
    f"{result['reason']}"
)

print()

print("TOOL RESULT")
print("-" * 70)

print(
    result["tool_result"]
)

print()

print("=" * 70)