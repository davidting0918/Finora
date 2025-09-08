import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  X,
  DollarSign,
  Calendar,
  FileText,
  ChevronDown,
  Plus,
  Minus,
  Check,
  Coffee,
  Car,
  ShoppingCart,
  Gamepad2,
  Home,
  Heart,
  Briefcase,
  Zap,
  TrendingUp,
  PiggyBank,
  Wallet,
  Loader
} from 'lucide-react'
import { transactionService } from '../../lib/api/services/transaction'
import type { Category, TransactionType, CreateTransactionRequest } from '../../lib/types'

// Form validation schema
const transactionSchema = z.object({
  type: z.string(),
  amount: z.string().min(1, 'Amount is required'),
  description: z.string().min(1, 'Description is required'),
  category: z.string().min(1, 'Category is required'),
  date: z.string().min(1, 'Date is required'),
  tags: z.string().optional()
})

type TransactionFormData = z.infer<typeof transactionSchema>

interface QuickAddFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: TransactionFormData) => Promise<void>
}

// Icon mapping for categories (fallback icons)
const categoryIconMap: Record<string, any> = {
  'Food & Dining': Coffee,
  'Transportation': Car,
  'Shopping': ShoppingCart,
  'Entertainment': Gamepad2,
  'Utilities': Home,
  'Healthcare': Heart,
  'Salary': Briefcase,
  'Freelance': Zap,
  'Investment': TrendingUp,
  'Business': PiggyBank,
  'Other Income': Wallet
}

// Default emoji mapping (fallback emojis)
const categoryEmojiMap: Record<string, string> = {
  'Food & Dining': '🍽️',
  'Transportation': '🚗',
  'Shopping': '🛍️',
  'Entertainment': '🎮',
  'Utilities': '🏠',
  'Healthcare': '❤️',
  'Salary': '💼',
  'Freelance': '⚡',
  'Investment': '📈',
  'Business': '🏢',
  'Other Income': '💰'
}

export function QuickAddForm({ isOpen, onClose, onSubmit }: QuickAddFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [transactionType, setTransactionType] = useState<'income' | 'expense'>('expense')
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [loadingCategories, setLoadingCategories] = useState(false)
  const [categoryError, setCategoryError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      type: 'expense',
      category: '',
      date: new Date().toISOString().split('T')[0]
    }
  })

  const selectedCategory = watch('category')

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      if (categories.length > 0) return // Already loaded

      setLoadingCategories(true)
      setCategoryError(null)

      try {
        const categoriesData = await transactionService.getCategoriesWithSubcategories()
        setCategories(categoriesData)
      } catch (error) {
        console.error('Failed to load categories:', error)
        setCategoryError('Failed to load categories')
      } finally {
        setLoadingCategories(false)
      }
    }

    if (isOpen) {
      fetchCategories()
    }
  }, [isOpen, categories.length])

  const handleFormSubmit = async (data: TransactionFormData) => {
    setIsSubmitting(true)
    try {
      // Convert form data to API format
      const transactionData: CreateTransactionRequest = {
        amount: parseFloat(data.amount),
        description: data.description,
        transaction_type: data.type as TransactionType,
        category_id: data.category,
        transaction_date: data.date,
        tags: data.tags ? data.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : undefined
      }

      // Call API to create transaction
      await transactionService.createTransaction(transactionData)

      // Call parent's onSubmit for any additional handling
      await onSubmit(data)

      reset()
      setCategoryDropdownOpen(false)
      onClose()
    } catch (error) {
      console.error('Failed to add transaction:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    reset()
    setCategoryDropdownOpen(false)
    onClose()
  }

  const handleTypeChange = (type: 'income' | 'expense') => {
    setTransactionType(type)
    setValue('type', type)
    setValue('category', '')
    setCategoryDropdownOpen(false)
  }

  const handleCategorySelect = (categoryId: string) => {
    setValue('category', categoryId)
    setCategoryDropdownOpen(false)
  }

  // Filter categories based on transaction type (if we have type-specific categories from API)
  // For now, we'll use all categories since the backend doesn't specify transaction type per category
  const currentCategories = categories.map(cat => ({
    id: cat.id,
    name: cat.name,
    icon: categoryIconMap[cat.name] || Wallet,
    emoji: cat.emoji || categoryEmojiMap[cat.name] || '💰'
  }))

  const selectedCategoryData = currentCategories.find(cat => cat.id === selectedCategory || cat.name === selectedCategory)

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={handleClose}
        >
          {/* Backdrop */}
          <motion.div
            initial={{ backdropFilter: "blur(0px)" }}
            animate={{ backdropFilter: "blur(12px)" }}
            exit={{ backdropFilter: "blur(0px)" }}
            className="absolute inset-0 bg-black/60"
          />

          {/* Form Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md"
          >
            {/* Dark modern container */}
            <div className="bg-slate-900 rounded-2xl shadow-2xl border border-slate-700 overflow-hidden">

              {/* Header */}
              <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white">Quick Add</h2>
                  <p className="text-sm text-slate-400">Add a new transaction</p>
                </div>
                <button
                  onClick={handleClose}
                  className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4">

                {/* Transaction Type Toggle */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Type</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => handleTypeChange('expense')}
                      className={`flex items-center justify-center px-4 py-3 rounded-lg border transition-all ${
                        transactionType === 'expense'
                          ? 'bg-red-500/10 border-red-500/30 text-red-400'
                          : 'bg-slate-800 border-slate-600 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      <Minus className="w-4 h-4 mr-2" />
                      Expense
                    </button>
                    <button
                      type="button"
                      onClick={() => handleTypeChange('income')}
                      className={`flex items-center justify-center px-4 py-3 rounded-lg border transition-all ${
                        transactionType === 'income'
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                          : 'bg-slate-800 border-slate-600 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Income
                    </button>
                  </div>
                </div>

                {/* Amount Field */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Amount</label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                    <input
                      {...register('amount')}
                      type="text"
                      placeholder="0.00"
                      className={`w-full pl-10 pr-4 py-3 bg-slate-800 border rounded-lg focus:outline-none focus:ring-2 transition-all text-white placeholder-slate-500 ${
                        errors.amount
                          ? 'border-red-500/30 focus:ring-red-500/20 focus:border-red-500'
                          : 'border-slate-600 focus:ring-blue-500/20 focus:border-blue-500'
                      }`}
                    />
                  </div>
                  {errors.amount && (
                    <p className="text-sm text-red-400">{errors.amount.message}</p>
                  )}
                </div>

                {/* Description Field */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Description</label>
                  <div className="relative">
                    <FileText className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                    <input
                      {...register('description')}
                      type="text"
                      placeholder="What was this for?"
                      className={`w-full pl-10 pr-4 py-3 bg-slate-800 border rounded-lg focus:outline-none focus:ring-2 transition-all text-white placeholder-slate-500 ${
                        errors.description
                          ? 'border-red-500/30 focus:ring-red-500/20 focus:border-red-500'
                          : 'border-slate-600 focus:ring-blue-500/20 focus:border-blue-500'
                      }`}
                    />
                  </div>
                  {errors.description && (
                    <p className="text-sm text-red-400">{errors.description.message}</p>
                  )}
                </div>

                {/* Category Dropdown */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Category</label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setCategoryDropdownOpen(!categoryDropdownOpen)}
                      className={`w-full flex items-center justify-between px-4 py-3 bg-slate-800 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                        errors.category
                          ? 'border-red-500/30 focus:ring-red-500/20'
                          : 'border-slate-600 focus:ring-blue-500/20'
                      } ${selectedCategory ? 'text-white' : 'text-slate-500'}`}
                    >
                      <div className="flex items-center">
                        {selectedCategoryData ? (
                          <>
                            <selectedCategoryData.icon className="w-4 h-4 mr-2 text-slate-400" />
                            <span className="mr-1">{selectedCategoryData.emoji}</span>
                            <span>{selectedCategoryData.name}</span>
                          </>
                        ) : (
                          <span>Select category...</span>
                        )}
                      </div>
                      <ChevronDown
                        className={`w-4 h-4 text-slate-400 transition-transform ${
                          categoryDropdownOpen ? 'rotate-180' : ''
                        }`}
                      />
                    </button>

                    {/* Dropdown Menu */}
                    <AnimatePresence>
                      {categoryDropdownOpen && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          transition={{ duration: 0.15 }}
                          className="absolute z-10 w-full mt-1 bg-slate-800 border border-slate-600 rounded-lg shadow-xl max-h-48 overflow-y-auto"
                        >
                          {loadingCategories ? (
                            <div className="flex items-center justify-center py-6">
                              <Loader className="w-5 h-5 animate-spin text-blue-400" />
                              <span className="ml-2 text-slate-400">Loading categories...</span>
                            </div>
                          ) : categoryError ? (
                            <div className="px-4 py-3 text-red-400 text-sm">
                              {categoryError}
                            </div>
                          ) : currentCategories.length === 0 ? (
                            <div className="px-4 py-3 text-slate-400 text-sm">
                              No categories available
                            </div>
                          ) : (
                            currentCategories.map((category, index) => {
                              const Icon = category.icon
                              return (
                                <motion.button
                                  key={category.id}
                                  type="button"
                                  onClick={() => handleCategorySelect(category.id)}
                                  initial={{ opacity: 0, x: -10 }}
                                  animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: index * 0.05 }}
                                  className={`w-full flex items-center px-4 py-3 hover:bg-slate-700 transition-colors ${
                                    selectedCategory === category.id ? 'bg-blue-600/20 text-blue-400' : 'text-slate-300'
                                  }`}
                                >
                                  <Icon className="w-4 h-4 mr-3 text-slate-400" />
                                  <span className="mr-2">{category.emoji}</span>
                                  <span>{category.name}</span>
                                  {selectedCategory === category.id && (
                                    <Check className="w-4 h-4 ml-auto text-blue-400" />
                                  )}
                                </motion.button>
                              )
                            })
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                  {errors.category && (
                    <p className="text-sm text-red-400">{errors.category.message}</p>
                  )}
                </div>

                {/* Date Field */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Date</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                    <input
                      {...register('date')}
                      type="date"
                      className={`w-full pl-10 pr-4 py-3 bg-slate-800 border rounded-lg focus:outline-none focus:ring-2 transition-all text-white ${
                        errors.date
                          ? 'border-red-500/30 focus:ring-red-500/20 focus:border-red-500'
                          : 'border-slate-600 focus:ring-blue-500/20 focus:border-blue-500'
                      }`}
                    />
                  </div>
                </div>

                {/* Submit Button */}
                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-all ${
                      transactionType === 'income'
                        ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/25'
                        : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/25'
                    } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-xl'}`}
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5 mr-2" />
                        Add Transaction
                      </>
                    )}
                  </button>
                </div>

              </form>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
