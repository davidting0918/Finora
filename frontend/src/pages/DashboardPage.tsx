import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DashboardLayout } from '../components/layout/DashboardLayout'
import { WeeklyBarChart } from '../components/charts/BarChart'
import { CategoryPieChart } from '../components/charts/PieChart'
import { QuickAddForm } from '../components/forms/QuickAddForm'
import { useApiStatus } from '../lib/hooks/useApiStatus'
import { analyticsService, transactionService } from '../lib/api/services'
import type {
  FinancialSummary,
  CategoryBreakdown,
  SpendingTrend,
  TransactionFormData,
  TransactionListResponse
} from '../lib/types'
import { TrendingUp, DollarSign, PiggyBank, ArrowUpRight, ArrowDownRight, Zap, Activity, RefreshCw, Plus } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string
  icon: React.ComponentType<any>
  gradient: string
  change?: string
  changeType?: 'increase' | 'decrease'
  delay?: number
}

function StatsCard({ title, value, icon: Icon, gradient, change, changeType, delay = 0 }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, filter: "blur(10px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{
        delay,
        duration: 0.8,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      className="relative group cursor-pointer"
    >
      {/* Modern card container */}
      <div className="relative bg-gradient-to-br from-gray-900/80 to-gray-800/40 backdrop-blur-2xl rounded-2xl p-4 border border-gray-700/30 shadow-2xl overflow-hidden transform transition-all duration-500 group-hover:scale-[1.02] group-hover:rotate-1 group-hover:shadow-3xl">

        {/* Animated background elements */}
        <div className="absolute inset-0">
          {/* Noise texture overlay */}
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.1),rgba(255,255,255,0))]" />

          {/* Morphing background gradient */}
          <motion.div
            className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-700`}
            animate={{
              background: [
                `linear-gradient(45deg, transparent, transparent)`,
                `linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1))`,
                `linear-gradient(225deg, rgba(139,92,246,0.1), rgba(59,130,246,0.1))`,
                `linear-gradient(315deg, rgba(59,130,246,0.1), transparent)`
              ]
            }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          />

          {/* Geometric pattern overlay */}
          <div className="absolute top-0 right-0 w-32 h-32 opacity-5">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <defs>
                <pattern id="hexagon" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                  <polygon points="10,2 18,7 18,13 10,18 2,13 2,7" fill="none" stroke="white" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#hexagon)" />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <p className="text-gray-300/80 text-sm font-medium uppercase tracking-wide">{title}</p>
                <div className="w-1 h-1 bg-gray-500 rounded-full opacity-50" />
              </div>

              <motion.p
                className="text-2xl font-bold text-white mt-2 tracking-tight"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: delay + 0.3, duration: 0.5, ease: "backOut" }}
              >
                {value}
              </motion.p>

              {change && (
                <motion.div
                  className="flex items-center mt-3 space-x-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: delay + 0.5 }}
                >
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${
                    changeType === 'increase'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-red-500/20 text-red-300'
                  }`}>
                    {changeType === 'increase' ? (
                      <ArrowUpRight className="w-3 h-3" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3" />
                    )}
                    <span className="text-xs font-semibold">{change}</span>
                  </div>
                  <span className="text-gray-400 text-xs">vs last period</span>
                </motion.div>
              )}
            </div>

            {/* Modern icon container */}
            <motion.div
              className="relative"
              whileHover={{ rotate: 15, scale: 1.1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className={`relative p-3 rounded-xl bg-gradient-to-br ${gradient} shadow-xl`}>
                {/* Inner glow effect */}
                <div className="absolute inset-0 rounded-xl bg-white/10 backdrop-blur-sm" />

                {/* Animated border */}
                <motion.div
                  className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/40 to-transparent opacity-0 group-hover:opacity-100"
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                  style={{
                    background: `conic-gradient(from 0deg, transparent, rgba(255,255,255,0.3), transparent)`,
                    mask: `radial-gradient(circle at center, transparent 60%, black 65%)`
                  }}
                />

                <Icon className="w-5 h-5 text-white relative z-10 drop-shadow-lg" />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Hover activation line */}
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-60"
          initial={{ width: 0 }}
          whileHover={{ width: "100%" }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </motion.div>
  )
}

export default function DashboardPage() {
  const [isQuickAddOpen, setIsQuickAddOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null)
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategoryBreakdown[]>([])
  const [spendingTrends, setSpendingTrends] = useState<SpendingTrend[]>([])
  const [recentTransactions, setRecentTransactions] = useState<TransactionListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiStatus = useApiStatus({
    checkInterval: 30000, // Check every 30 seconds
    baseUrl: 'http://localhost:8000'
  })

  // Load dashboard data
  const loadDashboardData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Load all dashboard data in parallel
      const [
        summaryData,
        categoryData,
        trendsData,
        transactionsData
      ] = await Promise.all([
        analyticsService.getCurrentMonthSummary(),
        analyticsService.getCurrentMonthCategoryBreakdown(),
        analyticsService.getLast7DaysTrends(),
        transactionService.getTransactionList({
          page: 1,
          limit: 5,
          sort_by: 'created_at',
          sort_order: 'desc'
        })
      ])

      // Set data with fallbacks to prevent undefined errors
      setFinancialSummary(summaryData || null)
      setCategoryBreakdown(Array.isArray(categoryData) ? categoryData : [])
      setSpendingTrends(Array.isArray(trendsData) ? trendsData : [])
      setRecentTransactions(transactionsData || null)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    loadDashboardData()
  }, [])

  // Handle data refresh
  const handleRefresh = async () => {
    setIsRefreshing(true)

    try {
      // Force API status check
      await apiStatus.forceCheck()

      // Reload all dashboard data
      await loadDashboardData()

      console.log('Data refreshed successfully!')
    } catch (error) {
      console.error('Failed to refresh data:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Handle quick add form submission
  const handleQuickAdd = async (data: any) => {
    console.log('Quick add transaction:', data)

    try {
      // Transaction creation is already handled in QuickAddForm
      // Just refresh the dashboard data to show the new transaction
      await loadDashboardData()
      console.log('Transaction added successfully!')
    } catch (error) {
      console.error('Failed to refresh dashboard after adding transaction:', error)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-4">
        {/* Modern header with sophisticated design */}
        <motion.div
          initial={{ opacity: 0, y: -30, filter: "blur(10px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1] }}
          className="relative"
        >
          {/* Background accent */}
          <div className="absolute -inset-4 bg-gradient-to-r from-slate-800/50 to-transparent rounded-3xl blur-xl" />

          <div className="relative z-10">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <motion.div
                    initial={{ rotate: -180, scale: 0 }}
                    animate={{ rotate: 0, scale: 1 }}
                    transition={{ delay: 0.5, duration: 0.8, ease: "backOut" }}
                    className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl flex items-center justify-center border border-slate-600/50 shadow-lg"
                  >
                    <Activity className="w-5 h-5 text-slate-300" />
                  </motion.div>

                  <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                      Dashboard
                    </h1>
                    <motion.div
                      className="h-0.5 bg-gradient-to-r from-slate-400 via-slate-600 to-transparent rounded-full mt-1"
                      initial={{ width: 0 }}
                      animate={{ width: "50%" }}
                      transition={{ delay: 0.8, duration: 1 }}
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {/* API Status Indicator */}
                <motion.div
                  className="flex items-center space-x-2 px-3 py-1.5 bg-slate-800/50 rounded-xl border border-slate-700/30 backdrop-blur-xl"
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6, duration: 0.6 }}
                >
                  <Zap className="w-3 h-3 text-amber-400" />
                  <span className="text-slate-300 text-xs font-medium">Live Analytics</span>
                  <motion.div
                    className={`w-1.5 h-1.5 rounded-full ${
                      apiStatus.isOnline ? 'bg-emerald-400' : 'bg-red-400'
                    }`}
                    animate={{
                      scale: apiStatus.isOnline ? [1, 1.5, 1] : [1, 1.2, 1],
                      opacity: apiStatus.isOnline ? [1, 0.5, 1] : [1, 0.3, 1]
                    }}
                    transition={{
                      duration: apiStatus.isOnline ? 2 : 1,
                      repeat: Infinity
                    }}
                  />
                </motion.div>

                {/* Refresh Button */}
                <motion.button
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  whileHover={!isRefreshing ? { scale: 1.05 } : {}}
                  whileTap={!isRefreshing ? { scale: 0.95 } : {}}
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7, duration: 0.6 }}
                  className={`p-2 rounded-xl bg-slate-800/50 border border-slate-700/30 backdrop-blur-xl transition-all duration-200 ${
                    isRefreshing
                      ? 'text-slate-500 cursor-not-allowed'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50 hover:border-slate-600/30'
                  }`}
                >
                  <motion.div
                    animate={isRefreshing ? { rotate: 360 } : { rotate: 0 }}
                    transition={isRefreshing ? { duration: 1, repeat: Infinity, ease: "linear" } : { duration: 0.3 }}
                  >
                    <RefreshCw className="w-4 h-4" />
                  </motion.div>
                </motion.button>

                {/* Quick Add Button */}
                <motion.button
                  onClick={() => setIsQuickAddOpen(true)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8, duration: 0.6 }}
                  className="flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-blue-600/20 to-emerald-600/20 hover:from-blue-600/30 hover:to-emerald-600/30 rounded-xl border border-blue-500/30 hover:border-emerald-500/30 backdrop-blur-xl transition-all duration-200 text-blue-300 hover:text-emerald-300 shadow-lg shadow-blue-500/10"
                >
                  <Plus className="w-4 h-4" />
                  <span className="text-xs font-medium">Quick Add</span>
                </motion.button>
              </div>
            </div>

            <motion.p
              className="text-slate-400 text-sm font-light leading-relaxed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
            >
              Advanced financial intelligence at your fingertips
            </motion.p>
          </div>
        </motion.div>

        {/* Professional stats grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, staggerChildren: 0.1 }}
        >
          <StatsCard
            title="Net Income"
            value={loading ? "Loading..." : financialSummary ? `$${financialSummary.net_income.toLocaleString()}` : "$0"}
            icon={DollarSign}
            gradient="from-slate-700 to-slate-900"
            change={financialSummary && financialSummary.net_income >= 0 ? "+100%" : "-100%"}
            changeType={financialSummary && financialSummary.net_income >= 0 ? "increase" : "decrease"}
            delay={0.4}
          />
          <StatsCard
            title="Total Income"
            value={loading ? "Loading..." : financialSummary ? `$${financialSummary.total_income.toLocaleString()}` : "$0"}
            icon={TrendingUp}
            gradient="from-slate-700 to-slate-900"
            change="+12.5%"
            changeType="increase"
            delay={0.5}
          />
          <StatsCard
            title="Total Expenses"
            value={loading ? "Loading..." : financialSummary ? `$${financialSummary.total_expense.toLocaleString()}` : "$0"}
            icon={PiggyBank}
            gradient="from-slate-700 to-slate-900"
            change={financialSummary ? `${financialSummary.transaction_count} transactions` : "0 transactions"}
            changeType="increase"
            delay={0.6}
          />
        </motion.div>

        {/* Advanced charts section */}
        <motion.div
          className="grid grid-cols-1 xl:grid-cols-2 gap-6"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 1 }}
        >
          <WeeklyBarChart data={spendingTrends} loading={loading} />
          <CategoryPieChart data={categoryBreakdown} loading={loading} />
        </motion.div>

        {/* Signature modern element */}
        <motion.div
          className="flex items-center justify-center pt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <div className="h-px w-full bg-gradient-to-r from-transparent via-slate-700/50 to-transparent" />
          <div className="px-6 py-2 bg-slate-900/50 rounded-full border border-slate-800/50 backdrop-blur-xl">
            <span className="text-slate-500 text-xs font-medium tracking-wide">FINORA ANALYTICS</span>
          </div>
          <div className="h-px w-full bg-gradient-to-r from-transparent via-slate-700/50 to-transparent" />
        </motion.div>

        {/* Quick Add Form Modal */}
        <QuickAddForm
          isOpen={isQuickAddOpen}
          onClose={() => setIsQuickAddOpen(false)}
          onSubmit={handleQuickAdd}
        />
      </div>
    </DashboardLayout>
  )
}
