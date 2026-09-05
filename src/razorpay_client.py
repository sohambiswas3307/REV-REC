"""
Thin wrapper around Razorpay's TEST-MODE APIs.

For the buildathon submission this defaults to a MOCK mode so the whole
pipeline (data -> model -> retry decision -> "payment attempt") can be
demoed end-to-end without needing live Razorpay test keys. Swap
MOCK_MODE=False and provide RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET (test mode
keys only) to hit the real Razorpay test environment.
"""

import os
import random
import time

MOCK_MODE = os.getenv("RAZORPAY_MOCK_MODE", "true").lower() == "true"


class RazorpayClient:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not MOCK_MODE:
            import razorpay  # pip install razorpay
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_payment_attempt(self, amount, method, customer_id):
        """Simulate (or make) a payment attempt in Razorpay TEST mode."""
        if MOCK_MODE:
            time.sleep(0.05)
            success = random.random() > 0.35
            return {
                "id": f"pay_mock_{int(time.time()*1000)}",
                "status": "captured" if success else "failed",
                "amount": amount,
                "method": method,
                "customer_id": customer_id,
            }
        order = self.client.order.create({
            "amount": int(amount * 100),  # paise
            "currency": "INR",
            "payment_capture": 1,
        })
        return order

    def retry_payment(self, original_payment_id, new_method=None):
        """Simulate a retry attempt, optionally with a fallback payment method."""
        if MOCK_MODE:
            time.sleep(0.05)
            success = random.random() > 0.3
            return {
                "id": f"retry_mock_{int(time.time()*1000)}",
                "original_payment_id": original_payment_id,
                "status": "captured" if success else "failed",
                "method": new_method,
            }
        raise NotImplementedError("Wire up real retry logic against Razorpay test APIs here.")
