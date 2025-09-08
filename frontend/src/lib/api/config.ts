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

export interface GoogleConfig {
  clientId: string
}

export interface AppConfig extends ApiConfig {
  google: GoogleConfig
}

export interface EnvironmentConfig {
  staging: AppConfig
  production: AppConfig
}

// Environment-specific configurations
export const APP_CONFIG: EnvironmentConfig = {
  staging: {
    baseURL: 'http://localhost:8000',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    },
    google: {
      clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || ''
    }
  },
  production: {
    baseURL: 'https://api.finora.app',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    },
    google: {
      clientId: (() => {
        if (!process.env.REACT_APP_GOOGLE_CLIENT_ID) {
          throw new Error('REACT_APP_GOOGLE_CLIENT_ID must be set in production environment');
        }
        return process.env.REACT_APP_GOOGLE_CLIENT_ID;
      })()
    }
  }
}

// Backward compatibility - keep the old API_CONFIG for existing code
export const API_CONFIG: EnvironmentConfig = APP_CONFIG

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

// Get current API configuration (backward compatibility)
export const getCurrentApiConfig = (): ApiConfig => {
  const environment = getEnvironment()
  return APP_CONFIG[environment]
}

// Get current app configuration (includes Google config)
export const getCurrentAppConfig = (): AppConfig => {
  const environment = getEnvironment()
  return APP_CONFIG[environment]
}

// Get Google configuration
export const getGoogleConfig = (): GoogleConfig => {
  const config = getCurrentAppConfig()
  return config.google
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
  },
  // Transaction endpoints
  transaction: {
    create: '/transaction/create',
    info: '/transaction/info',           // GET /transaction/info/{transaction_id}
    list: '/transaction/list',
    update: '/transaction/update',       // POST /transaction/update/{transaction_id}
    delete: '/transaction/delete',       // POST /transaction/delete/{transaction_id}
    categories: '/transaction/category',
    subcategories: '/transaction/subcategory' // GET /transaction/subcategory/{category_id}
  },
  // Analytics endpoints
  analytics: {
    overview: '/analytics/overview',
    categoryBreakdown: '/analytics/category-breakdown',
    spendingTrends: '/analytics/spending-trends',
    financialSummary: '/analytics/financial-summary',
    tagAnalytics: '/analytics/tag-analytics'
  }
} as const
