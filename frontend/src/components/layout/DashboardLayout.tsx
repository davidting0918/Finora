import { Sidebar } from './Sidebar'
import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen relative overflow-hidden bg-black">
      {/* Sophisticated dark background */}
      <div className="absolute inset-0">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-gray-900 to-black" />

        {/* Noise texture overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
            backgroundSize: '256px 256px'
          }}
        />
      </div>

      {/* Advanced animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Morphing geometric shapes */}
        <motion.div
          className="absolute top-1/4 right-1/4 w-96 h-96"
          animate={{
            rotate: [0, 360],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        >
          <div className="w-full h-full bg-gradient-to-br from-slate-800/5 to-slate-700/5 rounded-[40%] blur-3xl" />
        </motion.div>

        <motion.div
          className="absolute bottom-1/4 left-1/4 w-80 h-80"
          animate={{
            rotate: [360, 0],
            scale: [1.2, 0.8, 1.2],
          }}
          transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        >
          <div className="w-full h-full bg-gradient-to-tl from-slate-700/5 to-slate-600/5 rounded-[60%] blur-3xl" />
        </motion.div>

        {/* Subtle moving lines */}
        <motion.div
          className="absolute inset-0"
          animate={{ backgroundPosition: ["0% 0%", "100% 100%"] }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          style={{
            backgroundImage: `linear-gradient(45deg, transparent 48%, rgba(148, 163, 184, 0.03) 49%, rgba(148, 163, 184, 0.03) 51%, transparent 52%)`,
            backgroundSize: '100px 100px'
          }}
        />
      </div>

      {/* Modern grid pattern */}
      <div className="absolute inset-0 opacity-[0.01]">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="modernGrid" width="60" height="60" patternUnits="userSpaceOnUse">
              <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgb(148, 163, 184)" strokeWidth="0.5"/>
              <circle cx="0" cy="0" r="1" fill="rgb(148, 163, 184)" opacity="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#modernGrid)" />
        </svg>
      </div>

      {/* Content with advanced styling */}
      <div className="relative z-10 flex w-full">
        <Sidebar />

        <main className="flex-1 overflow-auto">
          <div className="min-h-full">
            {/* Modern content wrapper */}
            <div className="relative p-6 lg:p-8">
              {/* Sophisticated backdrop */}
              <div className="absolute inset-4 bg-gradient-to-br from-slate-900/10 via-gray-900/5 to-transparent backdrop-blur-[2px] rounded-[2rem] border border-slate-800/20" />

              {/* Content area */}
              <div className="relative z-10">
                {children}
              </div>

              {/* Subtle corner accents */}
              <div className="absolute top-8 right-8 w-8 h-8">
                <div className="absolute inset-0 bg-gradient-to-br from-slate-600/20 to-transparent rounded-tr-3xl" />
              </div>
              <div className="absolute bottom-8 left-8 w-8 h-8">
                <div className="absolute inset-0 bg-gradient-to-tl from-slate-600/20 to-transparent rounded-bl-3xl" />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
