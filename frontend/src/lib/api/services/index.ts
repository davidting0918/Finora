/**
 * API Services Index
 * Central export point for API services
 */

import { authService } from './auth'
import { userService } from './user'
import { transactionService } from './transaction'
import { analyticsService } from './analytics'

// Export services
export { AuthService, authService } from './auth'
export { UserService, userService } from './user'
export { TransactionService, transactionService } from './transaction'
export { AnalyticsService, analyticsService } from './analytics'

// Export API object with all services
export const api = {
  auth: authService,
  user: userService,
  transaction: transactionService,
  analytics: analyticsService
}

export default api
