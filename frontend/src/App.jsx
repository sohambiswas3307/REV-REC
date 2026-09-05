import { useEffect, useState } from 'react'
import ScenarioChips from './components/ScenarioChips'
import HistoryStrip from './components/HistoryStrip'
import TransactionForm from './components/TransactionForm'
import ResultPanel from './components/ResultPanel'
import { DEFAULT_TRANSACTION, DEFAULT_API_URL } from './constants'

export default function App() {
  const [apiUrl, setApiUrl] = useState(DEFAULT_API_URL)
  const [apiStatus, setApiStatus] = useState('checking')
  const [txn, setTxn] = useState(DEFAULT_TRANSACTION)
  const [activeScenario, setActiveScenario] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [copyLabel, setCopyLabel] = useState('Copy JSON')

  const healthUrl = () => apiUrl.replace(/\/recover\/?$/, '/health')

  useEffect(() => {
    let cancelled = false
    setApiStatus('checking')
    fetch(healthUrl())
      .then((res) => { if (!cancelled) setApiStatus(res.ok ? 'ready' : 'down') })
      .catch(() => { if (!cancelled) setApiStatus('down') })
    return () => { cancelled = true }
  }, [apiUrl])

  function pickScenario(scenario) {
    setActiveScenario(scenario.label)
    setTxn(scenario.txn)
    setResult(null)
    setError(null)
  }

  function handleFormChange(next) {
    setActiveScenario(null)
    setTxn(next)
  }

  async function runAnalysis() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(txn),
      })
      if (!res.ok) throw new Error(`Server responded ${res.status}`)
      const data = await res.json()
      setResult(data)
      setHistory((prev) => [
        {
          id: Date.now(),
          customer_name: txn.customer_name,
          failure_reason: data.failure_classification.failure_reason,
          should_retry: data.retry_recommendation.should_retry,
          txn,
          result: data,
        },
        ...prev,
      ].slice(0, 6))
    } catch (err) {
      setError(
        `Request failed: ${err.message}. Confirm the API is running ` +
        `(uvicorn api.main:app --reload) and CORS is enabled.`
      )
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  function selectHistory(entry) {
    setTxn(entry.txn)
    setResult(entry.result)
    setActiveScenario(null)
    setError(null)
  }

  function copyJson() {
    if (!result) return
    navigator.clipboard.writeText(JSON.stringify(result, null, 2)).then(() => {
      setCopyLabel('Copied')
      setTimeout(() => setCopyLabel('Copy JSON'), 1200)
    })
  }

  const dotColor =
    apiStatus === 'ready' ? 'var(--positive)' :
    apiStatus === 'checking' ? 'var(--muted-dim)' : 'var(--negative)'
  const statusLabel =
    apiStatus === 'ready' ? 'API connected' :
    apiStatus === 'checking' ? 'Checking API…' : 'API unreachable'

  return (
    <div className="page">
      <header className="hero"></header>

      <div className="content">
        <ScenarioChips activeLabel={activeScenario} onPick={pickScenario} />

        <div className="workspace">
          <TransactionForm txn={txn} onChange={handleFormChange} onSubmit={runAnalysis} loading={loading} />
          <ResultPanel result={result} error={error} loading={loading} onCopy={copyJson} copyLabel={copyLabel} />
        </div>

        <HistoryStrip entries={history} onSelect={selectHistory} />
      </div>

      <style>{`
        .page { min-height: 100vh; padding-bottom: 3rem; }
        .hero { display: none; }
        .hero h1 {
          font-size: 2rem;
          font-weight: 700;
          letter-spacing: -0.02em;
          margin: 0 0 0.6rem;
          line-height: 1.2;
        }
        .subtitle {
          font-size: 0.95rem;
          color: var(--muted);
          line-height: 1.6;
          max-width: 620px;
          margin: 0;
        }
        .content { max-width: 900px; margin: 0 auto; padding: 2.25rem 1.5rem 0; }
        .workspace {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.25rem;
          margin-top: 1.5rem;
        }
        .panel {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
          padding: 1.6rem 1.75rem;
        }
        @media (max-width: 800px) {
          .workspace { grid-template-columns: 1fr; }
          .hero h1 { font-size: 1.5rem; }
        }
      `}</style>
    </div>
  )
}
