# RecoverAI

## AI-Powered Failed Payment Recovery Decision System

RecoverAI is an AI-powered payment recovery decision platform designed to analyze failed payments and recommend the best recovery action.

The system uses machine learning, expected-value calculations, business rules, and safety guardrails to help maximize payment recovery while minimizing unnecessary intervention costs.

---

## Dashboard Preview

![RecoverAI Dashboard](screenshots/dashboard.png)

---

## Features

### AI Payment Analysis

- Predicts the probability of successful payment recovery
- Analyzes failed payment information
- Recommends the best recovery action

### Recovery Action Optimization

RecoverAI evaluates possible actions such as:

- RETRY
- SEND_REMINDER

The system selects the action with the highest expected net recovery.

### Expected Value Decision Engine

The platform considers:

- Payment amount
- Probability of recovery
- Expected recovered revenue
- Intervention cost
- Expected net recovery

### Safety Guardrails

RecoverAI includes guardrails for situations such as:

- Fraud suspected payments
- Excessive retry attempts
- Negative expected recovery value

Depending on the situation, the system can recommend escalation or avoiding unnecessary actions.

### Dashboard

The dashboard provides insights into:

- Failed payments
- Revenue at risk
- Potentially recoverable revenue
- Successful recoveries
- Recovered value
- Recovery rate
- Model performance metrics

### Recovery Analytics

The analytics system provides:

- Overall recovery performance
- Recovery action performance
- Failure reason analysis
- Recovery success rates

### Audit Trail

Every payment analysis can be recorded with:

- Payment details
- Failure reason
- Recommended action
- Recovery probability
- Expected recovery
- Expected net recovery
- Guardrail information
- Decision reason

---

# System Architecture

```text
Failed Payment
      |
      v
Payment Analyzer
      |
      v
Machine Learning Models
      |
      v
Recovery Probability Prediction
      |
      v
Action Evaluation
      |
      v
Expected Net Recovery Calculation
      |
      v
Safety Guardrails
      |
      v
Best Recovery Decision
      |
      +-------------------+
      |                   |
      v                   v
Dashboard            Audit Trail