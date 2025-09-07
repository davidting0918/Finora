import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  ArrowRight,
  Sparkles,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { AuthLayout } from '../components/layout/AuthLayout'
import { GlassCard } from '../components/ui/GlassCard'
import { useAuth } from '../lib/contexts/AuthContext'
import { googleAuthService } from '../lib/services/googleAuth'
import type { ApiError } from '../lib/api'

// Form validation schema
const loginSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid email address' }),
  password: z.string().min(6, 'Password must be at least 6 characters')
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [isGoogleInitialized, setIsGoogleInitialized] = useState(false)
  const navigate = useNavigate()
  const { login, loginWithGoogle, isAuthenticated } = useAuth()
  const googleInitialized = useRef(false)

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  })

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  // Initialize Google OAuth on component mount
  useEffect(() => {
    const initializeGoogle = async () => {
      if (googleInitialized.current) return

      try {
        console.log('🔧 Starting Google OAuth initialization...')
        console.log('🔍 Google Client ID:', googleAuthService.getClientId())

        await googleAuthService.initializeGoogle()
        googleAuthService.initializeGoogleSignIn({
          onSuccess: handleGoogleSuccess,
          onError: handleGoogleError,
        })

        // Also render a native Google button as fallback
        setTimeout(() => {
          try {
            googleAuthService.renderButton('google-signin-button', {
              onSuccess: handleGoogleSuccess,
              onError: handleGoogleError,
            })
            console.log('✅ Native Google button rendered successfully')
          } catch (error) {
            console.warn('⚠️ Failed to render native Google button (this is optional):', error)
          }
        }, 100)

        setIsGoogleInitialized(true)
        googleInitialized.current = true
        console.log('✅ Google OAuth initialized successfully')
      } catch (error) {
        console.error('❌ Failed to initialize Google OAuth:', error)
        setErrorMessage('Failed to initialize Google Sign-In')
      }
    }

    initializeGoogle()
  }, [])

  // Handle Google OAuth success
  const handleGoogleSuccess = async (credential: string) => {
    console.log('🎯 handleGoogleSuccess called with credential length:', credential?.length)
    setErrorMessage('')

    try {
      console.log('🔐 Google credential received, calling loginWithGoogle...')
      console.log('🔍 Credential preview:', credential.substring(0, 50) + '...')

      await loginWithGoogle(credential)
      console.log('✅ Google login successful, navigating to dashboard')
      navigate('/dashboard')
    } catch (error) {
      const apiError = error as ApiError
      console.error('❌ Google login failed:', error)
      console.error('❌ Error details:', {
        message: apiError.message,
        status: apiError.status,
        details: apiError.details
      })
      setErrorMessage(apiError.message || 'Google login failed')
    }
  }

  // Handle Google OAuth error
  const handleGoogleError = (error: string) => {
    console.error('❌ Google OAuth error:', error)
    setErrorMessage(error || 'Google authentication failed')
  }

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setErrorMessage('')

    try {
      await login(data.email, data.password)
      navigate('/dashboard')
    } catch (error) {
      const apiError = error as ApiError
      setErrorMessage(apiError.message || 'Login failed, please check your email and password')
      console.error('Login error:', error)
    } finally {
      setIsLoading(false)
    }
  }


  return (
    <AuthLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <GlassCard className="relative overflow-hidden">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-center mb-8"
          >
            <motion.div
              animate={{
                rotate: [0, 5, -5, 0],
                scale: [1, 1.05, 1]
              }}
              transition={{ duration: 4, repeat: Infinity }}
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl mb-4"
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>

            <h1 className="text-2xl font-bold text-white mb-2">
              Welcome Back! 👋
            </h1>
            <p className="text-gray-400">
              Sign in to continue to your financial dashboard
            </p>
          </motion.div>

          {/* Google Login Button */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="mb-6"
          >
            {/* Native Google Button */}
            {isGoogleInitialized ? (
              <div className="relative">
                <div id="google-signin-button" className="w-full flex justify-center"></div>
              </div>
            ) : (
              <div className="w-full flex items-center justify-center space-x-3 p-3 rounded-lg bg-white border border-gray-300 opacity-50">
                <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
                <span className="font-medium text-gray-700">Initializing Google Sign-In...</span>
              </div>
            )}
          </motion.div>

          {/* Divider */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="relative mb-6"
          >
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-900 text-gray-400">or continue with email</span>
            </div>
          </motion.div>

          {/* Error Message */}
          <AnimatePresence>
            {errorMessage && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-red-900/30 border border-red-500 rounded-lg p-4 mb-6"
              >
                <div className="flex items-center space-x-2 text-red-400">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-sm">{errorMessage}</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email Field */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium text-gray-300">
                Email Address
              </label>
              <div className="relative">
                <motion.div
                  animate={{
                    scale: errors.email ? [1, 1.05, 1] : 1,
                  }}
                  transition={{ duration: 0.3 }}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2"
                >
                  <Mail className={`w-5 h-5 ${
                    errors.email ? 'text-red-400' : 'text-gray-400'
                  }`} />
                </motion.div>
                <input
                  {...register('email')}
                  type="email"
                  placeholder="user@example.com"
                  className={`w-full pl-10 pr-4 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all ${
                    errors.email
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-gray-700 focus:border-blue-500 focus:ring-blue-500/20'
                  }`}
                />
              </div>
              <AnimatePresence>
                {errors.email && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center space-x-2 text-red-400 text-sm"
                  >
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.email.message}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Password Field */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="space-y-2"
            >
              <label className="block text-sm font-medium text-gray-300">
                Password
              </label>
              <div className="relative">
                <motion.div
                  animate={{
                    scale: errors.password ? [1, 1.05, 1] : 1,
                  }}
                  transition={{ duration: 0.3 }}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2"
                >
                  <Lock className={`w-5 h-5 ${
                    errors.password ? 'text-red-400' : 'text-gray-400'
                  }`} />
                </motion.div>
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  className={`w-full pl-10 pr-12 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all ${
                    errors.password
                      ? 'border-red-500 focus:ring-red-500/20'
                      : 'border-gray-700 focus:border-blue-500 focus:ring-blue-500/20'
                  }`}
                />
                <motion.button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </motion.button>
              </div>
              <AnimatePresence>
                {errors.password && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center space-x-2 text-red-400 text-sm"
                  >
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.password.message}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Forgot Password */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="flex justify-end"
            >
              <Link
                to="/forgot-password"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot your password?
              </Link>
            </motion.div>

            {/* Submit Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={!isLoading ? { scale: 1.02 } : {}}
                whileTap={!isLoading ? { scale: 0.98 } : {}}
                className="w-full flex items-center justify-center space-x-2 p-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg font-medium text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="flex items-center space-x-2"
                    >
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Signing in...</span>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="signin"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="flex items-center space-x-2"
                    >
                      <span>Sign In</span>
                      <ArrowRight className="w-5 h-5" />
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            </motion.div>
          </form>

          {/* Sign Up Link */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            className="mt-6 text-center"
          >
            <p className="text-gray-400">
              Don&apos;t have an account?{' '}
              <Link
                to="/signup"
                className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
              >
                Sign up
              </Link>
            </p>
          </motion.div>

          {/* Floating particles */}
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              animate={{
                y: [0, -20, 0],
                opacity: [0.3, 1, 0.3],
                scale: [0, 1, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.8,
              }}
              className="absolute w-1 h-1 bg-blue-400 rounded-full"
              style={{
                left: `${20 + i * 40}%`,
                top: `${10 + i * 15}%`,
              }}
            />
          ))}
        </GlassCard>
      </motion.div>
    </AuthLayout>
  )
}
