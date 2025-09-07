/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { apiClient } from '../client'
import { API_ENDPOINTS } from '../config'
import type {
  ApiResponse,
  EmailLoginRequest,
  GoogleLoginRequest,
  OAuth2LoginRequest,
  CreateUserRequest,
  LoginResponse,
  TokenResponse
} from '../../types'
import { userService } from './user'

export class AuthService {
  /**
   * Login with email and password
   */
  async loginWithEmail(credentials: EmailLoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>(
      API_ENDPOINTS.auth.emailLogin,
      credentials
    )

    // Store token after successful login
    apiClient.setToken(response.data.access_token)

    return response.data
  }

  /**
   * Login with Google OAuth token
   */
  async loginWithGoogle(googleRequest: GoogleLoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>(
      API_ENDPOINTS.auth.googleLogin,
      googleRequest
    )

    // Store token after successful login
    apiClient.setToken(response.data.access_token)

    return response.data
  }

  /**
   * Sign up with email and password
   * This creates a new user account, then automatically logs them in
   */
  async signupWithEmail(signupData: CreateUserRequest): Promise<LoginResponse> {
    // Step 1: Create user account using API key authentication
    await userService.createUser(signupData)

    // Step 2: Log in the newly created user
    const loginData: EmailLoginRequest = {
      email: signupData.email,
      pwd: signupData.pwd
    }

    const response = await this.loginWithEmail(loginData)

    return response
  }


  /**
   * Get access token using OAuth2 flow (username/password)
   */
  async getAccessToken(credentials: OAuth2LoginRequest): Promise<TokenResponse> {
    // OAuth2 expects form data
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await apiClient.post<ApiResponse<TokenResponse>>(
      API_ENDPOINTS.auth.accessToken,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    return response.data
  }

  /**
   * Logout user - clears token from storage
   */
  logout(): void {
    apiClient.clearToken()
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return apiClient.isAuthenticated()
  }

  /**
   * Get stored token
   */
  getToken(): string | null {
    return apiClient.getStoredToken()
  }
}

// Export singleton instance
export const authService = new AuthService()
export default authService
