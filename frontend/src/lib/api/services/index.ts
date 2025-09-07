/**
 * API Services Index
 * Central export point for API services
 */

import { authService } from './auth'
import { userService } from './user'

// Export services
export { AuthService, authService } from './auth'
export { UserService, userService } from './user'

// Export API object with all services

export const api = {
  auth: authService,
  user: userService
}

export default api
