"""Basic smoke tests for the revenue recovery pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.failure_classifier import FailureClassifier
from src.retry_optimizer import RetryOptimizer
from src.payment_fallback import next_fallback_method
from src.dunning_manager import build_dunning_message


def test_failure_classifier_returns_valid_reason():
    clf = FailureClassifier()
    sample = {
        "payment_method": "card", "bank": "YES", "card_type": "credit",
        "device_type": "mobile", "amount": 4500, "hour_of_day": 2,
        "day_of_week": 5, "is_weekend": 1, "customer_tenure_days": 40,
        "prior_failed_attempts_30d": 2, "network_latency_ms": 260,
        "retry_attempt_number": 1,
    }
    result = clf.predict(sample)
    assert result["failure_reason"] in {
        "insufficient_funds", "expired_card", "bank_server_error",
        "risk_declined", "invalid_otp",
    }
    assert 0 <= result["confidence"] <= 1


def test_retry_optimizer_blocks_hopeless_reasons():
    opt = RetryOptimizer()
    sample = {
        "payment_method": "card", "bank": "SBI", "card_type": "credit",
        "device_type": "mobile", "failure_reason": "expired_card",
        "amount": 1000, "hour_of_day": 12, "day_of_week": 1, "is_weekend": 0,
        "customer_tenure_days": 200, "prior_failed_attempts_30d": 0,
        "network_latency_ms": 100, "retry_attempt_number": 1,
    }
    result = opt.recommend(sample)
    assert result["should_retry"] is False


def test_payment_fallback_chain():
    assert next_fallback_method("card", ["card"]) == "upi"
    assert next_fallback_method("card", ["card", "upi"]) == "netbanking"
    assert next_fallback_method("card", ["card", "upi", "netbanking", "wallet"]) is None


def test_dunning_message_builds():
    result = build_dunning_message("Asha", 1499, "insufficient_funds", 18)
    assert "Asha" in result["message"]
    assert "1499" in result["message"]


if __name__ == "__main__":
    test_failure_classifier_returns_valid_reason()
    test_retry_optimizer_blocks_hopeless_reasons()
    test_payment_fallback_chain()
    test_dunning_message_builds()
    print("All tests passed.")
