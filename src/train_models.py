"""
Train two models and save them as .pkl:

1. failure_model.pkl        -> multiclass classifier predicting failure_reason
                                (trained only on rows where failed == 1)
2. retry_success_model.pkl  -> binary classifier predicting whether a retry
                                on a failed transaction will succeed

Leakage safeguards baked into this script:
  - Uses the pre-made customer-level train/test CSVs (transactions_train.csv /
    transactions_test.csv) produced by generate_data.py, so no customer's
    rows appear in both splits.
  - All preprocessing objects (OneHotEncoder, scaler) are FIT ONLY on the
    training split, then used to TRANSFORM the test split. Never fit on
    combined data.
  - failure_model is never given `retry_success` or `failed` as a feature.
  - retry_success_model is never given the true `failure_reason` label as a
    raw leak-prone passthrough beyond what a real system would know at
    retry-decision time (it's a legitimate causal input here, analogous to
    a real system already knowing why the payment failed before retrying).
  - Metrics are computed ONLY on the held-out test split.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

CATEGORICAL = ["payment_method", "bank", "card_type", "device_type"]
NUMERIC = [
    "amount", "hour_of_day", "day_of_week", "is_weekend",
    "customer_tenure_days", "prior_failed_attempts_30d",
    "network_latency_ms", "retry_attempt_number",
]


def load_splits():
    train_df = pd.read_csv(DATA_DIR / "transactions_train.csv")
    test_df = pd.read_csv(DATA_DIR / "transactions_test.csv")
    return train_df, test_df


def make_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )


def train_failure_model(train_df, test_df):
    train_fail = train_df[train_df["failed"] == 1].copy()
    test_fail = test_df[test_df["failed"] == 1].copy()

    X_train, y_train = train_fail[CATEGORICAL + NUMERIC], train_fail["failure_reason"]
    X_test, y_test = test_fail[CATEGORICAL + NUMERIC], test_fail["failure_reason"]

    pipe = Pipeline([
        ("prep", make_preprocessor()),
        ("clf", RandomForestClassifier(
            n_estimators=300, max_depth=12, min_samples_leaf=3,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    acc = accuracy_score(y_test, preds)
    macro_f1 = f1_score(y_test, preds, average="macro")
    report = classification_report(y_test, preds, output_dict=True)

    joblib.dump(pipe, MODEL_DIR / "failure_model.pkl")
    with open(MODEL_DIR / "failure_model_metrics.json", "w") as f:
        json.dump({"accuracy": acc, "macro_f1": macro_f1, "report": report}, f, indent=2)

    print(f"[failure_model] test accuracy={acc:.4f}  macro_f1={macro_f1:.4f}")
    return pipe


def train_retry_model(train_df, test_df):
    train_fail = train_df[train_df["failed"] == 1].copy()
    test_fail = test_df[test_df["failed"] == 1].copy()

    features = CATEGORICAL + NUMERIC + ["failure_reason"]
    X_train, y_train = train_fail[features], train_fail["retry_success"].astype(int)
    X_test, y_test = test_fail[features], test_fail["retry_success"].astype(int)

    cat_plus_reason = CATEGORICAL + ["failure_reason"]
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_plus_reason),
            ("num", "passthrough", NUMERIC),
        ]
    )

    pipe = Pipeline([
        ("prep", preprocessor),
        ("clf", RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_leaf=5,
            class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, proba)

    joblib.dump(pipe, MODEL_DIR / "retry_success_model.pkl")
    with open(MODEL_DIR / "retry_success_model_metrics.json", "w") as f:
        json.dump({"accuracy": acc, "roc_auc": auc}, f, indent=2)

    print(f"[retry_success_model] test accuracy={acc:.4f}  roc_auc={auc:.4f}")
    return pipe


if __name__ == "__main__":
    train_df, test_df = load_splits()
    train_failure_model(train_df, test_df)
    train_retry_model(train_df, test_df)
    print(f"Models saved to {MODEL_DIR}")
