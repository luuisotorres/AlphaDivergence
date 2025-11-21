import axios from 'axios';
import { API_BASE_URL } from '../config';

/**
 * API Client with automatic API key injection from localStorage
 */

// Get API keys from localStorage
const getApiKeys = () => {
    try {
        const keys = localStorage.getItem('alphadivergence_api_keys');
        return keys ? JSON.parse(keys) : {};
    } catch (error) {
        console.error('Error reading API keys from localStorage:', error);
        return {};
    }
};

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
});

// Add request interceptor to inject API keys as headers
apiClient.interceptors.request.use(
    (config) => {
        const keys = getApiKeys();

        // Add API keys as custom headers if they exist
        if (keys.openaiKey) {
            config.headers['X-OpenAI-Key'] = keys.openaiKey;
        }
        if (keys.geminiKey) {
            config.headers['X-Gemini-Key'] = keys.geminiKey;
        }
        if (keys.etherscanKey) {
            config.headers['X-Etherscan-Key'] = keys.etherscanKey;
        }
        if (keys.redditClientId) {
            config.headers['X-Reddit-Client-Id'] = keys.redditClientId;
        }
        if (keys.redditClientSecret) {
            config.headers['X-Reddit-Client-Secret'] = keys.redditClientSecret;
        }
        if (keys.redditUserAgent) {
            config.headers['X-Reddit-User-Agent'] = keys.redditUserAgent;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// API methods
export const analyzeToken = async (tokenSymbol) => {
    const response = await apiClient.get(`/analyze/${tokenSymbol}`);
    return response.data;
};

export const healthCheck = async () => {
    const response = await apiClient.get('/health');
    return response.data;
};

export default apiClient;
