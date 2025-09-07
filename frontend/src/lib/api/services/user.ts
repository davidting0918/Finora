/**
 * User Service
 * Handles user-related API calls
 */

import { apiClient } from '../client'
import { API_ENDPOINTS } from '../config'
import type {
  ApiResponse,
  CreateUserRequest,
  User
} from '../../types'

export class UserService {
  /**
   * Create a new user account
   * Note: Bearer token with API key:secret format is automatically added by the API client
   * for this endpoint. Format: Authorization: Bearer {key}:{secret}
   */
  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<ApiResponse<User>>(
      API_ENDPOINTS.user.create,
      userData
    )

    return response.data
  }

  /**
   * Get current user information
   * Requires user authentication token
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>(
      API_ENDPOINTS.user.me
    )

    return response.data
  }
}

// Export singleton instance
export const userService = new UserService()
export default userService
