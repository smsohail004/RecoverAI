import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = "data/intervention_history.csv"
MODEL_PATH = "models/action_model_v2.joblib"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print()
print("=" * 75)
print("        RECOVERAI ACTION MODEL V2 — RANDOM FOREST")
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
# SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
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
            "passthrough",
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
# RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
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
print("Training Random Forest...")

pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# ============================================================
# EVALUATION
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
# SAVE
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