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
// Transaction Types
// =============================================================================

export enum TransactionType {
  INCOME = 'income',
  EXPENSE = 'expense'
}

export interface Transaction {
  id: string
  user_id: string
  amount: number
  description: string
  transaction_type: TransactionType
  category_id: string
  subcategory_id?: string
  transaction_date: string // ISO date string
  tags?: string[]
  created_at: string
  updated_at: string
}

export interface CreateTransactionRequest {
  amount: number
  description: string
  transaction_type: TransactionType
  category_id: string
  subcategory_id?: string
  transaction_date: string
  tags?: string[]
}

export interface UpdateTransactionRequest {
  amount?: number
  description?: string
  transaction_type?: TransactionType
  category_id?: string
  subcategory_id?: string
  transaction_date?: string
  tags?: string[]
}

export interface TransactionListQuery {
  page: number
  limit: number
  start_date?: string
  end_date?: string
  transaction_type?: TransactionType
  category_id?: string
  subcategory_id?: string
  sort_by: string
  sort_order: 'asc' | 'desc'
}

export interface TransactionListResponse {
  transactions: Transaction[]
  pagination: {
    total: number
    page: number
    limit: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface Category {
  id: string
  name: string
  icon?: string
  emoji?: string
  subcategories?: Subcategory[]
}

export interface Subcategory {
  id: string
  name: string
  category_id: string
}

// =============================================================================
// Analytics Types
// =============================================================================

export enum AnalyticsPeriod {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly'
}

export interface AnalyticsQuery {
  start_date?: string
  end_date?: string
  period?: AnalyticsPeriod
  transaction_type?: TransactionType
  category_id?: string
}

export interface FinancialSummary {
  total_income: number
  total_expense: number
  net_income: number
  transaction_count: number
  average_transaction: number
  period_start: string
  period_end: string
}

export interface CategoryBreakdown {
  category_id: string
  category_name: string
  total_amount: number
  transaction_count: number
  percentage: number
  subcategories?: {
    subcategory_id: string
    subcategory_name: string
    total_amount: number
    transaction_count: number
    percentage: number
  }[]
}

export interface SpendingTrend {
  period: string
  total_income: number
  total_expense: number
  net_income: number
  transaction_count: number
}

export interface TagAnalytics {
  tag: string
  total_amount: number
  transaction_count: number
  average_amount: number
}

export interface AnalyticsOverview {
  financial_summary: FinancialSummary
  spending_trends: SpendingTrend[]
  category_breakdown: CategoryBreakdown[]
  top_categories: {
    category_id: string
    category_name: string
    total_amount: number
    transaction_count: number
  }[]
}

// =============================================================================
// Form Data Types (for frontend forms)
// =============================================================================

export interface TransactionFormData {
  type: 'income' | 'expense'
  amount: string
  description: string
  category: string
  subcategory?: string
  date: string
  tags?: string
}

// =============================================================================
// Local Storage Keys (constants)
// =============================================================================

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'finora_access_token',
  USER_INFO: 'finora_user_info',
  TOKEN_EXPIRY: 'finora_token_expiry'
} as const
