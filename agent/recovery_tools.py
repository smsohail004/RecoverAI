from datetime import datetime
import json
import os
import random


AUDIT_PATH = "data/audit_log.jsonl"


# ============================================================
# AUDIT LOGGER
# ============================================================

def write_audit_event(event):
    """
    Store one immutable-style audit event.

    JSONL means each line is one independent JSON record.
    """

    os.makedirs("data", exist_ok=True)

    with open(
        AUDIT_PATH,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(event)
            + "\n"
        )


# ============================================================
# RETRY PAYMENT
# ============================================================

def retry_payment(payment_id, amount):
    """
    Simulate a payment retry.

    This is ONLY a simulation.
    No real payment is processed.
    """

    success = random.random() < 0.80

    result = (
        "SUCCESS"
        if success
        else "FAILED"
    )

    event = {
        "timestamp": datetime.now().isoformat(),
        "payment_id": payment_id,
        "action": "RETRY",
        "amount": amount,
        "result": result,
        "environment": "SIMULATION",
    }

    write_audit_event(event)

    return event


# ============================================================
# SEND PAYMENT REMINDER
# ============================================================

def send_payment_reminder(
    payment_id,
    amount
):
    """
    Simulate sending a payment reminder.

    No real customer communication occurs.
    """

    event = {
        "timestamp": datetime.now().isoformat(),
        "payment_id": payment_id,
        "action": "SEND_REMINDER",
        "amount": amount,
        "result": "SCHEDULED",
        "environment": "SIMULATION",
    }

    write_audit_event(event)

    return event


# ============================================================
# ESCALATE
# ============================================================

def escalate_payment(
    payment_id,
    reason
):
    """
    Send the payment to human review.
    """

    event = {
        "timestamp": datetime.now().isoformat(),
        "payment_id": payment_id,
        "action": "ESCALATE",
        "reason": reason,
        "result": "REVIEW_REQUIRED",
        "environment": "SIMULATION",
    }

    write_audit_event(event)

    return event


# ============================================================
# DO NOTHING
# ============================================================

def do_nothing(
    payment_id,
    reason
):
    """
    Explicitly record that the agent decided
    not to intervene.
    """

    event = {
        "timestamp": datetime.now().isoformat(),
        "payment_id": payment_id,
        "action": "DO_NOT_ACT",
        "reason": reason,
        "result": "NO_ACTION",
        "environment": "SIMULATION",
    }

    write_audit_event(event)

    return event