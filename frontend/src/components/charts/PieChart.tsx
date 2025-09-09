import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { TrendingDown, Target, Loader } from 'lucide-react'
import { ChartColors } from '../../lib/colors'
import type { CategoryBreakdown } from '../../lib/types'

interface CategoryPieChartProps {
  data: CategoryBreakdown[]
  loading?: boolean
}

// Color palette for categories
const getColorForCategory = (index: number): string => {
  const colors = [
    '#3b82f6', // blue
    '#ef4444', // red
    '#10b981', // green
    '#f59e0b', // amber
    '#8b5cf6', // purple
    '#f97316', // orange
    '#06b6d4', // cyan
    '#84cc16', // lime
    '#ec4899', // pink
    '#6b7280', // gray
  ]
  return colors[index % colors.length]
}

// Transform category breakdown data for the chart
const transformCategoryData = (categories: CategoryBreakdown[]) => {
  // Handle empty or invalid categories array
  if (!categories || !Array.isArray(categories)) {
    return []
  }

  return categories.map((category, index) => {
    // Handle invalid category objects
    if (!category || typeof category !== 'object') {
      return {
        name: `Category ${index + 1}`,
        value: 0,
        color: getColorForCategory(index),
        percentage: 0,
        transaction_count: 0
      }
    }

    return {
      name: category.category_name || `Category ${index + 1}`,
      value: Number(category.total_amount) || 0,
      color: getColorForCategory(index),
      percentage: Number(category.percentage) || 0,
      transaction_count: Number(category.transaction_count) || 0
    }
  })
}

// Fallback category data for reference
const fallbackCategoryData = [
  {
    name: 'Food & Dining',
    value: 450,
    color: ChartColors.categories['Food & Dining'].color,
    gradient: ChartColors.categories['Food & Dining'].gradient,
    percentage: 28.1
  },
  {
    name: 'Transportation',
    value: 320,
    color: ChartColors.categories['Transportation'].color,
    gradient: ChartColors.categories['Transportation'].gradient,
    percentage: 20.0
  },
  {
    name: 'Shopping',
    value: 280,
    color: ChartColors.categories['Shopping'].color,
    gradient: ChartColors.categories['Shopping'].gradient,
    percentage: 17.5
  },
  {
    name: 'Entertainment',
    value: 180,
    color: ChartColors.categories['Entertainment'].color,
    gradient: ChartColors.categories['Entertainment'].gradient,
    percentage: 11.3
  },
  {
    name: 'Utilities',
    value: 240,
    color: ChartColors.categories['Utilities'].color,
    gradient: ChartColors.categories['Utilities'].gradient,
    percentage: 15.0
  },
  {
    name: 'Healthcare',
    value: 120,
    color: ChartColors.categories['Healthcare'].color,
    gradient: ChartColors.categories['Healthcare'].gradient,
    percentage: 7.5
  }
]

// Modern professional tooltip component
function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const data = payload[0]
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-5 shadow-2xl"
      >
        <div className="flex items-center space-x-3 mb-3">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-slate-400" />
            <div
              className="w-4 h-4 rounded-full border border-slate-600/50 shadow-sm"
              style={{ backgroundColor: data.payload.color }}
            />
          </div>
          <p className="text-slate-300 text-sm font-medium uppercase tracking-wide">{data.payload.name}</p>
        </div>
        <div className="space-y-2">
          <p className="text-white text-xl font-bold tabular-nums">
            ${data.value}
          </p>
          <div className="flex items-center space-x-2">
            <p className="text-slate-400 text-sm">
              {data.payload.percentage}% of total
            </p>
            <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${data.payload.percentage}%`,
                  backgroundColor: data.payload.color
                }}
              />
            </div>
          </div>
        </div>
        <div className="mt-3 pt-2 border-t border-slate-700/50">
          <p className="text-slate-400 text-xs uppercase tracking-wider">Category Analysis</p>
        </div>
      </motion.div>
    )
  }
  return null
}


export function CategoryPieChart({ data = [], loading = false }: CategoryPieChartProps) {
  const chartData = transformCategoryData(data)
  const totalSpending = data.reduce((sum, category) => sum + category.total_amount, 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.6, ease: "easeOut" }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="relative group"
    >
      {/* Modern card container */}
      <div className="relative bg-gradient-to-br from-slate-900/60 to-gray-900/40 backdrop-blur-2xl rounded-3xl p-8 border border-slate-700/30 shadow-2xl overflow-hidden">
        {/* Sophisticated background effects */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800/10 via-transparent to-slate-700/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-slate-600/5 to-transparent rounded-tr-[100px]" />
        </div>

        {/* Header */}
        <div className="relative z-10 flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-white mb-1">Spending by Category</h2>
            <p className="text-gray-400 text-sm">Monthly expense breakdown</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-slate-400 text-xs uppercase tracking-wide">Total spending</p>
              <p className="text-white text-lg font-bold tabular-nums">${totalSpending}</p>
            </div>
            <div className="p-3 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 shadow-lg border border-slate-600/30">
              <Target className="w-5 h-5 text-slate-300" />
            </div>
          </div>
        </div>

        {/* Chart and Legend Container */}
        <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between">
          {/* Chart */}
          <div className="flex-1 max-w-sm" style={{ height: 280 }}>
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader className="w-8 h-8 animate-spin text-slate-400" />
                <span className="ml-2 text-slate-400">Loading chart...</span>
              </div>
            ) : chartData.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <span className="text-slate-400">No categories data available</span>
              </div>
            ) : (
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={110}
                    paddingAngle={2}
                    dataKey="value"
                    animationBegin={0}
                    animationDuration={800}
                  >
                    {chartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        stroke="#1f2937"
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Custom Legend */}
          {!loading && chartData.length > 0 && (
            <div className="flex-1 ml-6 space-y-3 max-w-xs">
              {chartData.map((entry, index) => (
              <motion.div
                key={entry.name}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-700/30 hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full shadow-sm"
                    style={{ backgroundColor: entry.color }}
                  />
                  <div>
                    <p className="text-white text-sm font-medium">{entry.name}</p>
                    <p className="text-gray-400 text-xs">{entry.percentage}%</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white text-sm font-semibold">${entry.value}</p>
                </div>
              </motion.div>
            ))}
            </div>
          )}
        </div>

        {/* Bottom insight */}
        {!loading && chartData.length > 0 && (
          <div className="relative z-10 mt-6 pt-4 border-t border-gray-700/50">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <TrendingDown className="w-4 h-4 text-emerald-500" />
                <span className="text-gray-400">Largest category: <span className="text-white font-medium">{chartData[0]?.name || 'N/A'}</span></span>
              </div>
              <div className="text-gray-400">
                Total: <span className="text-white font-medium">${totalSpending.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
