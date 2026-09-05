"""FastAPI app exposing the revenue recovery pipeline.

Run: uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.failure_classifier import FailureClassifier
from src.retry_optimizer import RetryOptimizer
from src.dunning_manager import build_dunning_message

app = FastAPI(title="Razorpay AI Revenue Recovery")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

failure_clf = FailureClassifier()
retry_opt = RetryOptimizer()


class Transaction(BaseModel):
    customer_name: str = "Customer"
    payment_method: str
    bank: str
    card_type: str | None = None
    device_type: str = "mobile"
    amount: float
    hour_of_day: int
    day_of_week: int
    is_weekend: int
    customer_tenure_days: int
    prior_failed_attempts_30d: int
    network_latency_ms: float
    retry_attempt_number: int = 1


@app.post("/recover")
def recover(txn: Transaction):
    txn_dict = txn.model_dump()

    failure_result = failure_clf.predict(txn_dict)
    txn_dict["failure_reason"] = failure_result["failure_reason"]

    retry_result = retry_opt.recommend(txn_dict)

    dunning = build_dunning_message(
        name=txn.customer_name,
        amount=txn.amount,
        failure_reason=failure_result["failure_reason"],
        retry_hour=retry_result.get("best_retry_hour"),
    )

    return {
        "failure_classification": failure_result,
        "retry_recommendation": retry_result,
        "dunning_message": dunning,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
