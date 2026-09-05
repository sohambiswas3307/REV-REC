# Architecture

```
                 ┌─────────────────────┐
   Failed        │  Failure Classifier │  → failure_reason + confidence
   Transaction ─▶│  (RandomForest,     │
                 │   multiclass)       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Retry Optimizer    │  → should_retry, best_hour,
                 │  (RandomForest,     │     suggested_method
                 │   binary)           │
                 └──────────┬──────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   ┌─────────────────────┐      ┌─────────────────────┐
   │  Payment Fallback    │      │  Dunning Manager     │
   │  (rule-based chain)  │      │  (rule-based message)│
   └─────────────────────┘      └─────────────────────┘
```

## Why RandomForest over deep learning
Tabular data with ~12 features and 16k training rows — RandomForest gives
strong, well-calibrated, and explainable results (feature_importances_)
without the overfitting risk or training complexity of a neural net. This is
a deliberate "AI Judgment" choice: use the simplest model that meets the bar,
not the fanciest one.

## Why rule-based fallback/dunning, not ML
Payment-method fallback ordering and reminder cadence are business policy
decisions, not predictions — a lookup table is more auditable and reliable
than a model here. ML is reserved for the two genuinely predictive
sub-problems (failure reason, retry success).
