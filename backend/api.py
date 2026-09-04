from datetime import datetime, timezone
from pathlib import Path
import csv

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# ============================================================
# PROJECT PATHS
# ============================================================

# api.py is inside:
# RecoverAI/backend/api.py
#
# BASE_DIR becomes:
# RecoverAI/

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = MODELS_DIR / "action_model_v2.joblib"

PAYMENTS_FILE = DATA_DIR / "payments_with_recovery.csv"

INTERVENTION_FILE = DATA_DIR / "intervention_history.csv"

AUDIT_TRAIL_FILE = DATA_DIR / "audit_trail.csv"

RETRY_COST = 5.00
REMINDER_COST = 2.00


# ============================================================
# ENSURE DATA DIRECTORY EXISTS
# ============================================================

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

if not MODEL_PATH.exists():

    raise FileNotFoundError(
        f"\n\nMODEL FILE NOT FOUND!\n"
        f"Expected location:\n{MODEL_PATH}\n\n"
        f"Make sure this file exists:\n"
        f"RecoverAI/models/action_model_v2.joblib\n"
    )


model = joblib.load(MODEL_PATH)


print("================================================")
print("RecoverAI Model Loaded Successfully")
print(f"Model: {MODEL_PATH}")
print("================================================")


# ============================================================
# CREATE API
# ============================================================

app = FastAPI(
    title="RecoverAI API",
    description="AI-powered payment recovery decision engine.",
    version="1.1.0",
)


# ============================================================
# FRONTEND
# ============================================================

if not FRONTEND_DIR.exists():

    raise FileNotFoundError(
        f"Frontend folder not found:\n{FRONTEND_DIR}"
    )


app.mount(
    "/dashboard",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="dashboard"
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class PaymentRequest(BaseModel):

    payment_id: str

    amount: float

    payment_method: str

    failure_reason: str

    attempt_number: int

    customer_success_rate: float


# ============================================================
# AUDIT TRAIL CONFIGURATION
# ============================================================

AUDIT_COLUMNS = [
    "timestamp",
    "payment_id",
    "amount",
    "payment_method",
    "failure_reason",
    "attempt_number",
    "customer_success_rate",
    "recommended_action",
    "recovery_probability",
    "expected_recovery",
    "expected_net_recovery",
    "guardrail",
    "reason",
]


# ============================================================
# SAVE AUDIT RECORD
# ============================================================

def save_audit_record(
    payment: PaymentRequest,
    decision: dict,
    timestamp: str,
):

    audit_record = {
        "timestamp": timestamp,
        "payment_id": payment.payment_id,
        "amount": float(payment.amount),
        "payment_method": payment.payment_method,
        "failure_reason": payment.failure_reason,
        "attempt_number": int(payment.attempt_number),
        "customer_success_rate": float(
            payment.customer_success_rate
        ),
        "recommended_action": decision.get(
            "recommended_action",
            "UNKNOWN"
        ),
        "recovery_probability": float(
            decision.get(
                "recovery_probability",
                0
            )
        ),
        "expected_recovery": float(
            decision.get(
                "expected_recovery",
                0
            )
        ),
        "expected_net_recovery": float(
            decision.get(
                "expected_net_recovery",
                0
            )
        ),
        "guardrail": decision.get(
            "guardrail"
        ) or "",
        "reason": decision.get(
            "reason",
            ""
        ),
    }


    file_exists = AUDIT_TRAIL_FILE.exists()


    with open(
        AUDIT_TRAIL_FILE,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=AUDIT_COLUMNS
        )


        if not file_exists:

            writer.writeheader()


        writer.writerow(audit_record)


# ============================================================
# GET POSITIVE CLASS PROBABILITY
# ============================================================

def get_positive_probability(candidate_df):

    probabilities = model.predict_proba(candidate_df)[0]


    # Find probability for class 1

    if hasattr(model, "classes_"):

        classes = list(model.classes_)

        if 1 in classes:

            index = classes.index(1)

            return float(
                probabilities[index]
            )


    # Default fallback

    if len(probabilities) > 1:

        return float(
            probabilities[1]
        )


    return float(
        probabilities[0]
    )


# ============================================================
# ACTION PREDICTION
# ============================================================

def predict_action(
    payment: PaymentRequest,
    action: str,
):

    candidate = {

        "amount":
            payment.amount,

        "payment_method":
            payment.payment_method,

        "failure_reason":
            payment.failure_reason,

        "attempt_number":
            payment.attempt_number,

        "customer_success_rate":
            payment.customer_success_rate,

        "action":
            action,

    }


    candidate_df = pd.DataFrame(
        [candidate]
    )


    probability = get_positive_probability(
        candidate_df
    )


    # --------------------------------------------------------
    # ACTION COST
    # --------------------------------------------------------

    if action == "RETRY":

        cost = RETRY_COST


    elif action == "SEND_REMINDER":

        cost = REMINDER_COST


    else:

        cost = 0.00


    # --------------------------------------------------------
    # EXPECTED RECOVERY
    # --------------------------------------------------------

    expected_revenue = (
        payment.amount
        * probability
    )


    expected_net = (
        expected_revenue
        - cost
    )


    return {

        "action":
            action,

        "probability":
            float(probability),

        "expected_revenue":
            float(expected_revenue),

        "cost":
            float(cost),

        "expected_net":
            float(expected_net),

    }


# ============================================================
# MAIN DECISION ENGINE
# ============================================================

def make_decision(
    payment: PaymentRequest
):


    # --------------------------------------------------------
    # FRAUD GUARDRAIL
    # --------------------------------------------------------

    if payment.failure_reason == "FRAUD_SUSPECTED":

        return {

            "recommended_action":
                "ESCALATE",

            "reason":
                "Fraud-related payment requires manual review.",

            "recovery_probability":
                0.0,

            "expected_recovery":
                0.0,

            "expected_net_recovery":
                0.0,

            "alternatives":
                [],

            "guardrail":
                "FRAUD_PROTECTION",

        }


    # --------------------------------------------------------
    # RETRY LIMIT
    # --------------------------------------------------------

    if payment.attempt_number >= 4:

        return {

            "recommended_action":
                "ESCALATE",

            "reason":
                "Maximum retry threshold reached.",

            "recovery_probability":
                0.0,

            "expected_recovery":
                0.0,

            "expected_net_recovery":
                0.0,

            "alternatives":
                [],

            "guardrail":
                "RETRY_LIMIT",

        }


    # --------------------------------------------------------
    # SCORE RETRY
    # --------------------------------------------------------

    retry = predict_action(
        payment,
        "RETRY",
    )


    # --------------------------------------------------------
    # SCORE SEND REMINDER
    # --------------------------------------------------------

    reminder = predict_action(
        payment,
        "SEND_REMINDER",
    )


    # --------------------------------------------------------
    # SELECT BEST ACTION
    # --------------------------------------------------------

    best = max(
        [retry, reminder],
        key=lambda x: x["expected_net"],
    )


    # --------------------------------------------------------
    # NO ACTION THRESHOLD
    # --------------------------------------------------------

    if best["expected_net"] <= 0:

        return {

            "recommended_action":
                "DO_NOT_ACT",

            "reason":
                "Expected net recovery is not positive.",

            "recovery_probability":
                float(
                    best["probability"]
                ),

            "expected_recovery":
                float(
                    max(
                        best["expected_revenue"],
                        0,
                    )
                ),

            "expected_net_recovery":
                float(
                    best["expected_net"]
                ),

            "alternatives": [
                retry,
                reminder,
            ],

            "guardrail":
                "NEGATIVE_EXPECTED_VALUE",

        }


    # --------------------------------------------------------
    # RETURN BEST DECISION
    # --------------------------------------------------------

    return {

        "recommended_action":
            best["action"],

        "reason":
            "Selected action with highest expected net recovery.",

        "recovery_probability":
            float(
                best["probability"]
            ),

        "expected_recovery":
            float(
                best["expected_revenue"]
            ),

        "expected_net_recovery":
            float(
                best["expected_net"]
            ),

        "alternatives": [
            retry,
            reminder,
        ],

        "guardrail":
            None,

    }


# ============================================================
# ANALYZE PAYMENT ENDPOINT
# ============================================================

@app.post("/analyze-payment")
def analyze_payment(
    payment: PaymentRequest
):


    # Make AI decision

    decision = make_decision(
        payment
    )


    # Create timestamp

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()


    # --------------------------------------------------------
    # SAVE AUDIT RECORD
    # --------------------------------------------------------

    try:

        save_audit_record(
            payment,
            decision,
            timestamp,
        )

    except Exception as error:

        print(
            f"WARNING: Could not save audit record: {error}"
        )


    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    response = {

        "timestamp":
            timestamp,

        "payment_id":
            payment.payment_id,

        "amount":
            payment.amount,

        "failure_reason":
            payment.failure_reason,

        "decision":
            decision,

        "simulation":
            True,

    }


    return response


# ============================================================
# AUDIT TRAIL ENDPOINT
# ============================================================

@app.get("/audit-trail")
def get_audit_trail(
    limit: int = 50
):


    # Prevent unreasonable limits

    limit = max(
        1,
        min(limit, 500)
    )


    # If no audit records exist yet

    if not AUDIT_TRAIL_FILE.exists():

        return {

            "total_records":
                0,

            "records":
                [],

            "simulation":
                True,

        }


    try:

        data = pd.read_csv(
            AUDIT_TRAIL_FILE
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not read audit trail: "
                f"{error}"
            )
        )


    # Handle empty file

    if data.empty:

        return {

            "total_records":
                0,

            "records":
                [],

            "simulation":
                True,

        }


    # Replace NaN values

    data = data.fillna("")


    # Sort newest first

    if "timestamp" in data.columns:

        data = data.sort_values(
            by="timestamp",
            ascending=False
        )


    # Get total before limiting

    total_records = len(data)


    # Limit results

    data = data.head(limit)


    return {

        "total_records":
            int(total_records),

        "records":
            data.to_dict(
                orient="records"
            ),

        "simulation":
            True,

    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "RecoverAI",

        "simulation":
            True,

        "model_loaded":
            True,

    }


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard-summary")
def dashboard_summary():

    if not PAYMENTS_FILE.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                f"Payments data file not found: "
                f"{PAYMENTS_FILE}"
            )
        )


    data = pd.read_csv(
        PAYMENTS_FILE
    )


    # --------------------------------------------------------
    # FAILED PAYMENTS
    # --------------------------------------------------------

    failed = data[
        data["status"] == "FAILED"
    ].copy()


    # --------------------------------------------------------
    # REVENUE AT RISK
    # --------------------------------------------------------

    revenue_at_risk = float(
        failed["amount"].sum()
    )


    # --------------------------------------------------------
    # POTENTIALLY RECOVERABLE
    # --------------------------------------------------------

    recoverable_reasons = [

        "BANK_ERROR",

        "NETWORK_ERROR",

        "TIMEOUT",

        "USER_CANCELLED",

    ]


    recoverable = failed[
        failed["failure_reason"].isin(
            recoverable_reasons
        )
    ]


    potentially_recoverable = float(
        recoverable["amount"].sum()
    )


    # --------------------------------------------------------
    # SUCCESSFUL RECOVERIES
    # --------------------------------------------------------

    successful = failed[
        failed["recovery_success"] == 1
    ]


    recovered_value = float(
        successful["amount"].sum()
    )


    # --------------------------------------------------------
    # RECOVERY RATE
    # --------------------------------------------------------

    recovery_rate = (

        len(successful)
        / len(failed)

        if len(failed) > 0

        else 0

    )


    # --------------------------------------------------------
    # RETURN DASHBOARD DATA
    # --------------------------------------------------------

    return {

        "failed_payments":
            int(len(failed)),

        "revenue_at_risk":
            revenue_at_risk,

        "potentially_recoverable":
            potentially_recoverable,

        "successful_recoveries":
            int(len(successful)),

        "recovered_value":
            recovered_value,

        "recovery_rate":
            float(recovery_rate),

        "model_accuracy":
            0.7106,

        "model_roc_auc":
            0.7492,

        "best_action_accuracy":
            0.7150,

        "simulation":
            True,

    }


# ============================================================
# RECOVERY ANALYTICS
# ============================================================

@app.get("/recovery-analytics")
def recovery_analytics():

    if not INTERVENTION_FILE.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                f"Intervention history file not found: "
                f"{INTERVENTION_FILE}"
            )
        )


    data = pd.read_csv(
        INTERVENTION_FILE
    )


    # --------------------------------------------------------
    # CALCULATE RECOVERED AMOUNT
    # --------------------------------------------------------

    data["recovered_amount"] = (

        data["amount"]
        * data["recovery_success"]

    )


    # --------------------------------------------------------
    # OVERALL ACTION PERFORMANCE
    # --------------------------------------------------------

    action_summary = (

        data

        .groupby("action")

        .agg(

            attempts=(
                "recovery_success",
                "count"
            ),

            successes=(
                "recovery_success",
                "sum"
            ),

            recovery_rate=(
                "recovery_success",
                "mean"
            ),

            recovered_value=(
                "recovered_amount",
                "sum"
            ),

        )

        .reset_index()

    )


    # --------------------------------------------------------
    # CLEAN DATA TYPES
    # --------------------------------------------------------

    action_summary["attempts"] = (
        action_summary["attempts"]
        .astype(int)
    )


    action_summary["successes"] = (
        action_summary["successes"]
        .astype(int)
    )


    action_summary["recovery_rate"] = (
        action_summary["recovery_rate"]
        .astype(float)
    )


    action_summary["recovered_value"] = (
        action_summary["recovered_value"]
        .astype(float)
    )


    # --------------------------------------------------------
    # FAILURE REASON PERFORMANCE
    # --------------------------------------------------------

    failure_summary = (

        data

        .groupby(
            [
                "failure_reason",
                "action",
            ]
        )

        .agg(

            attempts=(
                "recovery_success",
                "count"
            ),

            successes=(
                "recovery_success",
                "sum"
            ),

            recovery_rate=(
                "recovery_success",
                "mean"
            ),

        )

        .reset_index()

    )


    # --------------------------------------------------------
    # CLEAN FAILURE DATA TYPES
    # --------------------------------------------------------

    failure_summary["attempts"] = (
        failure_summary["attempts"]
        .astype(int)
    )


    failure_summary["successes"] = (
        failure_summary["successes"]
        .astype(int)
    )


    failure_summary["recovery_rate"] = (
        failure_summary["recovery_rate"]
        .astype(float)
    )


    # --------------------------------------------------------
    # OVERALL METRICS
    # --------------------------------------------------------

    total_attempts = len(data)


    total_successes = int(
        data["recovery_success"].sum()
    )


    overall_recovery_rate = (

        total_successes
        / total_attempts

        if total_attempts > 0

        else 0

    )


    total_value = float(
        data["amount"].sum()
    )


    # --------------------------------------------------------
    # RETURN ANALYTICS
    # --------------------------------------------------------

    return {

        "total_interventions":
            int(total_attempts),

        "total_successes":
            int(total_successes),

        "overall_recovery_rate":
            float(overall_recovery_rate),

        "total_intervention_value":
            float(total_value),

        "action_performance":
            action_summary.to_dict(
                orient="records"
            ),

        "failure_performance":
            failure_summary.to_dict(
                orient="records"
            ),

        "model_accuracy":
            0.7106,

        "model_roc_auc":
            0.7492,

        "best_action_accuracy":
            0.7150,

        "simulation":
            True,

    }


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    import uvicorn


    print("================================================")
    print("Starting RecoverAI Server...")
    print("Dashboard:")
    print("http://127.0.0.1:8000/dashboard/")
    print("================================================")


    uvicorn.run(


        app,

        host="127.0.0.1",

        port=8000,

    )