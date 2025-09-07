/**
 * API Module Index
 * Central export point for the entire API module
 */

// Export configuration
export { API_CONFIG, API_ENDPOINTS, getCurrentApiConfig, getCurrentAppConfig, getGoogleConfig, getEnvironment } from './config'

// Export client
export { ApiClient, apiClient, type ApiError } from './client'

// Export all services
export * from './services'

// Export default API object for convenience
export { default as api } from './services'
