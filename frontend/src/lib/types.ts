// =============================================================================
// Authentication & User Types
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

export interface CreateUserRequest {
  name: string
  email: string
  pwd: string  // Backend expects 'pwd', not 'password'
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
// API Response Wrapper (Backend Format)
// =============================================================================

export interface ApiResponse<T> {
  status: number
  data: T
  message: string
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
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

// =============================================================================
// Local Storage Keys (constants)
// =============================================================================

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'finora_access_token',
  USER_INFO: 'finora_user_info',
  TOKEN_EXPIRY: 'finora_token_expiry'
} as const
