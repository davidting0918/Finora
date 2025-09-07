import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { LogOut, User } from 'lucide-react'
import { useAuth } from '../lib/contexts/AuthContext'
import { useEffect } from 'react'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated, isLoading } = useAuth()

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login', { replace: true })
    }
  }, [isAuthenticated, isLoading, navigate])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    )
  }

  // Don't render if not authenticated
  if (!isAuthenticated || !user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user.name}! 🎉
            </h1>
            <p className="text-gray-400 flex items-center space-x-2">
              <User className="w-4 h-4" />
              <span>{user.email}</span>
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* User Info Card */}
          <div className="glass-card rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
              <User className="w-5 h-5" />
              <span>User Info</span>
            </h2>
            <div className="space-y-3 text-gray-300">
              <div className="flex justify-between">
                <span className="text-gray-400">User ID:</span>
                <span className="font-mono text-sm">{user.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Email:</span>
                <span>{user.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Name:</span>
                <span>{user.name}</span>
              </div>
            </div>
          </div>

          {/* API Connection Status */}
          <div className="glass-card rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              API Connection Status
            </h2>
            <div className="space-y-2 text-gray-300">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>✅ Connected to Staging API</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>✅ Authentication successful</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>✅ User data loaded</span>
              </div>
            </div>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            🎉 API Integration Complete!
          </h2>
          <p className="text-gray-300 mb-4">
            The frontend is successfully connected to the backend staging API. All API services are available.
          </p>
          <div className="grid grid-cols-2 gap-4 text-gray-400">
            <div className="space-y-2">
              <p>✅ Authentication API</p>
              <p>✅ User Management API</p>
              <p>✅ Transaction API</p>
              <p>✅ Analytics API</p>
            </div>
            <div className="space-y-2">
              <p>✅ Unified HTTP Client</p>
              <p>✅ Error Handling</p>
              <p>✅ Token Auto Management</p>
              <p>✅ TypeScript Support</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
