import { useState, useEffect } from 'react';
import './Settings.css';

function Settings({ isOpen, onClose }) {
    const [apiKeys, setApiKeys] = useState({
        openaiKey: '',
        geminiKey: '',
        etherscanKey: '',
        redditClientId: '',
        redditClientSecret: '',
        redditUserAgent: 'AlphaDivergence/1.0'
    });

    const [showKeys, setShowKeys] = useState({
        openaiKey: false,
        geminiKey: false,
        etherscanKey: false,
        redditClientId: false,
        redditClientSecret: false
    });

    const [saveMessage, setSaveMessage] = useState('');

    // Load API keys from localStorage on mount
    useEffect(() => {
        try {
            const stored = localStorage.getItem('alphadivergence_api_keys');
            if (stored) {
                setApiKeys(JSON.parse(stored));
            }
        } catch (error) {
            console.error('Error loading API keys:', error);
        }
    }, [isOpen]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setApiKeys(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const toggleShowKey = (keyName) => {
        setShowKeys(prev => ({
            ...prev,
            [keyName]: !prev[keyName]
        }));
    };

    const handleSave = () => {
        try {
            localStorage.setItem('alphadivergence_api_keys', JSON.stringify(apiKeys));
            setSaveMessage('✅ API Keys saved successfully!');
            setTimeout(() => setSaveMessage(''), 3000);
        } catch (error) {
            console.error('Error saving API keys:', error);
            setSaveMessage('❌ Error saving API keys');
            setTimeout(() => setSaveMessage(''), 3000);
        }
    };

    const handleClear = () => {
        if (window.confirm('Are you sure you want to clear all API keys?')) {
            setApiKeys({
                openaiKey: '',
                geminiKey: '',
                etherscanKey: '',
                redditClientId: '',
                redditClientSecret: '',
                redditUserAgent: 'AlphaDivergence/1.0'
            });
            localStorage.removeItem('alphadivergence_api_keys');
            setSaveMessage('🗑️ API Keys cleared');
            setTimeout(() => setSaveMessage(''), 3000);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="settings-overlay" onClick={onClose}>
            <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
                <div className="settings-header">
                    <h2>⚙️ API Configuration</h2>
                    <button className="close-btn" onClick={onClose}>✕</button>
                </div>

                <div className="settings-content">
                    <p className="settings-description">
                        Configure your API keys to unlock full functionality. Keys are stored locally in your browser.
                    </p>

                    <div className="settings-section">
                        <h3>🤖 AI Models (Required)</h3>
                        <p className="section-note">At least one AI model key is required for analysis</p>

                        <div className="input-group">
                            <label htmlFor="openaiKey">OpenAI API Key</label>
                            <div className="input-with-toggle">
                                <input
                                    type={showKeys.openaiKey ? "text" : "password"}
                                    id="openaiKey"
                                    name="openaiKey"
                                    value={apiKeys.openaiKey}
                                    onChange={handleInputChange}
                                    placeholder="sk-..."
                                />
                                <button
                                    type="button"
                                    className="toggle-visibility"
                                    onClick={() => toggleShowKey('openaiKey')}
                                >
                                    {showKeys.openaiKey ? '👁️' : '👁️‍🗨️'}
                                </button>
                            </div>
                        </div>

                        <div className="input-group">
                            <label htmlFor="geminiKey">Google Gemini API Key</label>
                            <div className="input-with-toggle">
                                <input
                                    type={showKeys.geminiKey ? "text" : "password"}
                                    id="geminiKey"
                                    name="geminiKey"
                                    value={apiKeys.geminiKey}
                                    onChange={handleInputChange}
                                    placeholder="AI..."
                                />
                                <button
                                    type="button"
                                    className="toggle-visibility"
                                    onClick={() => toggleShowKey('geminiKey')}
                                >
                                    {showKeys.geminiKey ? '👁️' : '👁️‍🗨️'}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="settings-section">
                        <h3>🔗 Blockchain Data (Optional)</h3>
                        <p className="section-note">Enables deep whale tracking for Ethereum tokens</p>

                        <div className="input-group">
                            <label htmlFor="etherscanKey">Etherscan API Key</label>
                            <div className="input-with-toggle">
                                <input
                                    type={showKeys.etherscanKey ? "text" : "password"}
                                    id="etherscanKey"
                                    name="etherscanKey"
                                    value={apiKeys.etherscanKey}
                                    onChange={handleInputChange}
                                    placeholder="Your Etherscan API Key"
                                />
                                <button
                                    type="button"
                                    className="toggle-visibility"
                                    onClick={() => toggleShowKey('etherscanKey')}
                                >
                                    {showKeys.etherscanKey ? '👁️' : '👁️‍🗨️'}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="settings-section">
                        <h3>🗣️ Social Data (Optional)</h3>
                        <p className="section-note">Enables faster Reddit scraping (RSS fallback available)</p>

                        <div className="input-group">
                            <label htmlFor="redditClientId">Reddit Client ID</label>
                            <div className="input-with-toggle">
                                <input
                                    type={showKeys.redditClientId ? "text" : "password"}
                                    id="redditClientId"
                                    name="redditClientId"
                                    value={apiKeys.redditClientId}
                                    onChange={handleInputChange}
                                    placeholder="Your Reddit Client ID"
                                />
                                <button
                                    type="button"
                                    className="toggle-visibility"
                                    onClick={() => toggleShowKey('redditClientId')}
                                >
                                    {showKeys.redditClientId ? '👁️' : '👁️‍🗨️'}
                                </button>
                            </div>
                        </div>

                        <div className="input-group">
                            <label htmlFor="redditClientSecret">Reddit Client Secret</label>
                            <div className="input-with-toggle">
                                <input
                                    type={showKeys.redditClientSecret ? "text" : "password"}
                                    id="redditClientSecret"
                                    name="redditClientSecret"
                                    value={apiKeys.redditClientSecret}
                                    onChange={handleInputChange}
                                    placeholder="Your Reddit Client Secret"
                                />
                                <button
                                    type="button"
                                    className="toggle-visibility"
                                    onClick={() => toggleShowKey('redditClientSecret')}
                                >
                                    {showKeys.redditClientSecret ? '👁️' : '👁️‍🗨️'}
                                </button>
                            </div>
                        </div>

                        <div className="input-group">
                            <label htmlFor="redditUserAgent">Reddit User Agent</label>
                            <input
                                type="text"
                                id="redditUserAgent"
                                name="redditUserAgent"
                                value={apiKeys.redditUserAgent}
                                onChange={handleInputChange}
                                placeholder="AlphaDivergence/1.0"
                            />
                        </div>
                    </div>

                    {saveMessage && (
                        <div className="save-message">{saveMessage}</div>
                    )}

                    <div className="settings-actions">
                        <button className="btn-save" onClick={handleSave}>
                            💾 Save Configuration
                        </button>
                        <button className="btn-clear" onClick={handleClear}>
                            🗑️ Clear All
                        </button>
                    </div>

                    <div className="settings-footer">
                        <p>
                            <strong>🔒 Privacy:</strong> API keys are stored locally in your browser and sent to our backend only for authentication with external API providers.
                            They are never persisted or stored server-side.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Settings;
