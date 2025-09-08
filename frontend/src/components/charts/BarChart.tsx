import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { BarChart3, Loader } from 'lucide-react'
import { ChartColors } from '../../lib/colors'
import type { SpendingTrend } from '../../lib/types'

// Modern professional categories with sophisticated colors
const categories = ChartColors.categories

interface WeeklyBarChartProps {
  data: SpendingTrend[]
  loading?: boolean
}

// Transform spending trends data for the chart
const transformSpendingTrendsData = (trends: SpendingTrend[]) => {
  // Handle empty or invalid trends array
  if (!trends || !Array.isArray(trends)) {
    return []
  }

  return trends.map((trend, index) => {
    // Handle invalid trend objects
    if (!trend || typeof trend !== 'object') {
      return {
        period: `Period ${index + 1}`,
        income: 0,
        expenses: 0,
        net: 0,
        transactions: 0
      }
    }

    return {
      period: formatPeriod(trend.period),
      income: Number(trend.total_income) || 0,
      expenses: Number(trend.total_expense) || 0,
      net: Number(trend.net_income) || 0,
      transactions: Number(trend.transaction_count) || 0
    }
  })
}

// Helper function to format period for display
const formatPeriod = (period: string | undefined | null): string => {
  // Handle null/undefined periods
  if (!period || typeof period !== 'string') {
    return 'N/A'
  }

  // If it's an ISO date, format it for daily view
  if (period.includes('-')) {
    const date = new Date(period)
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return period
    }

    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    // Format as "Today", "Yesterday", or "Mon 12/9"
    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    } else {
      // Return short weekday + month/day format for other days
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'numeric',
        day: 'numeric'
      })
    }
  }
  return period
}

// Modern professional tooltip component
function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    // Calculate total from payload
    const total = payload.reduce((sum: number, entry: any) => sum + (entry.value || 0), 0)

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-5 shadow-2xl min-w-[240px]"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-slate-400" />
            <p className="text-slate-300 text-sm font-medium uppercase tracking-wide">{label}</p>
          </div>
          <p className="text-white text-xl font-bold">${total}</p>
        </div>

        <div className="space-y-3">
          {payload
            .filter((entry: any) => entry.value > 0)
            .sort((a: any, b: any) => b.value - a.value)
            .map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div
                  className="w-3 h-3 rounded-full border border-slate-600/50 shadow-sm"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-slate-300 text-sm font-medium">{entry.dataKey}</span>
              </div>
              <span className="text-white text-sm font-bold tabular-nums">${entry.value}</span>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t border-slate-700/50">
          <p className="text-slate-400 text-xs uppercase tracking-wider">Professional Analytics</p>
        </div>
      </motion.div>
    )
  }
  return null
}


export function WeeklyBarChart({ data = [], loading = false }: WeeklyBarChartProps) {
  const chartData = transformSpendingTrendsData(data)
  const totalExpenses = data.reduce((sum, trend) => sum + trend.total_expense, 0)
  const avgExpenses = data.length > 0 ? Math.round(totalExpenses / data.length) : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="relative group"
    >
      {/* Modern card container */}
      <div className="relative bg-gradient-to-br from-slate-900/60 to-gray-900/40 backdrop-blur-2xl rounded-3xl p-8 border border-slate-700/30 shadow-2xl overflow-hidden">
        {/* Sophisticated background effects */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800/10 via-transparent to-slate-700/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-slate-600/5 to-transparent rounded-bl-[100px]" />
        </div>

        {/* Header */}
        <div className="relative z-10 flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-white mb-1">Last 7 Days Spending Trends</h2>
            <p className="text-gray-400 text-sm">Daily income vs expense comparison</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-slate-400 text-xs uppercase tracking-wide">Total Expenses</p>
              <p className="text-white text-lg font-bold tabular-nums">
                {loading ? 'Loading...' : `$${totalExpenses.toLocaleString()}`}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 shadow-lg border border-slate-600/30">
              <BarChart3 className="w-5 h-5 text-slate-300" />
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="relative z-10" style={{ width: '100%', height: 320 }}>
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader className="w-8 h-8 animate-spin text-slate-400" />
              <span className="ml-2 text-slate-400">Loading chart data...</span>
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <span className="text-slate-400">No data available</span>
            </div>
          ) : (
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
              {/* Enhanced grid */}
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#374151"
                opacity={0.3}
                horizontal={true}
                vertical={false}
              />

              {/* Enhanced X-axis */}
              <XAxis
                dataKey="period"
                stroke="#9ca3af"
                fontSize={12}
                fontWeight={500}
                axisLine={false}
                tickLine={false}
                dy={10}
              />

              {/* Enhanced Y-axis */}
              <YAxis
                stroke="#9ca3af"
                fontSize={12}
                fontWeight={500}
                axisLine={false}
                tickLine={false}
                dx={-10}
                tickFormatter={(value) => `$${value}`}
              />

              {/* Custom tooltip */}
              <Tooltip
                content={<CustomTooltip />}
                cursor={{ fill: 'rgba(59, 130, 246, 0.1)', radius: 4 }}
              />

              {/* Income and Expense bars */}
              <Bar
                dataKey="income"
                fill="#10b981"
                radius={[2, 2, 0, 0]}
                stroke="#10b981"
                strokeWidth={0}
                name="Income"
              />
              <Bar
                dataKey="expenses"
                fill="#ef4444"
                radius={[2, 2, 0, 0]}
                stroke="#ef4444"
                strokeWidth={0}
                name="Expenses"
              />
            </BarChart>
          </ResponsiveContainer>
          )}
        </div>

        {/* Modern legend */}
        {!loading && chartData.length > 0 && (
          <div className="relative z-10 mt-6 pt-4 border-t border-slate-700/30">
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex items-center space-x-3 p-2 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 transition-colors">
                <div className="w-3 h-3 rounded-full shadow-sm border border-slate-600/40 bg-green-500" />
                <span className="text-slate-300 text-sm font-medium">Income</span>
              </div>
              <div className="flex items-center space-x-3 p-2 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 transition-colors">
                <div className="w-3 h-3 rounded-full shadow-sm border border-slate-600/40 bg-red-500" />
                <span className="text-slate-300 text-sm font-medium">Expenses</span>
              </div>
            </div>

            {/* Professional bottom stats */}
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-slate-400 shadow-sm"></div>
                <span className="text-slate-400 font-medium">Avg Daily: <span className="text-white tabular-nums">${avgExpenses.toLocaleString()}</span></span>
              </div>
              <div className="text-slate-400">
                Days: <span className="text-slate-300 font-medium">{data.length}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
