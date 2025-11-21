// Environment detection utility
// Determines if the app is running in a cloud environment (Render) vs local Docker

/**
 * Checks if the application is running in a cloud deployment environment
 * @returns {boolean} true if running on Render or similar cloud platform
 */
export const isCloudDeployment = () => {
    // Check for Render-specific environment indicator
    // Render sets the hostname to include .onrender.com
    const hostname = window.location.hostname;

    // Cloud deployment indicators:
    // 1. Hostname includes .onrender.com (Render)
    // 2. Hostname is not localhost or 127.0.0.1
    // 3. Protocol is https (cloud deployments typically use HTTPS)

    const isRender = hostname.includes('.onrender.com');
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
    const isHttps = window.location.protocol === 'https:';

    // Consider it a cloud deployment if:
    // - It's on Render, OR
    // - It's HTTPS and not localhost (covers other cloud providers)
    return isRender || (isHttps && !isLocalhost);
};

/**
 * Checks if Settings UI should be shown
 * Settings are only needed for cloud deployments where users configure their own API keys
 * @returns {boolean} true if Settings UI should be displayed
 */
export const shouldShowSettings = () => {
    return isCloudDeployment();
};
