import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/payments_with_recovery.csv"
MODEL_PATH = "models/recovery_model.joblib"


# ============================================================
# LOAD DATA
# ============================================================

print()
print("=" * 70)
print("             RECOVERAI ML TRAINING")
print("=" * 70)
print()

df = pd.read_csv(INPUT_PATH)

# We only train on failed payments because successful
# payments never needed recovery.

df = df[df["status"] == "FAILED"].copy()

print(f"Failed payments available: {len(df):,}")


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
print(f"Training records: {len(X_train):,}")
print(f"Testing records : {len(X_test):,}")


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
print("Training recovery prediction model...")

pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# ============================================================
# PREDICTIONS
# ============================================================

predictions = pipeline.predict(X_test)

probabilities = pipeline.predict_proba(
    X_test
)[:, 1]


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions,
)

roc_auc = roc_auc_score(
    y_test,
    probabilities,
)

cm = confusion_matrix(
    y_test,
    predictions,
)


print()
print("=" * 70)
print("                 MODEL PERFORMANCE")
print("=" * 70)

print()

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)

print()

print("Confusion Matrix:")
print(cm)

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
print("=" * 70)
print("MODEL SAVED")
print("=" * 70)

print()
print(f"Model location: {MODEL_PATH}")
print()