# ============================================================
# RECOVERAI ACTION POLICY
# ============================================================

ACTION_COSTS = {
    "RETRY": 5.00,
    "SEND_REMINDER": 2.00,
    "ESCALATE": 15.00,
    "DO_NOT_ACT": 0.00,
}


def estimate_action_probability(
    base_probability,
    failure_reason,
    action,
):
    """
    Estimate action-specific recovery probability.

    IMPORTANT:
    These are prototype policy assumptions.
    They are NOT learned causal probabilities.
    """

    probability = base_probability

    # --------------------------------------------------------
    # Retry
    # --------------------------------------------------------

    if action == "RETRY":

        if failure_reason in [
            "BANK_ERROR",
            "NETWORK_ERROR",
            "TIMEOUT",
        ]:
            probability += 0.05

        elif failure_reason in [
            "CARD_EXPIRED",
            "LIMIT_EXCEEDED",
        ]:
            probability -= 0.25

        elif failure_reason == "FRAUD_SUSPECTED":
            probability = 0.0

    # --------------------------------------------------------
    # Reminder
    # --------------------------------------------------------

    elif action == "SEND_REMINDER":

        if failure_reason in [
            "USER_CANCELLED",
            "INSUFFICIENT_FUNDS",
            "CARD_EXPIRED",
        ]:
            probability += 0.10

        elif failure_reason in [
            "BANK_ERROR",
            "NETWORK_ERROR",
        ]:
            probability -= 0.10

        elif failure_reason == "FRAUD_SUSPECTED":
            probability = 0.0

    # --------------------------------------------------------
    # Escalation
    # --------------------------------------------------------

    elif action == "ESCALATE":

        # Escalation doesn't automatically recover
        # revenue in our simulation.
        probability = 0.05

    # --------------------------------------------------------
    # No action
    # --------------------------------------------------------

    elif action == "DO_NOT_ACT":

        probability = 0.0

    return max(
        0.0,
        min(probability, 0.99)
    )


def calculate_expected_net_recovery(
    amount,
    probability,
    action,
):
    """
    Expected recovered revenue minus
    estimated intervention cost.
    """

    expected_revenue = (
        amount * probability
    )

    cost = ACTION_COSTS[action]

    return expected_revenue - cost


def choose_best_action(
    amount,
    base_probability,
    failure_reason,
    attempt_number,
):
    """
    Select the best allowed recovery action.
    """

    # --------------------------------------------------------
    # Hard safety rules
    # --------------------------------------------------------

    if failure_reason == "FRAUD_SUSPECTED":

        return {
            "action": "ESCALATE",
            "reason": "Fraud-related payment requires review.",
            "candidates": {},
        }

    if attempt_number >= 4:

        return {
            "action": "ESCALATE",
            "reason": "Maximum retry threshold reached.",
            "candidates": {},
        }

    # --------------------------------------------------------
    # Candidate actions
    # --------------------------------------------------------

    actions = [
        "RETRY",
        "SEND_REMINDER",
        "DO_NOT_ACT",
    ]

    candidates = {}

    for action in actions:

        probability = estimate_action_probability(
            base_probability,
            failure_reason,
            action,
        )

        expected_net_recovery = (
            calculate_expected_net_recovery(
                amount,
                probability,
                action,
            )
        )

        candidates[action] = {
            "probability": probability,
            "expected_net_recovery":
                expected_net_recovery,
        }

    # --------------------------------------------------------
    # Select maximum expected value
    # --------------------------------------------------------

    best_action = max(
        candidates,
        key=lambda action:
            candidates[action][
                "expected_net_recovery"
            ],
    )

    # --------------------------------------------------------
    # Don't act if expected value is negative
    # --------------------------------------------------------

    if candidates[best_action][
        "expected_net_recovery"
    ] <= 0:

        best_action = "DO_NOT_ACT"

    return {
        "action": best_action,
        "reason": (
            "Selected action with the highest "
            "expected net recovery."
        ),
        "candidates": candidates,
    }