"""Generates dunning (payment-reminder) schedules for failed recurring
payments, adjusting cadence and tone based on the predicted failure reason
and retry recommendation."""

from datetime import datetime, timedelta
from typing import Optional

TEMPLATES = {
    "insufficient_funds": "Hi {name}, your payment of Rs.{amount} didn't go through. "
                           "We'll try again on {retry_date} - feel free to top up before then.",
    "expired_card": "Hi {name}, your card on file has expired. Please update your "
                     "payment method to avoid service interruption.",
    "bank_server_error": "Hi {name}, we hit a temporary issue with your bank. "
                          "We're retrying automatically shortly.",
    "risk_declined": "Hi {name}, your bank declined this transaction for security "
                      "reasons. Please contact your bank or try an alternate method.",
    "invalid_otp": "Hi {name}, the OTP verification failed. Please retry your payment.",
}

DEFAULT_TEMPLATE = "Hi {name}, your payment of Rs.{amount} was unsuccessful. We'll retry soon."


def build_dunning_message(name: str, amount: float, failure_reason: str, retry_hour: Optional[int]) -> dict:
    template = TEMPLATES.get(failure_reason, DEFAULT_TEMPLATE)
    retry_date = None
    if retry_hour is not None:
        retry_dt = datetime.now().replace(hour=retry_hour, minute=0, second=0, microsecond=0)
        if retry_dt < datetime.now():
            retry_dt += timedelta(days=1)
        retry_date = retry_dt.strftime("%b %d, %I:%M %p")

    message = template.format(name=name, amount=amount, retry_date=retry_date or "shortly")
    return {"channel": "email+sms", "message": message, "scheduled_for": retry_date}


if __name__ == "__main__":
    print(build_dunning_message("Asha", 1499, "insufficient_funds", 18))
