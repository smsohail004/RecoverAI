# RecoverAI

## AI-Powered Failed Payment Recovery Decision System

RecoverAI is an AI-powered payment recovery decision platform designed to analyze failed payments and recommend optimal recovery actions.

The system combines machine learning, expected-value optimization, business rules, bounded recovery workflows, and safety guardrails to help maximize payment recovery while minimizing unnecessary intervention.

---

## Live Demo

Try RecoverAI live:

https://recoverai-production-5600.up.railway.app/

The live dashboard demonstrates how RecoverAI analyzes failed payments and recommends recovery actions using machine learning, financial decision logic, and safety guardrails.

---

## Dashboard Preview

![RecoverAI Dashboard](screenshots/dashboard.png)

---

# Features

## AI-Powered Payment Analysis

RecoverAI analyzes failed payment information to support intelligent recovery decisions.

- Predicts the probability of successful payment recovery
- Analyzes payment failure information
- Evaluates possible recovery strategies
- Recommends an appropriate recovery action

---

## Recovery Action Optimization

RecoverAI evaluates recovery actions such as:

- `RETRY`
- `SEND_REMINDER`
- `ESCALATE`
- `DO_NOT_ACT`

The system selects actions based on predicted recovery probability, financial value, and safety constraints.

---

## Expected Value Decision Engine

The decision engine evaluates multiple financial factors, including:

- Payment amount
- Probability of recovery
- Expected recovered revenue
- Intervention costs
- Expected net recovery

This helps ensure that recovery decisions are financially meaningful rather than based only on recovery probability.

---

## Safety Guardrails and Stopping Rules

RecoverAI includes bounded recovery workflows designed to prevent unnecessary or unsafe automated intervention.

Guardrails include:

- Fraud-suspected payments are escalated for review
- Maximum automated recovery attempts are limited
- Low-confidence recovery opportunities can be stopped
- Unsafe or low-value interventions can be avoided

This ensures the system does not blindly retry every failed payment.

---

# Batch Revenue Recovery Simulation

RecoverAI includes a batch recovery simulator that demonstrates the complete recovery workflow across a large set of failed payments.

The workflow follows:

```text
Detect
   ↓
Predict
   ↓
Decide
   ↓
Execute Bounded Recovery Action
   ↓
Measure Outcome
   ↓
Stop or Escalate When Required
   ↓
Audit Results
```

The simulator uses the machine learning model to predict recovery probability and applies decision rules and stopping conditions before simulating recovery outcomes.

> **Important:** All recovery outcomes and financial results in this simulation are synthetic. No real payments are processed.

## Example Batch Simulation Results

Using the current synthetic payment dataset:

| Metric | Result |
|---|---:|
| Failed payments analyzed | 1,252 |
| Total revenue at risk | ₹3,097,532.86 |
| Recovery workflows executed | 404 |
| Successful simulated recoveries | 274 |
| Workflows safely stopped | 848 |
| Simulated money recovered | ₹672,110.88 |
| Recovery success rate | 67.82% |
| Revenue recovery rate | 21.70% |

### Recovery Action Breakdown

| Action | Payments |
|---|---:|
| ESCALATE | 655 |
| SEND_REMINDER | 276 |
| DO_NOT_ACT | 193 |
| RETRY | 128 |

These results demonstrate that RecoverAI does not automatically retry every failed payment. The system uses bounded workflows, stopping rules, escalation, and selective intervention.

---

# Interactive Dashboard

The RecoverAI dashboard provides insights into:

- Failed payments
- Revenue at risk
- Potentially recoverable revenue
- Successful recoveries
- Recovered value
- Recovery rate
- Model performance metrics

---

# Recovery Analytics

The analytics system provides insights into:

- Overall recovery performance
- Recovery action performance
- Failure reason analysis
- Recovery success rates

These metrics help evaluate how effectively different recovery strategies perform.

---

# Audit Trail

Every payment analysis can be recorded in an audit trail containing:

- Payment details
- Failure reason
- Recommended action
- Recovery probability
- Expected recovery
- Expected net recovery
- Guardrail information
- Decision reason

The simulation tools also record recovery actions in a structured audit log.

This improves transparency and makes decisions easier to review.

---

# System Architecture

```text
                    Failed Payment
                          |
                          v
                  Payment Analyzer
                          |
                          v
                Machine Learning Model
                          |
                          v
            Recovery Probability Prediction
                          |
                          v
                 Financial Evaluation
                          |
                          v
                  Decision Engine
                          |
                          v
             Safety Guardrails / Rules
                          |
             +------------+------------+
             |                         |
             v                         v
      Bounded Recovery            Stop / Escalate
             |
             v
      Simulated Outcome
             |
             v
      Recovery Measurement
             |
             +------------+------------+
             |                         |
             v                         v
        Dashboard                  Audit Trail
```

---

# Technology Stack

- Python
- FastAPI
- Scikit-learn
- Pandas
- NumPy
- Machine Learning
- Expected Value Optimization
- Git and GitHub
- Railway

---

# Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/smsohail004/RecoverAI.git
cd RecoverAI
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn backend.api:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# Run Batch Recovery Simulation

To demonstrate the bounded batch recovery workflow:

```bash
python backend/simulate_recovery.py
```

The simulator will:

1. Load failed payments from the synthetic dataset
2. Use the ML model to predict recovery probability
3. Select an appropriate recovery action
4. Apply stopping rules and escalation logic
5. Simulate bounded recovery outcomes
6. Measure simulated money recovered
7. Calculate batch recovery metrics

---

# Project Scope

RecoverAI is an experimental AI and machine learning project designed for demonstrating payment recovery decision-making.

All payment recovery actions and financial outcomes are simulated.

**No real payments are processed, retried, charged, or communicated to customers.**

---

## Author

**SM Sohail**

GitHub: https://github.com/smsohail004

---

## Future Improvements

Possible future enhancements include:

- Real-time payment event processing
- More advanced recovery models
- Action-specific intervention costs
- Multi-step recovery workflows
- A/B testing of recovery strategies
- Real-time monitoring and alerting
- Model performance monitoring
- Enhanced human review workflows