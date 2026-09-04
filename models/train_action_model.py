import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/intervention_history.csv"
MODEL_PATH = "models/action_model.joblib"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print()
print("=" * 75)
print("             RECOVERAI ACTION MODEL")
print("=" * 75)
print()

print(
    f"Intervention records: {len(df):,}"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "amount",
    "payment_method",
    "failure_reason",
    "attempt_number",
    "customer_success_rate",
    "action",
]

TARGET = "recovery_success"


X = df[FEATURES]

y = df[TARGET].astype(int)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


print()
print(
    f"Training records: {len(X_train):,}"
)

print(
    f"Testing records : {len(X_test):,}"
)


# ============================================================
# PREPROCESSING
# ============================================================

numeric_features = [
    "amount",
    "attempt_number",
    "customer_success_rate",
]

categorical_features = [
    "payment_method",
    "failure_reason",
    "action",
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
    ]
)


# ============================================================
# MODEL
# ============================================================

model = LogisticRegression(
    max_iter=1000,
    random_state=42,
)


# ============================================================
# PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ============================================================
# TRAIN
# ============================================================

print()
print("Training action-selection model...")

pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# ============================================================
# EVALUATE
# ============================================================

predictions = pipeline.predict(
    X_test
)

probabilities = pipeline.predict_proba(
    X_test
)[:, 1]


accuracy = accuracy_score(
    y_test,
    predictions,
)

roc_auc = roc_auc_score(
    y_test,
    probabilities,
)


print()
print("=" * 75)
print("                 MODEL PERFORMANCE")
print("=" * 75)

print()

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)

print()

print("Classification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Recovery Failed",
            "Recovery Successful",
        ],
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True,
)

joblib.dump(
    pipeline,
    MODEL_PATH,
)


print()
print("=" * 75)
print("MODEL SAVED")
print("=" * 75)

print()

print(
    f"Model location: {MODEL_PATH}"
)

print()