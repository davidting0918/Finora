import { useState, useEffect, useRef, useCallback } from 'react'

export interface ApiStatus {
  isOnline: boolean
  isChecking: boolean
  lastChecked: Date | null
  errorCount: number
}

interface UseApiStatusOptions {
  checkInterval?: number // in milliseconds
  baseUrl?: string
  timeout?: number
}

export function useApiStatus(options: UseApiStatusOptions = {}) {
  const {
    checkInterval = 30000, // 30 seconds default
    baseUrl = 'http://localhost:8000', // Default backend URL
    timeout = 5000 // 5 second timeout
  } = options

  const [status, setStatus] = useState<ApiStatus>({
    isOnline: true,
    isChecking: false,
    lastChecked: null,
    errorCount: 0
  })

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const checkApiStatus = useCallback(async () => {
    // Abort previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    const controller = new AbortController()
    abortControllerRef.current = controller

    setStatus(prev => ({ ...prev, isChecking: true }))

    try {
      // Try to hit a health check endpoint or any lightweight endpoint
      const response = await fetch(`${baseUrl}`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout using AbortController
      })

      // Create manual timeout
      const timeoutId = setTimeout(() => {
        controller.abort()
      }, timeout)

      const isOnline = response.ok && response.status >= 200 && response.status < 300

      clearTimeout(timeoutId)

      setStatus(prev => ({
        isOnline,
        isChecking: false,
        lastChecked: new Date(),
        errorCount: isOnline ? 0 : prev.errorCount + 1
      }))

    } catch (error) {
      // Only update status if the request wasn't aborted
      if (!controller.signal.aborted) {
        console.log('API Status Check Failed:', error)
        setStatus(prev => ({
          isOnline: false,
          isChecking: false,
          lastChecked: new Date(),
          errorCount: prev.errorCount + 1
        }))
      }
    }
  }, [baseUrl, timeout])

  const startMonitoring = useCallback(() => {
    // Initial check
    checkApiStatus()

    // Set up interval for continuous monitoring
    intervalRef.current = setInterval(checkApiStatus, checkInterval)
  }, [checkApiStatus, checkInterval])

  const stopMonitoring = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
  }, [])

  // Start monitoring on mount
  useEffect(() => {
    startMonitoring()
    return stopMonitoring
  }, [startMonitoring, stopMonitoring])

  // Manual check function for refresh button
  const forceCheck = useCallback(async () => {
    await checkApiStatus()
  }, [checkApiStatus])

  return {
    ...status,
    forceCheck,
    startMonitoring,
    stopMonitoring
  }
}
