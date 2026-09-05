const TICKS = 20

export default function ProbabilityMeter({ value, color = 'var(--accent)' }) {
  const filled = Math.round(value * TICKS)

  return (
    <div className="meter">
      {Array.from({ length: TICKS }).map((_, i) => (
        <span
          key={i}
          className="tick"
          style={{ background: i < filled ? color : 'var(--border)' }}
        />
      ))}
      <style>{`
        .meter { display: flex; gap: 2px; height: 14px; align-items: flex-end; }
        .tick { flex: 1; height: 100%; border-radius: 1px; }
      `}</style>
    </div>
  )
}