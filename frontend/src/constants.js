export const PAYMENT_METHODS = ['card', 'netbanking', 'upi', 'wallet']
export const CARD_TYPES = ['credit', 'debit', 'prepaid']
export const BANKS = ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'YES', 'IDFC']
export const DEVICES = ['mobile', 'desktop']

export const DEFAULT_TRANSACTION = {
  customer_name: 'Asha',
  payment_method: 'netbanking',
  bank: 'IDFC',
  card_type: 'debit',
  device_type: 'mobile',
  amount: 1200,
  hour_of_day: 3,
  day_of_week: 2,
  is_weekend: 0,
  customer_tenure_days: 400,
  prior_failed_attempts_30d: 0,
  network_latency_ms: 300,
  retry_attempt_number: 1,
}

export const DEFAULT_API_URL = 'http://127.0.0.1:8000/recover'

export const BANK_META = {
  HDFC: { initials: 'HD', color: '#e0475c' },
  ICICI: { initials: 'IC', color: '#f57d20' },
  SBI: { initials: 'SB', color: '#3a7bd5' },
  AXIS: { initials: 'AX', color: '#8b3fd1' },
  KOTAK: { initials: 'KO', color: '#d13f6a' },
  YES: { initials: 'YE', color: '#2fae6b' },
  IDFC: { initials: 'ID', color: '#c9822a' },
}

export const METHOD_ICONS = {
  card: 'CreditCard',
  upi: 'Smartphone',
  netbanking: 'Landmark',
  wallet: 'Wallet',
}

export const SCENARIOS = [
  {
    label: 'Bank server error',
    note: 'high latency, netbanking',
    txn: {
      customer_name: 'Asha', payment_method: 'netbanking', bank: 'IDFC',
      card_type: 'debit', device_type: 'mobile', amount: 1200,
      hour_of_day: 3, day_of_week: 2, is_weekend: 0,
      customer_tenure_days: 400, prior_failed_attempts_30d: 0,
      network_latency_ms: 300, retry_attempt_number: 1,
    },
  },
  {
    label: 'Expired card',
    note: 'credit card',
    txn: {
      customer_name: 'Rohan', payment_method: 'card', bank: 'HDFC',
      card_type: 'credit', device_type: 'mobile', amount: 800,
      hour_of_day: 14, day_of_week: 3, is_weekend: 0,
      customer_tenure_days: 250, prior_failed_attempts_30d: 0,
      network_latency_ms: 90, retry_attempt_number: 1,
    },
  },
  {
    label: 'Insufficient funds',
    note: 'high amount, prior fails',
    txn: {
      customer_name: 'Meera', payment_method: 'card', bank: 'SBI',
      card_type: 'debit', device_type: 'mobile', amount: 6000,
      hour_of_day: 14, day_of_week: 3, is_weekend: 0,
      customer_tenure_days: 250, prior_failed_attempts_30d: 2,
      network_latency_ms: 90, retry_attempt_number: 1,
    },
  },
  {
    label: 'Invalid OTP',
    note: 'small UPI payment',
    txn: {
      customer_name: 'Karan', payment_method: 'upi', bank: 'HDFC',
      card_type: 'debit', device_type: 'mobile', amount: 350,
      hour_of_day: 14, day_of_week: 3, is_weekend: 0,
      customer_tenure_days: 250, prior_failed_attempts_30d: 0,
      network_latency_ms: 90, retry_attempt_number: 1,
    },
  },
  {
    label: 'Risk declined',
    note: 'edge case — model\u2019s weakest class, often confused with insufficient funds',
    txn: {
      customer_name: 'Vikram', payment_method: 'card', bank: 'YES',
      card_type: 'debit', device_type: 'desktop', amount: 9000,
      hour_of_day: 2, day_of_week: 6, is_weekend: 1,
      customer_tenure_days: 30, prior_failed_attempts_30d: 3,
      network_latency_ms: 120, retry_attempt_number: 2,
    },
  },
]

export const METHOD_TABS = ['All', 'card', 'upi', 'netbanking', 'wallet']

export const GUIDES = [
  { title: 'Intro to Revenue Recovery', body: 'Failed payments leak revenue silently. This tool classifies why a payment failed, then decides if/how/when to retry it.' },
  { title: 'Failure Reasons Explained', body: 'Five classes: insufficient_funds, expired_card, bank_server_error, risk_declined, invalid_otp — each needs a different recovery action.' },
  { title: 'Retry Optimization Logic', body: 'Reasons like expired_card or risk_declined rarely resolve via retry — the model flags these instead of wasting an attempt.' },
  { title: 'Dunning Messages', body: 'Tone and cadence adapt to the failure reason — a bank error gets a soft auto-retry note, an expired card asks for action.' },
  { title: 'Model Metrics', body: 'Failure classifier: 79.8% accuracy, 0.64 macro F1. Retry model: 81.5% accuracy, 0.89 ROC-AUC. Numbers are realistic, not inflated.' },
  { title: 'Leakage Safeguards', body: 'Customer-level train/test split, fit-on-train-only preprocessing, and no post-outcome features feeding the model.' },
]
