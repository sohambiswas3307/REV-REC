"""
Loads retry_success_model.pkl and decides:
  1. whether a retry is worth attempting at all
  2. the best hour-of-day window to retry
  3. whether to suggest a fallback payment method
"""

from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "retry_success_model.pkl"

FEATURES = [
    "payment_method", "bank", "card_type", "device_type", "failure_reason",
    "amount", "hour_of_day", "day_of_week", "is_weekend",
    "customer_tenure_days", "prior_failed_attempts_30d",
    "network_latency_ms", "retry_attempt_number",
]

CANDIDATE_HOURS = [10, 12, 15, 18, 20]
FALLBACK_METHOD = {
    "card": "upi",
    "netbanking": "upi",
    "wallet": "upi",
    "upi": "card",
}

# Reasons where retrying the SAME method is basically pointless.
NO_RETRY_REASONS = {"expired_card", "risk_declined"}


class RetryOptimizer:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model = joblib.load(model_path)

    def _score(self, transaction: dict) -> float:
        row = pd.DataFrame([{k: transaction.get(k) for k in FEATURES}])
        return float(self.model.predict_proba(row)[0][1])

    def recommend(self, transaction: dict) -> dict:
        reason = transaction.get("failure_reason")

        if reason in NO_RETRY_REASONS:
            return {
                "should_retry": False,
                "reason": f"'{reason}' rarely resolves via retry — recommend "
                          f"direct customer contact or payment-method change instead.",
                "suggested_method": FALLBACK_METHOD.get(transaction.get("payment_method")),
            }

        best_hour, best_score = None, -1.0
        for hour in CANDIDATE_HOURS:
            candidate = {**transaction, "hour_of_day": hour}
            score = self._score(candidate)
            if score > best_score:
                best_hour, best_score = hour, score

        same_method_score = self._score(transaction)
        fallback_method = FALLBACK_METHOD.get(transaction.get("payment_method"))
        fallback_txn = {**transaction, "payment_method": fallback_method}
        fallback_score = self._score(fallback_txn) if fallback_method else -1

        use_fallback = fallback_score > best_score

        return {
            "should_retry": max(best_score, fallback_score) > 0.4,
            "best_retry_hour": best_hour,
            "predicted_success_probability": round(max(best_score, fallback_score), 4),
            "suggested_method": fallback_method if use_fallback else transaction.get("payment_method"),
            "switched_method": use_fallback,
        }


if __name__ == "__main__":
    opt = RetryOptimizer()
    sample = {
        "payment_method": "netbanking", "bank": "IDFC", "card_type": "debit",
        "device_type": "mobile", "failure_reason": "bank_server_error",
        "amount": 1200, "hour_of_day": 3, "day_of_week": 2, "is_weekend": 0,
        "customer_tenure_days": 400, "prior_failed_attempts_30d": 0,
        "network_latency_ms": 300, "retry_attempt_number": 1,
    }
    print(opt.recommend(sample))
