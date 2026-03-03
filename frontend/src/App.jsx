import { useState } from 'react'
import './App.css'

const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const API_BASE = configuredApiBase || (import.meta.env.DEV ? 'http://127.0.0.1:5000' : null)
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 45000)

function formatNumber(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '--'
  }
  return value.toFixed(2)
}

function App() {
  const [ticker, setTicker] = useState('AAPL')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const performRequest = async (endpoint, options = {}) => {
    if (!API_BASE) {
      throw new Error('API is not configured. Set VITE_API_BASE_URL in Vercel project settings.')
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    let response
    try {
      response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        signal: controller.signal,
      })
    } finally {
      clearTimeout(timeoutId)
    }

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

    return payload
  }

  const callApi = async (endpoint, options = {}, settings = {}) => {
    const { autoRetrainOnMissingModel = false } = settings

    setLoading(true)
    setError('')
    setResult(null)

    try {
      let payload
      try {
        payload = await performRequest(endpoint, options)
      } catch (initialError) {
        const initialMessage = initialError instanceof Error ? initialError.message : ''
        const shouldRetryWithRetrain =
          autoRetrainOnMissingModel &&
          /model not trained yet/i.test(initialMessage) &&
          endpoint.startsWith('/predict')

        if (!shouldRetryWithRetrain) {
          throw initialError
        }

        const separator = endpoint.includes('?') ? '&' : '?'
        payload = await performRequest(`${endpoint}${separator}retrain=true`, options)
      }

      setResult(payload)
    } catch (apiError) {
      let message = apiError instanceof Error ? apiError.message : 'Request failed'

      if (apiError instanceof DOMException && apiError.name === 'AbortError') {
        message = `Request timed out after ${Math.round(REQUEST_TIMEOUT_MS / 1000)}s. Backend may be cold-starting or training.`
      } else if (message === 'Failed to fetch') {
        message = 'Network error while contacting backend. Check VITE_API_BASE_URL, backend uptime, CORS, and HTTPS URL.'
      }

      setError(message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    const symbol = ticker.trim().toUpperCase() || 'AAPL'
    await callApi(
      `/predict?ticker=${encodeURIComponent(symbol)}`,
      {},
      { autoRetrainOnMissingModel: true }
    )
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
          <h3>Predicted Price</h3>
          <p>${formatNumber(result?.predicted_price)}</p>
        </article>
        <article className="card">
          <h3>Decision</h3>
          <p>{result?.decision || '--'}</p>
        </article>
      </section>
    </main>
  )
}

export default App
