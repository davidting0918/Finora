/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authService } from '../api'
import type { AuthUser, EmailLoginRequest, GoogleLoginRequest, CreateUserRequest } from '../types'

interface AuthContextType {
  // State
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Methods
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: (googleToken: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!token && !!user

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth()
  }, [])

  /**
   * Initialize authentication state from stored data
   */
  const initializeAuth = async () => {
    try {
      const storedToken = authService.getToken()
      const storedUserInfo = localStorage.getItem('finora_user_info')

      if (storedToken && storedUserInfo) {
        const userData = JSON.parse(storedUserInfo)
        setToken(storedToken)
        setUser({
          id: userData.id,
          email: userData.email,
          name: userData.name
        })
      }
    } catch (error) {
      console.error('Error initializing auth:', error)
      await logout()
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Login with email and password
   */
  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true)

    try {
      const credentials: EmailLoginRequest = { email, pwd: password }
      const response = await authService.loginWithEmail(credentials)

      // Set auth state
      setToken(response.access_token)
      setUser(response.user)

      // Store user info for persistence
      localStorage.setItem('finora_user_info', JSON.stringify({
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        created_at: Date.now(),
        updated_at: Date.now(),
        is_active: true,
        source: 'email'
      }))

    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Login with Google OAuth token
   */
  const loginWithGoogle = async (googleToken: string): Promise<void> => {
    setIsLoading(true)

    try {
      const googleRequest: GoogleLoginRequest = { token: googleToken }
      const response = await authService.loginWithGoogle(googleRequest)

      // Set auth state
      setToken(response.access_token)
      setUser(response.user)

      // Store user info for persistence
      localStorage.setItem('finora_user_info', JSON.stringify({
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        created_at: Date.now(),
        updated_at: Date.now(),
        is_active: true,
        source: 'google'
      }))

    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Sign up with email and password
   */
  const signup = async (name: string, email: string, password: string): Promise<void> => {
    setIsLoading(true)

    try {
      const signupData: CreateUserRequest = { name, email, pwd: password }
      const response = await authService.signupWithEmail(signupData)

      // Set auth state
      setToken(response.access_token)
      setUser(response.user)

      // Store user info for persistence
      localStorage.setItem('finora_user_info', JSON.stringify({
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        created_at: Date.now(),
        updated_at: Date.now(),
        is_active: true,
        source: 'email'
      }))

    } catch (error) {
      console.error('Signup failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }


  /**
   * Logout user - clear all auth data
   */
  const logout = async (): Promise<void> => {
    setIsLoading(true)

    try {
      // Clear API client token
      authService.logout()

      // Clear localStorage data
      localStorage.removeItem('finora_user_info')

      // Clear local state
      setToken(null)
      setUser(null)

    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const value: AuthContextType = {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,

    // Methods
    login,
    loginWithGoogle,
    signup,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * Hook to use authentication context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}

export default AuthContext
