import { CreditCard, Smartphone, Landmark, Wallet } from 'lucide-react'
import { PAYMENT_METHODS, CARD_TYPES, BANKS, DEVICES, BANK_META } from '../constants'

const METHOD_ICON_COMPONENTS = {
  card: CreditCard,
  upi: Smartphone,
  netbanking: Landmark,
  wallet: Wallet,
}

const NUMERIC_FIELDS = [
  ['hour_of_day', 'Hour of day (0–23)'],
  ['day_of_week', 'Day of week (0 = Mon)'],
  ['customer_tenure_days', 'Customer tenure (days)'],
  ['prior_failed_attempts_30d', 'Prior fails, 30d'],
  ['network_latency_ms', 'Network latency (ms)'],
  ['retry_attempt_number', 'Retry attempt #'],
]

function Row({ label, children }) {
  return (
    <div className="row">
      <label>{label}</label>
      <div className="row-input">{children}</div>
    </div>
  )
}

function BankBadge({ bank }) {
  const meta = BANK_META[bank]
  if (!meta) return null
  return (
    <span className="bank-badge" style={{ background: meta.color }}>
      {meta.initials}
    </span>
  )
}

export default function TransactionForm({ txn, onChange, onSubmit, loading }) {
  const set = (key, value) => onChange({ ...txn, [key]: value })
  const MethodIcon = METHOD_ICON_COMPONENTS[txn.payment_method]

  return (
    <form
      className="panel form"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <h2>Transaction</h2>

      <Row label="Customer name">
        <input value={txn.customer_name} onChange={(e) => set('customer_name', e.target.value)} />
      </Row>

      <Row label="Payment method">
        <div className="iconed-select">
          <span className="field-icon">{MethodIcon && <MethodIcon size={15} />}</span>
          <select
            className="has-icon"
            value={txn.payment_method}
            onChange={(e) => set('payment_method', e.target.value)}
          >
            {PAYMENT_METHODS.map((m) => <option key={m}>{m}</option>)}
          </select>
        </div>
      </Row>

      <Row label="Card type">
        <select value={txn.card_type} onChange={(e) => set('card_type', e.target.value)}>
          {CARD_TYPES.map((c) => <option key={c}>{c}</option>)}
        </select>
      </Row>

      <Row label="Bank">
        <div className="iconed-select">
          <span className="field-icon"><BankBadge bank={txn.bank} /></span>
          <select
            className="has-icon"
            value={txn.bank}
            onChange={(e) => set('bank', e.target.value)}
          >
            {BANKS.map((b) => <option key={b}>{b}</option>)}
          </select>
        </div>
      </Row>

      <Row label="Device">
        <select value={txn.device_type} onChange={(e) => set('device_type', e.target.value)}>
          {DEVICES.map((d) => <option key={d}>{d}</option>)}
        </select>
      </Row>

      <Row label="Weekend">
        <select value={txn.is_weekend} onChange={(e) => set('is_weekend', Number(e.target.value))}>
          <option value={0}>No</option>
          <option value={1}>Yes</option>
        </select>
      </Row>

      <Row label="Amount">
        <div className="iconed-select">
          <span className="field-icon currency">₹</span>
          <input
            className="has-icon"
            type="number"
            value={txn.amount}
            onChange={(e) => set('amount', Number(e.target.value))}
          />
        </div>
      </Row>

      {NUMERIC_FIELDS.map(([key, label]) => (
        <Row key={key} label={label}>
          <input
            type="number"
            value={txn[key]}
            onChange={(e) => set(key, Number(e.target.value))}
          />
        </Row>
      ))}

      <button type="submit" disabled={loading}>
        {loading ? 'Analyzing…' : 'Analyze transaction'}
      </button>

      <style>{`
        .form { display: flex; flex-direction: column; }
        .form h2 {
          font-size: 0.9rem;
          font-weight: 600;
          margin: 0 0 1.1rem;
          color: var(--text);
        }
        .row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          align-items: center;
          gap: 1rem;
          padding: 0.55rem 0;
          border-bottom: 1px solid var(--border-soft);
        }
        .row:last-of-type { border-bottom: none; }
        .row label {
          font-size: 0.79rem;
          color: var(--muted);
        }
        .row-input input,
        .row-input select {
          width: 100%;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 7px;
          color: var(--text);
          padding: 0.45rem 0.6rem;
          font-size: 0.83rem;
          font-family: var(--font-mono);
        }
        .row-input select { font-family: var(--font-sans); }
        .row-input input:focus, .row-input select:focus { border-color: var(--accent); }

        .iconed-select { position: relative; display: flex; align-items: center; }
        .field-icon {
          position: absolute;
          left: 0.55rem;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--muted);
          pointer-events: none;
        }
        .field-icon.currency { font-size: 0.9rem; font-weight: 600; color: var(--muted); }
        .bank-badge {
          width: 20px;
          height: 20px;
          border-radius: 5px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.55rem;
          font-weight: 700;
          color: #0a0d18;
          letter-spacing: -0.02em;
        }
        select.has-icon, input.has-icon { padding-left: 2.2rem; }

        button[type="submit"] {
          margin-top: 1.4rem;
          background: var(--accent);
          color: #0a0d18;
          border: none;
          border-radius: 8px;
          padding: 0.75rem;
          font-size: 0.88rem;
          font-weight: 600;
          cursor: pointer;
          transition: filter 0.15s ease;
        }
        button[type="submit"]:hover:not(:disabled) { filter: brightness(1.12); }
        button[type="submit"]:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>
    </form>
  )
}
