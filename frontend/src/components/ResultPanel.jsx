import ProbabilityMeter from './ProbabilityMeter'

function Line({ label, value, mono = true }) {
  return (
    <div className="line">
      <span className="line-label">{label}</span>
      <span className="line-leader" />
      <span className={mono ? 'line-value mono' : 'line-value'}>{value}</span>
    </div>
  )
}

export default function ResultPanel({ result, error, loading, onCopy, copyLabel }) {
  return (
    <div className="panel receipt">
      <div className="receipt-head">
        <h2>Analysis</h2>
        {result && !loading && (
          <button type="button" className="copy-btn" onClick={onCopy}>{copyLabel}</button>
        )}
      </div>

      {!result && !error && !loading && (
        <p className="empty">Fill in the transaction and run an analysis to see a recommendation here.</p>
      )}

      {loading && <p className="empty">Running failure classifier and retry optimizer…</p>}

      {error && <p className="error">{error}</p>}

      {result && !loading && (
        <div className="reveal">
          <section>
            <h3>Failure reason</h3>
            <div className="reason-row">
              <span className="reason mono">{result.failure_classification.failure_reason}</span>
              <span className="confidence mono">
                {(result.failure_classification.confidence * 100).toFixed(1)}% confidence
              </span>
            </div>
            {Object.entries(result.failure_classification.all_probabilities)
              .sort((a, b) => b[1] - a[1])
              .map(([label, p]) => (
                <div key={label} className="prob-row">
                  <span className="prob-label">{label}</span>
                  <ProbabilityMeter value={p} />
                  <span className="prob-value mono">{(p * 100).toFixed(1)}%</span>
                </div>
              ))}
          </section>

          <section>
            <h3>Retry recommendation</h3>
            <div
              className="verdict"
              style={{
                background: result.retry_recommendation.should_retry ? 'var(--positive-soft)' : 'var(--negative-soft)',
                color: result.retry_recommendation.should_retry ? 'var(--positive)' : 'var(--negative)',
              }}
            >
              {result.retry_recommendation.should_retry ? 'Retry recommended' : 'Do not retry'}
            </div>

            {result.retry_recommendation.should_retry ? (
              <>
                <Line label="Best retry hour" value={`${result.retry_recommendation.best_retry_hour}:00`} />
                <Line
                  label="Predicted success"
                  value={`${(result.retry_recommendation.predicted_success_probability * 100).toFixed(1)}%`}
                />
                <Line
                  label="Suggested method"
                  value={
                    result.retry_recommendation.suggested_method +
                    (result.retry_recommendation.switched_method ? ' (switched)' : '')
                  }
                  mono={false}
                />
              </>
            ) : (
              <Line label="Reason" value={result.retry_recommendation.reason} mono={false} />
            )}
          </section>

          <section>
            <h3>Dunning message</h3>
            <div className="message-box">{result.dunning_message.message}</div>
            <Line label="Channel" value={result.dunning_message.channel} mono={false} />
            <Line label="Scheduled" value={result.dunning_message.scheduled_for || 'immediately'} mono={false} />
          </section>
        </div>
      )}

      <style>{`
        .receipt-head {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 1.1rem;
        }
        .receipt h2 {
          font-size: 0.9rem;
          font-weight: 600;
          margin: 0;
        }
        .copy-btn {
          background: none;
          border: 1px solid var(--border);
          color: var(--muted);
          border-radius: 6px;
          padding: 0.3rem 0.65rem;
          font-size: 0.72rem;
          cursor: pointer;
        }
        .copy-btn:hover { border-color: var(--accent); color: var(--text); }
        .reveal { animation: reveal 0.2s ease; }
        @keyframes reveal {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .empty, .error {
          font-size: 0.85rem;
          color: var(--muted);
          line-height: 1.55;
        }
        .error { color: var(--negative); }
        section {
          margin-bottom: 1.5rem;
          padding-bottom: 1.3rem;
          border-bottom: 1px solid var(--border-soft);
        }
        section:last-child { border-bottom: none; margin-bottom: 0; }
        section h3 {
          font-size: 0.74rem;
          font-weight: 600;
          color: var(--muted-dim);
          margin: 0 0 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .reason-row {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 1rem;
        }
        .reason { font-size: 1.1rem; color: var(--text); font-weight: 600; }
        .confidence { font-size: 0.76rem; color: var(--muted); }
        .prob-row {
          display: grid;
          grid-template-columns: 110px 1fr 46px;
          align-items: center;
          gap: 0.6rem;
          margin-bottom: 0.45rem;
        }
        .prob-label { font-size: 0.73rem; color: var(--muted); }
        .prob-value { font-size: 0.73rem; color: var(--muted); text-align: right; }
        .verdict {
          display: inline-block;
          padding: 0.35rem 0.8rem;
          border-radius: 999px;
          margin-bottom: 1rem;
          font-size: 0.85rem;
          font-weight: 600;
        }
        .line {
          display: flex;
          align-items: baseline;
          gap: 0.4rem;
          padding: 0.3rem 0;
          font-size: 0.82rem;
        }
        .line-label { color: var(--muted); white-space: nowrap; }
        .line-leader {
          flex: 1;
          border-bottom: 1px dotted var(--border);
          margin-bottom: 3px;
        }
        .line-value { color: var(--text); white-space: nowrap; }
        .mono { font-family: var(--font-mono); }
        .message-box {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.85rem 1rem;
          font-size: 0.84rem;
          line-height: 1.55;
          margin-bottom: 0.7rem;
        }
      `}</style>
    </div>
  )
}
