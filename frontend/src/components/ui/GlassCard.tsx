import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'
import { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  onClick?: () => void
  delay?: number
}

export function GlassCard({
  children,
  className,
  hover = true,
  onClick,
  delay = 0
}: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={hover ? {
        y: -4,
        transition: { duration: 0.2 }
      } : undefined}
      onClick={onClick}
      className={cn(
        'glass-card rounded-xl p-6',
        hover && 'cursor-pointer hover:glass-card-hover',
        onClick && 'cursor-pointer',
        className
      )}
    >
      {children}
    </motion.div>
  )
}
