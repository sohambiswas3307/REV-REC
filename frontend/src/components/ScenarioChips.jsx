import { SCENARIOS } from '../constants'

export default function ScenarioChips({ activeLabel, onPick }) {
  return (
    <div className="chips">
      <span className="chips-label">Try a scenario</span>
      <div className="chips-row">
        {SCENARIOS.map((s) => (
          <button
            key={s.label}
            className={'chip' + (activeLabel === s.label ? ' active' : '')}
            onClick={() => onPick(s)}
            title={s.note}
          >
            {s.label}
          </button>
        ))}
      </div>

      <style>{`
        .chips { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
        .chips-label { font-size: 0.8rem; color: var(--muted-dim); white-space: nowrap; }
        .chips-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .chip {
          background: var(--panel-raised);
          border: 1px solid var(--border);
          color: var(--muted);
          border-radius: 999px;
          padding: 0.4rem 0.9rem;
          font-size: 0.8rem;
          cursor: pointer;
          transition: all 0.15s ease;
        }
        .chip:hover { border-color: var(--accent); color: var(--text); }
        .chip.active {
          background: var(--accent-soft);
          border-color: var(--accent);
          color: var(--text);
        }
      `}</style>
    </div>
  )
}
