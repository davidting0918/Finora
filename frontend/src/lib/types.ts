// =============================================================================
// Authentication & User Types (Login-focused)
// =============================================================================

export interface User {
  id: string
  email: string
  name: string
  created_at: number
  updated_at: number
  is_active: boolean
  source?: string
  google_id?: string
}

export interface AuthUser {
  id: string
  email: string
  name: string
}

// =============================================================================
// Login Request Types
// =============================================================================

export interface EmailLoginRequest {
  email: string
  pwd: string
}

export interface GoogleLoginRequest {
  token: string
}

export interface OAuth2LoginRequest {
  username: string
  password: string
}

// =============================================================================
// Login Response Types
// =============================================================================

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// =============================================================================
// Google Auth Types
// =============================================================================

export interface GoogleUserInfo {
  id: string
  email: string
  name: string
  picture: string
}

// =============================================================================
// Token Management
// =============================================================================

export interface AccessToken {
  token: string
  user_id: string
  created_at: number
  expires_at: number
  is_active: boolean
}

// =============================================================================
// API Response Wrapper
// =============================================================================

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// =============================================================================
// Error Handling
// =============================================================================

export interface AuthError {
  message: string
  status: number
  detail?: string
}

export interface ValidationError {
  field: string
  message: string
}

// =============================================================================
// Auth Context Types (for React context)
// =============================================================================

export interface AuthContextType {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: (googleToken: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

// =============================================================================
// Local Storage Keys (constants)
// =============================================================================

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'finora_access_token',
  USER_INFO: 'finora_user_info',
  TOKEN_EXPIRY: 'finora_token_expiry'
} as const
