import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Home,
  Receipt,
  PieChart,
  Settings,
  Menu,
  X,
  DollarSign,
  LogOut,
  User
} from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/contexts/AuthContext'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Expenses', href: '/expenses', icon: Receipt },
  { name: 'Budget', href: '/budget', icon: PieChart },
  { name: 'Settings', href: '/settings', icon: Settings }
]

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, isLoading } = useAuth()

  // Handle logout with navigation
  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login', { replace: true })
    } catch (error) {
      console.error('Logout failed:', error)
      // Still navigate to login even if logout fails
      navigate('/login', { replace: true })
    }
  }

  return (
    <motion.div
      initial={{ width: 250 }}
      animate={{ width: isCollapsed ? 70 : 250 }}
      transition={{ duration: 0.3 }}
      className="bg-gradient-to-b from-slate-900 to-gray-900 border-r border-slate-700/50 h-screen flex flex-col shadow-2xl"
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-700/30 flex items-center justify-between">
        {!isCollapsed && (
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 1 }}
            animate={{ opacity: isCollapsed ? 0 : 1 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-8 h-8 bg-gradient-to-br from-slate-600 to-slate-800 rounded-xl flex items-center justify-center shadow-lg border border-slate-600/50">
              <DollarSign className="w-5 h-5 text-slate-300" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">Finora</span>
          </motion.div>
        )}

        <motion.button
          onClick={() => setIsCollapsed(!isCollapsed)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 rounded-xl hover:bg-slate-800/50 text-slate-400 hover:text-white transition-all duration-200 border border-transparent hover:border-slate-600/30"
        >
          {isCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon

          return (
            <Link key={item.name} to={item.href}>
              <motion.div
                whileHover={{ x: 6, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex items-center p-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-slate-700 to-slate-600 text-white shadow-lg border border-slate-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50 border border-transparent hover:border-slate-700/30'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : ''}`} />
                {!isCollapsed && (
                  <span className="ml-3 font-medium tracking-wide">{item.name}</span>
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* User Info & Logout Section */}
      <div className="p-4 border-t border-slate-700/30 bg-slate-900/50 backdrop-blur-sm">
        {/* User Info */}
        {user && !isCollapsed && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 p-3 rounded-xl bg-slate-800/30 border border-slate-700/30"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-slate-600 to-slate-700 rounded-full flex items-center justify-center shadow-lg">
                <User className="w-4 h-4 text-slate-300" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user.name || 'User'}
                </p>
                <p className="text-xs text-slate-400 truncate">
                  {user.email}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Logout Button */}
        <motion.button
          onClick={handleLogout}
          disabled={isLoading}
          whileHover={!isLoading ? { scale: 1.02, x: 2 } : {}}
          whileTap={!isLoading ? { scale: 0.98 } : {}}
          className={`w-full flex items-center justify-center space-x-3 p-3 rounded-xl transition-all duration-200 ${
            isLoading
              ? 'bg-slate-800/30 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-slate-700/50 to-slate-600/50 hover:from-red-600/20 hover:to-red-700/20 text-slate-300 hover:text-red-300 border border-slate-600/30 hover:border-red-500/30 shadow-lg hover:shadow-red-500/10'
          }`}
        >
          <LogOut className="w-4 h-4" />
          {!isCollapsed && (
            <span className="font-medium tracking-wide">
              {isLoading ? 'Logging out...' : 'Sign Out'}
            </span>
          )}
        </motion.button>
      </div>
    </motion.div>
  )
}
