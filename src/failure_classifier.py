"""Loads failure_model.pkl and classifies why a transaction failed."""

from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "failure_model.pkl"

FEATURES = [
    "payment_method", "bank", "card_type", "device_type",
    "amount", "hour_of_day", "day_of_week", "is_weekend",
    "customer_tenure_days", "prior_failed_attempts_30d",
    "network_latency_ms", "retry_attempt_number",
]


class FailureClassifier:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model = joblib.load(model_path)

    def predict(self, transaction: dict) -> dict:
        """transaction: dict with keys matching FEATURES."""
        row = pd.DataFrame([{k: transaction.get(k) for k in FEATURES}])
        pred = self.model.predict(row)[0]
        proba = self.model.predict_proba(row)[0]
        classes = self.model.classes_
        confidence = float(max(proba))
        return {
            "failure_reason": pred,
            "confidence": round(confidence, 4),
            "all_probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
        }


if __name__ == "__main__":
    clf = FailureClassifier()
    sample = {
        "payment_method": "card", "bank": "YES", "card_type": "credit",
        "device_type": "mobile", "amount": 4500, "hour_of_day": 2,
        "day_of_week": 5, "is_weekend": 1, "customer_tenure_days": 40,
        "prior_failed_attempts_30d": 2, "network_latency_ms": 260,
        "retry_attempt_number": 1,
    }
    print(clf.predict(sample))
