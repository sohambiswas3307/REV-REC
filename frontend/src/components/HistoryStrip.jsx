export default function HistoryStrip({ entries, onSelect }) {
  if (entries.length === 0) return null

  return (
    <div className="history">
      <div className="history-row">
        {entries.map((e) => (
          <button key={e.id} className="history-item" onClick={() => onSelect(e)}>
            <span
              className="dot"
              style={{ background: e.should_retry ? 'var(--positive)' : 'var(--negative)' }}
            />
            <span className="name">{e.customer_name}</span>
            <span className="reason mono">{e.failure_reason}</span>
          </button>
        ))}
      </div>

      <style>{`
        .history { display: flex; align-items: center; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap; }
        .history-label { font-size: 0.78rem; color: var(--muted-dim); white-space: nowrap; }
        .history-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .history-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: var(--panel-raised);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.4rem 0.75rem;
          cursor: pointer;
          font-size: 0.76rem;
        }
        .history-item:hover { border-color: var(--accent); }
        .dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
        .name { color: var(--text); }
        .reason { color: var(--muted); }
      `}</style>
    </div>
  )
}
