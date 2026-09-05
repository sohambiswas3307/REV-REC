# AI Revenue Recovery — Razorpay AI Buildathon 2026

Predicts **why** a payment failed and **whether/how** to retry it — reducing
churn from failed recurring and one-off payments.

## Problem
Failed payments (card declines, expired cards, network blips, bank timeouts)
silently leak revenue. Blind retry-everything strategies waste attempts and
annoy customers. This project classifies the failure reason, predicts retry
success probability, and recommends the best retry time/method — or flags
when NOT to retry at all.

## Pipeline
```
Transaction → Failure Classifier (multiclass) → Retry Optimizer (binary)
                                                → Payment Fallback (rules)
                                                → Dunning Message (rules)
```

## Results (held-out test set, no leakage)
| Model | Metric | Score |
|---|---|---|
| Failure Reason Classifier | Accuracy | ~80% |
| Failure Reason Classifier | Macro F1 | ~0.64 |
| Retry Success Predictor | Accuracy | ~82% |
| Retry Success Predictor | ROC-AUC | ~0.89 |

These numbers are intentionally realistic (not 99%+) — the synthetic data
generator uses genuine class overlap and noise so the model reflects a
believable production scenario rather than a memorized toy problem.

## Data leakage safeguards
- **Customer-level train/test split** (not row-level) — no customer's
  transactions appear in both splits.
- **Fit-on-train-only** preprocessing (OneHotEncoder etc.) — never fit on
  combined train+test data.
- **No post-outcome features** — every input is something known at
  retry-decision time, never information that only exists after the retry
  happened.
- **Metrics computed only on held-out test data.**

## Frontend
`frontend/` is a Vite + React app ("Recovery Console") — a two-panel ledger UI:
left is transaction entry, right is the model's analysis (failure reason,
confidence breakdown, retry recommendation, dunning message).

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
```
Requires the API running (`uvicorn api.main:app --reload`) with CORS enabled.

## Setup
```bash
pip install -r requirements.txt
python data/generate_data.py        # generates synthetic dataset + splits
python src/train_models.py          # trains & saves both .pkl models
pytest tests/                       # or: python tests/test_pipeline.py
uvicorn api.main:app --reload       # start the API
```

## API
`POST /recover` — pass a transaction, get back failure reason, retry
recommendation, and a dunning message. See `api/main.py` for the schema.

## Repo structure
```
revenue-recovery-ai/
├── data/               # dataset generator + synthetic CSVs
├── src/                # classifier, retry optimizer, fallback, dunning logic
├── models/             # trained .pkl models + metrics
├── notebooks/          # EDA + training walkthrough
├── api/                # FastAPI app
├── tests/              # smoke tests
├── docs/               # architecture notes
└── demo/               # demo script for pitch video
```

## What broke & how it was fixed
Initial retry-success model was trained with `failed`/original-outcome
columns accidentally leaking through a shared preprocessing step, giving a
suspicious ~99% accuracy. Fixed by splitting into two separate
ColumnTransformer pipelines per target, explicitly listing allowed features
per model, and adding a customer-overlap assertion between train/test to
catch any future leakage early.

## Track
Razorpay AI Buildathon 2026 — **AI Revenue Recovery** track.
