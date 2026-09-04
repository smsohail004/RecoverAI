from agent.recovery_tools import (
    retry_payment,
    send_payment_reminder,
    escalate_payment,
    do_nothing,
)


print()
print("=" * 70)
print("              RECOVERAI ACTION TOOL TEST")
print("=" * 70)


print()
print("1. RETRY")

result = retry_payment(
    "pay_test_001",
    4999.00
)

print(result)


print()
print("2. SEND REMINDER")

result = send_payment_reminder(
    "pay_test_002",
    2499.00
)

print(result)


print()
print("3. ESCALATE")

result = escalate_payment(
    "pay_test_003",
    "High risk payment"
)

print(result)


print()
print("4. DO NOT ACT")

result = do_nothing(
    "pay_test_004",
    "Low recovery probability"
)

print(result)


print()
print("=" * 70)
print("ACTION TOOL TEST COMPLETE")
print("=" * 70)