import { useState, useEffect, useRef, useCallback } from 'react'
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
  Loader2,
  Gem
} from 'lucide-react'
import { GlassCard } from '../components/ui/GlassCard'
import { useAuth } from '../lib/contexts/AuthContext'
import { googleAuthService } from '../lib/services/googleAuth'
import ParticleRing from '../components/effects/ParticleRing'
import type { ApiError } from '../lib/api'

// Form validation schema
const loginSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid email address' }),
  password: z.string().min(6, 'Password must be at least 6 characters')
})

type LoginFormData = z.infer<typeof loginSchema>


// Enhanced Auth Layout with Luxury Left Side
function LuxuryAuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* Left Side - Dark Luxury Branding */}
      <motion.div
        initial={{ opacity: 0, x: -100 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 1.2, ease: [0.23, 1, 0.32, 1] }}
        className="hidden lg:flex flex-1 relative overflow-hidden bg-gradient-to-br from-slate-950 via-gray-950 to-black"
      >
        {/* Dark Luxury Background Effects */}
        <div className="absolute inset-0">
          {/* Base texture */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 via-gray-900/30 to-black/50" />

          {/* Noise texture overlay */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
              backgroundSize: '256px 256px'
            }}
          />

          {/* Subtle diamond pattern */}
          <div className="absolute inset-0 opacity-[0.015]">
            <div className="w-full h-full" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%233b82f6' fill-opacity='0.1'%3E%3Cpath d='M30 0l30 30-30 30L0 30z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              backgroundSize: '60px 60px'
            }} />
          </div>
        </div>

        {/* 3D 粒子環效果 - 替代浮動球體 */}
        <div className="absolute inset-0 overflow-hidden z-0">
          <ParticleRing
            height="100vh"
            autoRotate={true}
            interactive={true}
            cameraPosition={[12, -8, -6]}
            ambientIntensity={0.2}
            className="opacity-60"
            showHint={false}
          />
        </div>

        {/* 保留少量幾何元素作為點綴 */}
        <div className="absolute inset-0 opacity-5 pointer-events-none">
          {Array.from({ length: 8 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute"
              style={{
                left: `${15 + Math.random() * 70}%`,
                top: `${15 + Math.random() * 70}%`,
              }}
            >
              {i % 2 === 0 ? (
                <motion.div
                  className="w-0.5 h-0.5 bg-blue-300/40 rounded-full"
                  animate={{
                    opacity: [0, 1, 0],
                    scale: [0, 1, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    delay: i * 0.8,
                  }}
                />
              ) : (
                <motion.div
                  className="w-3 h-px bg-gradient-to-r from-transparent via-purple-300/20 to-transparent"
                  animate={{
                    opacity: [0, 0.6, 0],
                    scaleX: [0, 1, 0],
                  }}
                  transition={{
                    duration: 5,
                    repeat: Infinity,
                    delay: i * 1.2,
                  }}
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Ambient light gradients */}
        <motion.div
          className="absolute top-1/4 right-1/4 w-96 h-96 pointer-events-none"
          animate={{
            rotate: [0, 360],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        >
          <div className="w-full h-full bg-gradient-to-br from-blue-900/5 to-purple-900/5 rounded-[40%] blur-3xl" />
        </motion.div>

        <motion.div
          className="absolute bottom-1/4 left-1/4 w-80 h-80 pointer-events-none"
          animate={{
            rotate: [360, 0],
            scale: [1.2, 0.8, 1.2],
          }}
          transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        >
          <div className="w-full h-full bg-gradient-to-tl from-purple-800/5 to-emerald-800/5 rounded-[60%] blur-3xl" />
        </motion.div>

        {/* Dark Luxury Content */}
        <div className="relative z-10 flex flex-col justify-center px-16 text-white" style={{ pointerEvents: 'none' }}>
          {/* Allow specific interactive elements */}
          <div style={{ pointerEvents: 'auto' }}>
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 1 }}
            className="mb-10"
          >
            {/* Dark Luxury Logo */}
            <motion.div
              className="flex items-center space-x-4 mb-10"
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="relative">
                <motion.div
                  className="w-20 h-20 bg-gradient-to-br from-blue-600 via-purple-500 to-emerald-600 rounded-3xl flex items-center justify-center shadow-2xl border border-blue-400/30"
                  animate={{
                    boxShadow: [
                      "0 0 30px rgba(59, 130, 246, 0.2)",
                      "0 0 50px rgba(139, 92, 246, 0.3)",
                      "0 0 30px rgba(16, 185, 129, 0.2)",
                    ]
                  }}
                  transition={{ duration: 4, repeat: Infinity }}
                >
                  <Gem className="w-10 h-10 text-white drop-shadow-xl" />
                </motion.div>
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-500 to-emerald-600 rounded-3xl opacity-40 blur-xl"
                  animate={{
                    scale: [1, 1.15, 1],
                    opacity: [0.3, 0.5, 0.3],
                  }}
                  transition={{ duration: 5, repeat: Infinity }}
                />
                {/* Additional glow layers */}
                <motion.div
                  className="absolute inset-0 bg-blue-500 rounded-3xl opacity-20 blur-2xl"
                  animate={{
                    scale: [0.9, 1.3, 0.9],
                    opacity: [0.1, 0.25, 0.1],
                  }}
                  transition={{ duration: 6, repeat: Infinity, delay: 1 }}
                />
              </div>
              <div>
                <motion.h1
                  className="text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-200 via-purple-100 to-emerald-200 bg-clip-text text-transparent"
                  animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                  }}
                  transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                  style={{ backgroundSize: '200% 100%' }}
                >
                  Finora
                </motion.h1>
                <motion.p
                  className="text-blue-300/80 text-sm font-light tracking-[0.3em] uppercase mt-1"
                  animate={{
                    opacity: [0.6, 1, 0.6],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  Luxury Finance
                </motion.p>
              </div>
            </motion.div>

            {/* Dark Luxury Headline */}
            <motion.h2
              className="text-4xl font-light mb-8 leading-tight"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 1 }}
            >
              Where <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 via-purple-200 to-emerald-300 font-medium">Elegance</span>
              <br />
              <span className="text-gray-300">Meets</span> <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-200 via-blue-100 to-emerald-200 font-medium">Excellence</span>
            </motion.h2>

            <motion.p
              className="text-xl text-gray-300 leading-relaxed font-light max-w-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 1 }}
            >
              Experience the pinnacle of financial sophistication with our
              <span className="text-blue-200 font-medium"> premium platform</span> designed for the discerning professional.
            </motion.p>
          </motion.div>

          {/* Dark Luxury Features */}
          <motion.div
            className="space-y-8"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 1 }}
          >
            {[
              {
                icon: "✨",
                title: "Elite Analytics",
                desc: "AI-powered insights with institutional-grade precision",
                accent: "amber"
              },
              {
                icon: "💎",
                title: "Bespoke Experience",
                desc: "Handcrafted interface tailored to your preferences",
                accent: "yellow"
              },
              {
                icon: "🛡️",
                title: "Private Security",
                desc: "Bank-level encryption with biometric protection",
                accent: "amber"
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                className="flex items-start space-x-6 group cursor-default"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.4 + index * 0.2 }}
                whileHover={{ x: 8 }}
              >
                <motion.div
                  className="relative flex-shrink-0"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-900/40 to-purple-800/40 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-blue-400/20 shadow-lg">
                    <span className="text-2xl">{feature.icon}</span>
                  </div>
                  {/* Subtle glow effect */}
                  <motion.div
                    className="absolute inset-0 bg-blue-500/20 rounded-2xl blur-lg opacity-0 group-hover:opacity-100"
                    transition={{ duration: 0.3 }}
                  />
                </motion.div>
                <div className="flex-1">
                  <motion.h3
                    className="text-lg font-medium text-blue-100 mb-2 group-hover:text-blue-50 transition-colors"
                  >
                    {feature.title}
                  </motion.h3>
                  <p className="text-sm text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">
                    {feature.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Subtle signature */}
          <motion.div
            className="mt-16 pt-8 border-t border-blue-900/20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2, duration: 1 }}
          >
            <p className="text-xs text-blue-600/60 font-light tracking-wider uppercase text-center">
              Crafted for the Elite
            </p>
          </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Right Side - Original Clean Form Area */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="flex-1 flex items-center justify-center p-8 bg-gray-900"
      >
        <div className="w-full max-w-md">
          {children}
        </div>
      </motion.div>
    </div>
  )
}

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

  // Handle Google OAuth success
  const handleGoogleSuccess = useCallback(async (credential: string) => {
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
  }, [loginWithGoogle, navigate])

  // Handle Google OAuth error
  const handleGoogleError = useCallback((error: string) => {
    console.error('❌ Google OAuth error:', error)
    setErrorMessage(error || 'Google authentication failed')
  }, [])

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
  }, [handleGoogleSuccess, handleGoogleError])

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
    <div>
      <LuxuryAuthLayout>
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
      </LuxuryAuthLayout>
    </div>
  )
}
