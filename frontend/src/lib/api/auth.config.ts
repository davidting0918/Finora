/**
 * API Authentication Configuration
 * This file manages API keys and authentication settings for the frontend
 */

// API Keys for user creation endpoint
// In production, these should come from environment variables
export const API_AUTH_CONFIG = {
  // Default API key for user registration
  // TODO: Move these to environment variables in production
  defaultApiKey: process.env.REACT_APP_API_KEY || 'your-api-key-here',
  defaultApiSecret: process.env.REACT_APP_API_SECRET || 'your-api-secret-here',

  // API endpoints that require API key authentication
  apiKeyEndpoints: [
    '/user/create'  // User registration endpoint
  ]
} as const

/**
 * Check if an endpoint requires API key authentication
 * @param endpoint - The API endpoint path
 * @returns true if the endpoint requires API key authentication
 */
export const requiresApiKey = (endpoint: string): boolean => {
  return API_AUTH_CONFIG.apiKeyEndpoints.some(path => endpoint.includes(path))
}

/**
 * Get API authentication headers
 * @returns Object containing Authorization header with Bearer token format
 */
export const getApiAuthHeaders = () => {
  const { defaultApiKey, defaultApiSecret } = API_AUTH_CONFIG
  const bearerToken = `${defaultApiKey}:${defaultApiSecret}`

  return {
    'Authorization': `Bearer ${bearerToken}`
  }
}

/**
 * Validate API key configuration
 * @returns true if API keys are properly configured
 */
export const validateApiKeyConfig = (): boolean => {
  const { defaultApiKey, defaultApiSecret } = API_AUTH_CONFIG

  // Check if API keys are set and not default placeholder values
  const isApiKeyValid = defaultApiKey && defaultApiKey !== 'your-api-key-here'
  const isApiSecretValid = defaultApiSecret && defaultApiSecret !== 'your-api-secret-here'

  if (!isApiKeyValid || !isApiSecretValid) {
    console.warn('⚠️  API keys not properly configured. Please set REACT_APP_API_KEY and REACT_APP_API_SECRET environment variables.')
    return false
  }

  return true
}
