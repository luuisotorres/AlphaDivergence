import { useState } from 'react'
import axios from 'axios'
import './App.css'

import { API_BASE_URL } from './config'

function App() {
  const [token, setToken] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!token) return
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const response = await axios.get(`${API_BASE_URL}/analyze/${token}`)
      setData(response.data)
    } catch (err) {
      setError("Failed to fetch analysis. Ensure backend is running.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>AlphaDivergence</h1>
      <p className="subtitle">Multi-Agent Fake Hype Detector</p>

      <div className="search-box">
        <input
          type="text"
          placeholder="Enter Token Symbol (e.g. PEPE)"
          value={token}
          onChange={(e) => setToken(e.target.value.toUpperCase())}
        />
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {data && (
        <div className="results">
          <div className="card judge">
            <h2>⚖️ The Judge's Verdict</h2>
            <div className={`verdict ${data.final_verdict.risk_level.toLowerCase()}`}>
              <h3>{data.final_verdict.verdict}</h3>
              <p>Risk Level: <strong>{data.final_verdict.risk_level}</strong></p>
              <p><em>"{data.final_verdict.reasoning}"</em></p>
            </div>
          </div>

          <div className="agents-grid">
            <div className="card listener">
              <h3>👂 Agent A: The Listener</h3>
              <p>Hype Score: <strong>{data.hype_analysis.hype_score}</strong></p>
              <p>Volume: {data.hype_analysis.trending_volume}</p>
              <p>Reddit Posts: {data.hype_analysis.details.reddit_data.posts}</p>
            </div>

            <div className="card analyst">
              <h3>🔎 Agent B: The Analyst</h3>
              <p>Smart Money: <strong>{data.onchain_analysis.net_smart_money_flow}</strong></p>
              <p>Net Flow: ${data.onchain_analysis.details.net_flow_usd ? data.onchain_analysis.details.net_flow_usd.toLocaleString() : "N/A"}</p>

              <div className="meta-info">
                <span className="badge chain">{data.onchain_analysis.details.chain_id}</span>
                <span className={`badge type ${data.onchain_analysis.details.tracking_type === 'Deep Whale Analysis' ? 'deep' : 'volume'}`}>
                  {data.onchain_analysis.details.tracking_type}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
