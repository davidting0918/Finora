/**
 * API Configuration
 * Centralized configuration for API endpoints and settings
 */

export interface ApiConfig {
  baseURL: string
  timeout: number
  headers: {
    'Content-Type': string
  }
}

export interface EnvironmentConfig {
  staging: ApiConfig
  production: ApiConfig
}

// Environment-specific API configurations
export const API_CONFIG: EnvironmentConfig = {
  staging: {
    baseURL: 'http://localhost:8000',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    }
  },
  production: {
    baseURL: 'https://api.finora.app',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    }
  }
}

// Environment detection
export const getEnvironment = (): 'staging' | 'production' => {
  // Check for environment variable first
  if (process.env.REACT_APP_ENV) {
    return process.env.REACT_APP_ENV as 'staging' | 'production'
  }

  // Default to staging for development
  if (process.env.NODE_ENV === 'development') {
    return 'staging'
  }

  // Production for built apps
  return 'production'
}

// Get current API configuration
export const getCurrentApiConfig = (): ApiConfig => {
  const environment = getEnvironment()
  return API_CONFIG[environment]
}

// API endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  auth: {
    googleLogin: '/auth/google/login',
    emailLogin: '/auth/email/login',
    accessToken: '/auth/access_token'
  },
  user: {
    create: '/user/create',  // User registration endpoint (requires API key)
    me: '/user/me'          // Get current user info (requires Bearer token)
  }
} as const
