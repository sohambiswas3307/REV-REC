# Demo Script

```bash
# 1. Generate data
python data/generate_data.py

# 2. Train models
python src/train_models.py

# 3. Run tests
python tests/test_pipeline.py

# 4. Start API
uvicorn api.main:app --reload

# 5. Sample request
curl -X POST http://localhost:8000/recover -H "Content-Type: application/json" -d '{
  "customer_name": "Asha",
  "payment_method": "netbanking",
  "bank": "IDFC",
  "card_type": "debit",
  "device_type": "mobile",
  "amount": 1200,
  "hour_of_day": 3,
  "day_of_week": 2,
  "is_weekend": 0,
  "customer_tenure_days": 400,
  "prior_failed_attempts_30d": 0,
  "network_latency_ms": 300,
  "retry_attempt_number": 1
}'
```

Expected: a bank_server_error-type classification with a high retry-success
probability and a recommended off-peak retry hour, since bank server errors
are transient.
