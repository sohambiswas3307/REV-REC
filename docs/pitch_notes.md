# Pitch Notes (for 5-min video)

1. **Problem (30s)**: Failed payments silently leak revenue; blind retries
   waste attempts and annoy customers.
2. **Demo (2 min)**: Show `/recover` API call on a failed transaction →
   walk through failure_reason → retry_recommendation → dunning message.
3. **What broke (1 min)**: Early retry model leaked the original outcome
   through shared preprocessing → caught via suspicious 99% accuracy →
   fixed with per-target pipelines + customer-overlap assertion.
4. **Metrics & judgment (1 min)**: ~80% / ~82% accuracy, ROC-AUC 0.89 — framed
   as realistic, not inflated. Explain why RandomForest, why rules for
   fallback/dunning instead of ML.
5. **Close (30s)**: Recovery rate impact framing — even a 15-20% lift in
   retry success across a payment platform's failed-transaction volume
   translates directly to recovered revenue.
