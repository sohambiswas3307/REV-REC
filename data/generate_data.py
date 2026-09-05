"""
Synthetic payment-failure dataset generator for the AI Revenue Recovery project.

Design goals
------------
1. Realistic causal structure: failure probability and retry-success
   probability are driven by plausible underlying factors (bank, card
   type, network latency, time of day, customer history) instead of
   pure random noise, so a model trained on it has real, learnable signal.
2. NO DATA LEAKAGE:
   - Every feature is something known at the moment we decide whether/how
     to retry. Nothing derived from post-outcome information is included.
   - "prior_failed_attempts_30d" and "customer_tenure_days" are historical
     / pre-transaction facts, not computed from the current row's outcome.
   - Train/test split is done BY CUSTOMER (not by row), so no customer's
     transactions appear in both sets - this prevents the model from
     memorizing a specific customer's pattern across the split.
   - retry_success is only generated for rows where failed == 1, and never
     used as a feature for predicting failure_reason (separate targets,
     separate models, no cross-target leakage).
3. Two targets, two models:
      - failure_reason  -> multiclass classification (why did it fail)
      - retry_success   -> binary classification (will a retry work)
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_ROWS = 20_000

OUT_DIR = Path(__file__).parent / "synthetic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BANKS = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "YES", "IDFC"]
CARD_TYPES = ["credit", "debit", "prepaid"]
PAYMENT_METHODS = ["card", "upi", "netbanking", "wallet"]
FAILURE_REASONS = [
    "insufficient_funds",
    "expired_card",
    "bank_server_error",
    "risk_declined",
    "invalid_otp",
    "no_failure",
]


def generate_transactions(n=N_ROWS) -> pd.DataFrame:
    customer_id = RNG.integers(1, n // 3, size=n)  # repeat customers
    amount = np.round(RNG.gamma(shape=2.0, scale=800, size=n), 2)
    payment_method = RNG.choice(PAYMENT_METHODS, size=n, p=[0.45, 0.35, 0.12, 0.08])
    bank = RNG.choice(BANKS, size=n)
    card_type = RNG.choice(CARD_TYPES, size=n, p=[0.5, 0.4, 0.1])
    hour_of_day = RNG.integers(0, 24, size=n)
    day_of_week = RNG.integers(0, 7, size=n)
    is_weekend = (day_of_week >= 5).astype(int)
    customer_tenure_days = RNG.integers(1, 1500, size=n)
    prior_failed_attempts_30d = RNG.poisson(0.6, size=n)
    network_latency_ms = np.round(RNG.exponential(scale=180, size=n) + 40, 1)
    retry_attempt_number = RNG.integers(1, 4, size=n)
    device_type = RNG.choice(["mobile", "desktop"], size=n, p=[0.72, 0.28])

    df = pd.DataFrame({
        "transaction_id": np.arange(1, n + 1),
        "customer_id": customer_id,
        "amount": amount,
        "payment_method": payment_method,
        "bank": bank,
        "card_type": card_type,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "customer_tenure_days": customer_tenure_days,
        "prior_failed_attempts_30d": prior_failed_attempts_30d,
        "network_latency_ms": network_latency_ms,
        "retry_attempt_number": retry_attempt_number,
        "device_type": device_type,
    })

    # ---- Failure probability driven by causal-ish factors ------------------
    logit = (
        -2.2
        + 1.8 * (df["payment_method"] == "netbanking")
        + 1.1 * (df["card_type"] == "prepaid")
        + 0.9 * (df["prior_failed_attempts_30d"])
        + 0.01 * (df["network_latency_ms"] - 180)
        + 1.0 * (df["hour_of_day"].between(0, 5).astype(int))
        + 0.7 * (df["amount"] > 3000)
        + 0.9 * (df["bank"].isin(["YES", "IDFC"]))
        - 0.6 * (df["customer_tenure_days"] > 365)
    )
    fail_prob = 1 / (1 + np.exp(-logit))
    failed = RNG.binomial(1, fail_prob)

    # ---- Failure reason (only defined where failed == 1) --------------------
    reason = np.full(n, "no_failure", dtype=object)
    fail_idx = np.where(failed == 1)[0]

    reasons5 = FAILURE_REASONS[:-1]
    reason_logits = np.zeros((len(fail_idx), 5))
    amt = df["amount"].values[fail_idx]
    card = df["card_type"].values[fail_idx]
    method = df["payment_method"].values[fail_idx]
    latency = df["network_latency_ms"].values[fail_idx]
    prior = df["prior_failed_attempts_30d"].values[fail_idx]

    reason_logits[:, 0] += 3.2 * (amt > 2500) + 1.4 * prior             # insufficient_funds
    reason_logits[:, 1] += 3.2 * (card == "credit")                      # expired_card
    reason_logits[:, 2] += 0.05 * (latency - 180)                        # bank_server_error
    reason_logits[:, 3] += 3.0 * (prior > 1) + 2.0 * (amt > 5000)        # risk_declined
    reason_logits[:, 4] += 3.4 * (method == "upi")                       # invalid_otp
    reason_logits += RNG.normal(0, 0.2, size=reason_logits.shape)        # residual noise

    probs = np.exp(reason_logits)
    probs = probs / probs.sum(axis=1, keepdims=True)
    chosen = [RNG.choice(reasons5, p=p) for p in probs]
    reason[fail_idx] = chosen
    df["failure_reason"] = reason

    # ---- Retry success target -------------------------------------------------
    retry_logit = (
        1.8
        - 1.0 * df["retry_attempt_number"]
        - 2.4 * (df["failure_reason"] == "risk_declined").astype(int)
        - 1.8 * (df["failure_reason"] == "expired_card").astype(int)
        + 2.2 * (df["failure_reason"] == "bank_server_error").astype(int)
        + 1.3 * (df["hour_of_day"].between(9, 21).astype(int))
        - 1.0 * df["prior_failed_attempts_30d"]
        + 0.9 * (df["customer_tenure_days"] > 180)
    )
    retry_prob = 1 / (1 + np.exp(-retry_logit))
    retry_success = RNG.binomial(1, retry_prob)
    retry_success = np.where(failed == 1, retry_success, np.nan)

    df["failed"] = failed
    df["retry_success"] = retry_success

    return df


def train_test_split_by_customer(df: pd.DataFrame, test_size=0.2, seed=42):
    """
    Split BY customer_id (not by row) so the same customer never appears
    in both train and test -> prevents customer-level leakage.
    """
    rng = np.random.default_rng(seed)
    unique_customers = df["customer_id"].unique()
    rng.shuffle(unique_customers)
    n_test = int(len(unique_customers) * test_size)
    test_customers = set(unique_customers[:n_test])
    is_test = df["customer_id"].isin(test_customers)
    return df[~is_test].copy(), df[is_test].copy()


if __name__ == "__main__":
    df = generate_transactions()
    train_df, test_df = train_test_split_by_customer(df)

    df.to_csv(OUT_DIR / "transactions_full.csv", index=False)
    train_df.to_csv(OUT_DIR / "transactions_train.csv", index=False)
    test_df.to_csv(OUT_DIR / "transactions_test.csv", index=False)

    print(f"Generated {len(df)} rows -> {OUT_DIR}")
    print(f"Train: {len(train_df)} rows | Test: {len(test_df)} rows")
    print(f"Overall failure rate: {df['failed'].mean():.3f}")
    print(f"Retry success rate (of failed): {df.loc[df['failed']==1, 'retry_success'].mean():.3f}")
