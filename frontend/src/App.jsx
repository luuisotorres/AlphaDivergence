import { useState, useEffect } from 'react'
import './App.css'
import Settings from './components/Settings'
import { analyzeToken } from './services/apiClient'
import { shouldShowSettings } from './utils/environment'

function App() {
  const [token, setToken] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [showBanner, setShowBanner] = useState(false)
  const [isCloudEnv, setIsCloudEnv] = useState(false)

  // Check if running in cloud environment and if API keys are configured
  useEffect(() => {
    const cloudEnv = shouldShowSettings();
    setIsCloudEnv(cloudEnv);

    // Only check for API keys and show banner if in cloud environment
    if (cloudEnv) {
      try {
        const keys = localStorage.getItem('alphadivergence_api_keys');
        const hasKeys = keys && JSON.parse(keys);
        const hasAnyKey = hasKeys && (hasKeys.openaiKey || hasKeys.geminiKey);

        if (!hasAnyKey) {
          setShowBanner(true);
        }
      } catch (error) {
        console.error('Error checking API keys:', error);
      }
    }
  }, []);

  const handleAnalyze = async () => {
    if (!token) return

    // Validate API keys when in cloud environment
    if (isCloudEnv) {
      try {
        const keys = localStorage.getItem('alphadivergence_api_keys');
        const parsedKeys = keys ? JSON.parse(keys) : null;
        const hasRequiredKey = parsedKeys && (
          (parsedKeys.openaiKey && parsedKeys.openaiKey.trim() !== '') ||
          (parsedKeys.geminiKey && parsedKeys.geminiKey.trim() !== '')
        );

        if (!hasRequiredKey) {
          setError('Please configure at least one API key (OpenAI or Gemini) in Settings before analyzing.');
          setShowBanner(true);
          return;
        }
      } catch (error) {
        console.error('Error checking API keys:', error);
        setError('Failed to validate API keys. Please check your configuration in Settings.');
        return;
      }
    }

    setLoading(true)
    setError(null)
    setData(null)

    try {
      const response = await analyzeToken(token)
      setData(response)
      setShowBanner(false) // Hide banner after successful analysis
    } catch (err) {
      const errorMsg = isCloudEnv
        ? "Failed to fetch analysis. Ensure backend is running and API keys are configured."
        : "Failed to fetch analysis. Ensure backend is running.";
      setError(errorMsg)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>AlphaDivergence</h1>
          <p className="subtitle">Multi-Agent Fake Hype Detector</p>
        </div>
        {isCloudEnv && (
          <button className="settings-btn" onClick={() => setSettingsOpen(true)} title="Configure API Keys">
            ⚙️
          </button>
        )}
      </div>

      {isCloudEnv && showBanner && (
        <div className="config-banner">
          <span>⚠️ Configure your API keys to unlock full functionality</span>
          <button onClick={() => setSettingsOpen(true)}>Configure Now</button>
        </div>
      )}

      <div className="search-box">
        <input
          type="text"
          placeholder="Enter Token Symbol (e.g. PEPE)"
          value={token}
          onChange={(e) => setToken(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
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

      {isCloudEnv && <Settings isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />}
    </div>
  )
}

export default App
