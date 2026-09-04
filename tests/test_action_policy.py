from agent.action_policy import (
    choose_best_action,
)


test_cases = [

    {
        "name": "Temporary bank failure",
        "amount": 4999,
        "probability": 0.887,
        "failure_reason": "BANK_ERROR",
        "attempt_number": 1,
    },

    {
        "name": "Expired card",
        "amount": 8000,
        "probability": 0.40,
        "failure_reason": "CARD_EXPIRED",
        "attempt_number": 1,
    },

    {
        "name": "Insufficient funds",
        "amount": 3000,
        "probability": 0.45,
        "failure_reason": "INSUFFICIENT_FUNDS",
        "attempt_number": 1,
    },

    {
        "name": "Fraud suspected",
        "amount": 25000,
        "probability": 0.80,
        "failure_reason": "FRAUD_SUSPECTED",
        "attempt_number": 1,
    },

    {
        "name": "Maximum attempts",
        "amount": 5000,
        "probability": 0.80,
        "failure_reason": "BANK_ERROR",
        "attempt_number": 4,
    },
]


print()
print("=" * 75)
print("             RECOVERAI ACTION INTELLIGENCE")
print("=" * 75)


for test in test_cases:

    result = choose_best_action(
        amount=test["amount"],
        base_probability=test["probability"],
        failure_reason=test["failure_reason"],
        attempt_number=test["attempt_number"],
    )

    print()
    print(f"CASE: {test['name']}")
    print("-" * 75)

    print(
        f"Amount          : ₹{test['amount']:,.2f}"
    )

    print(
        f"Failure         : {test['failure_reason']}"
    )

    print(
        f"Base probability: {test['probability']:.2%}"
    )

    print(
        f"BEST ACTION     : {result['action']}"
    )

    print(
        f"Reason          : {result['reason']}"
    )

    if result["candidates"]:

        print()
        print("Candidate actions:")

        for action, details in result[
            "candidates"
        ].items():

            print(
                f"  {action:18}"
                f" probability="
                f"{details['probability']:.2%}"
                f" | expected net="
                f"₹{details['expected_net_recovery']:,.2f}"
            )


print()
print("=" * 75)
print("ACTION INTELLIGENCE TEST COMPLETE")
print("=" * 75)