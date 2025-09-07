import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

// Class name merging utility function - used by the GlassCard component on the login page
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 可選：簡單的本地存儲工具函數，用於保存登錄狀態
export function getStoredValue<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue

  try {
    const item = window.localStorage.getItem(key)
    return item ? JSON.parse(item) : defaultValue
  } catch (error) {
    console.warn(`Error reading localStorage key "${key}":`, error)
    return defaultValue
  }
}

export function setStoredValue<T>(key: string, value: T): void {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.warn(`Error setting localStorage key "${key}":`, error)
  }
}

export function removeStoredValue(key: string): void {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.removeItem(key)
  } catch (error) {
    console.warn(`Error removing localStorage key "${key}":`, error)
  }
}

// 簡單的表單驗證輔助函數
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 密碼強度檢查（如果需要的話）
export function getPasswordStrength(password: string): {
  score: number
  label: string
  color: string
} {
  if (!password) return { score: 0, label: 'No password', color: 'text-gray-400' }

  let score = 0

  // 長度檢查
  if (password.length >= 6) score++
  if (password.length >= 10) score++

  // Character type checks
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/\d/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++

  const levels = [
    { label: 'Very Weak', color: 'text-red-500' },
    { label: 'Weak', color: 'text-red-400' },
    { label: 'Fair', color: 'text-yellow-500' },
    { label: 'Good', color: 'text-blue-500' },
    { label: 'Strong', color: 'text-green-500' },
    { label: 'Very Strong', color: 'text-green-600' }
  ]

  const level = Math.min(score, levels.length - 1)
  return { score, ...levels[level] }
}
