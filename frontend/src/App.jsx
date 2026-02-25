import { useMemo, useState } from 'react'
import './App.css'

const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const API_BASE = configuredApiBase || (import.meta.env.DEV ? '' : null)

function formatNumber(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '--'
  }
  return value.toFixed(2)
}

function MiniLineChart({ points }) {
  const width = 640
  const height = 200
  const padding = 20

  const chartPath = useMemo(() => {
    if (!points || points.length < 2) {
      return ''
    }

    const max = Math.max(...points)
    const min = Math.min(...points)
    const span = Math.max(max - min, 1)

    return points
      .map((value, index) => {
        const x = padding + (index / (points.length - 1)) * (width - padding * 2)
        const y =
          height -
          padding -
          ((value - min) / span) * (height - padding * 2)
        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
      })
      .join(' ')
  }, [points])

  if (!chartPath) {
    return <p className="muted">No chart data available yet.</p>
  }

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Recent close prices">
      <path d={chartPath} fill="none" stroke="currentColor" strokeWidth="2.5" />
    </svg>
  )
}

function App() {
  const [ticker, setTicker] = useState('AAPL')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const callApi = async (endpoint, options = {}) => {
    setLoading(true)
    setError('')

    try {
      if (!API_BASE) {
        throw new Error('API is not configured. Set VITE_API_BASE_URL in Vercel project settings.')
      }

      const response = await fetch(`${API_BASE}${endpoint}`, options)
      const contentType = response.headers.get('content-type') || ''
      const payload = contentType.includes('application/json')
        ? await response.json()
        : null

      if (!response.ok) {
        throw new Error(payload?.error || `Request failed (${response.status})`)
      }

      if (!payload) {
        throw new Error('Backend returned a non-JSON response. Check API URL and deployment logs.')
      }

      setResult(payload)
    } catch (apiError) {
      const message = apiError instanceof Error ? apiError.message : 'Request failed'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    const symbol = ticker.trim().toUpperCase() || 'AAPL'
    await callApi(`/predict?ticker=${encodeURIComponent(symbol)}`)
  }

  const handleRetrain = async () => {
    const symbol = ticker.trim().toUpperCase() || 'AAPL'
    await callApi(`/train?ticker=${encodeURIComponent(symbol)}`, { method: 'POST' })
  }

  return (
    <main className="container">
      <header className="header">
        <h1>AI Stock Agent</h1>
        <p>Production-safe prediction dashboard</p>
      </header>

      <section className="controls">
        <input
          value={ticker}
          onChange={(event) => setTicker(event.target.value)}
          placeholder="Ticker (e.g. AAPL)"
          maxLength={10}
        />
        <button onClick={handlePredict} disabled={loading}>
          {loading ? 'Loading...' : 'Predict'}
        </button>
        <button className="secondary" onClick={handleRetrain} disabled={loading}>
          {loading ? 'Loading...' : 'Retrain'}
        </button>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="grid">
        <article className="card">
          <h3>Current Price</h3>
          <p>${formatNumber(result?.current_price)}</p>
        </article>
        <article className="card">
          <h3>Predicted Price</h3>
          <p>${formatNumber(result?.predicted_price)}</p>
        </article>
        <article className="card">
          <h3>Model Estimate</h3>
          <p>${formatNumber(result?.model_price)}</p>
        </article>
        <article className="card">
          <h3>Decision</h3>
          <p>{result?.decision || '--'}</p>
        </article>
        <article className="card">
          <h3>Model Status</h3>
          <p>{result ? (result.used_baseline ? 'Using Baseline' : 'Using Model') : '--'}</p>
        </article>
        <article className="card">
          <h3>Confidence</h3>
          <p>{result?.confidence?.toUpperCase() || '--'}</p>
        </article>
      </section>

      <section className="panel">
        <h2>Recent Price Trend</h2>
        <MiniLineChart points={result?.recent_close_prices || []} />
      </section>

      <section className="panel metrics">
        <h2>Validation Metrics</h2>
        <div className="metrics-grid">
          <div><span>MAE</span><strong>{formatNumber(result?.metrics?.mae)}</strong></div>
          <div><span>Baseline MAE</span><strong>{formatNumber(result?.metrics?.baseline_mae)}</strong></div>
          <div><span>RMSE</span><strong>{formatNumber(result?.metrics?.rmse)}</strong></div>
          <div><span>R²</span><strong>{formatNumber(result?.metrics?.r2)}</strong></div>
        </div>
      </section>

      <section className="panel metrics">
        <h2>Data Provenance</h2>
        <div className="metrics-grid">
          <div><span>Source</span><strong>{result?.data_source || '--'}</strong></div>
          <div><span>Requested Period</span><strong>{result?.data_period || '--'}</strong></div>
          <div><span>Rows Used</span><strong>{result?.data_rows ?? '--'}</strong></div>
          <div><span>Date Range</span><strong>{result ? `${result.data_start || '--'} → ${result.data_end || '--'}` : '--'}</strong></div>
          <div><span>Trained At</span><strong>{result?.trained_at || '--'}</strong></div>
          <div><span>Horizon</span><strong>{result?.target_horizon_days ?? '--'} day(s)</strong></div>
        </div>
      </section>
    </main>
  )
}

export default App
