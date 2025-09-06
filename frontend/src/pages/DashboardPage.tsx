import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'

export default function DashboardPage() {
  const navigate = useNavigate()

  const handleLogout = () => {
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">
            歡迎來到 Finora 儀表板 🎉
          </h1>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>登出</span>
          </button>
        </div>

        <div className="glass-card rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            登錄功能已成功遷移！
          </h2>
          <p className="text-gray-300 mb-4">
            您已經成功地將 Next.js 的登錄功能遷移到 Create React App 項目中。
          </p>
          <div className="space-y-2 text-gray-400">
            <p>✅ React Hook Form 表單驗證</p>
            <p>✅ Zod 架構驗證</p>
            <p>✅ Framer Motion 動畫效果</p>
            <p>✅ Tailwind CSS 樣式</p>
            <p>✅ React Router 路由導航</p>
            <p>✅ 響應式設計</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
