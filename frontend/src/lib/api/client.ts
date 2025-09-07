/**
 * API Client
 * Base HTTP client with authentication and error handling
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'
import { getCurrentApiConfig, getEnvironment } from './config'
import { requiresApiKey, getApiAuthHeaders, validateApiKeyConfig } from './auth.config'

// Token management
const TOKEN_KEY = 'finora_access_token'
const TOKEN_TYPE = 'Bearer'

export class ApiClient {
  private instance: AxiosInstance

  constructor() {
    const config = getCurrentApiConfig()

    this.instance = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: config.headers
    })

    this.setupInterceptors()

    // Validate API key configuration on startup
    validateApiKeyConfig()
  }

  private setupInterceptors() {
    // Request interceptor for authentication
    this.instance.interceptors.request.use(
      (config) => {
        // Check if this endpoint requires API key authentication
        if (config.url && requiresApiKey(config.url)) {
          // For API key endpoints, use API key Bearer token
          const apiAuthHeaders = getApiAuthHeaders()
          Object.assign(config.headers, apiAuthHeaders)

          // Log API key usage in staging
          if (getEnvironment() === 'staging') {
            console.log('🔑 Using API key Bearer token for:', config.url)
          }
        } else {
          // For regular endpoints, use user Bearer token if available
          const token = this.getStoredToken()
          if (token) {
            config.headers.Authorization = `${TOKEN_TYPE} ${token}`
          }
        }

        // Log requests in staging environment
        if (getEnvironment() === 'staging') {
          console.log('🚀 API Request:', {
            method: config.method?.toUpperCase(),
            url: `${config.baseURL}${config.url}`,
            data: config.data,
            headers: {
              ...config.headers,
              // Hide sensitive data in logs
              'Authorization': config.headers.Authorization ? '[REDACTED]' : undefined
            }
          })
        }

        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response) => {
        // Log responses in staging environment
        if (getEnvironment() === 'staging') {
          console.log('✅ API Response:', {
            status: response.status,
            url: response.config.url,
            data: response.data
          })
        }

        return response
      },
      (error: AxiosError) => {
        // Handle specific error cases
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          this.clearToken()
          window.location.href = '/login'
        }

        // Log errors in staging environment
        if (getEnvironment() === 'staging') {
          console.error('❌ API Error:', {
            status: error.response?.status,
            url: error.config?.url,
            message: error.message,
            data: error.response?.data
          })
        }

        return Promise.reject(this.formatError(error))
      }
    )
  }

  private formatError(error: AxiosError): ApiError {
    if (error.response?.data) {
      return {
        message: (error.response.data as any).detail || error.message,
        status: error.response.status,
        details: error.response.data
      }
    }

    return {
      message: error.message || 'Network error occurred',
      status: 0,
      details: null
    }
  }

  // Token management methods
  public setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  }

  public getStoredToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  public clearToken(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem('finora_user_info')
  }

  public isAuthenticated(): boolean {
    return !!this.getStoredToken()
  }

  // HTTP methods
  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config)
    return response.data
  }

  public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config)
    return response.data
  }

  public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config)
    return response.data
  }

  public async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.patch<T>(url, data, config)
    return response.data
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config)
    return response.data
  }
}

// Error interface
export interface ApiError {
  message: string
  status: number
  details: any
}

// Create and export singleton instance
export const apiClient = new ApiClient()

// Export default for convenience
export default apiClient
