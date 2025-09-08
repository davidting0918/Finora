/**
 * Modern Professional Color System
 * Centralized color management for charts and UI components
 */

// Modern Professional Color Palette
export const ModernColors = {
  // Primary professional colors (low saturation, enterprise-grade)
  slate: {
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a'
  },

  // Professional accent colors
  steel: {
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151'
  },

  // Modern blues (muted, sophisticated)
  azure: {
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1'
  },

  // Professional purples (low saturation)
  indigo: {
    500: '#6366f1',
    600: '#4f46e5',
    700: '#4338ca'
  },

  // Enterprise greens
  emerald: {
    500: '#10b981',
    600: '#059669',
    700: '#047857'
  },

  // Sophisticated grays
  neutral: {
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937'
  }
}

// Modern Chart Color Schemes
export const ChartColorSchemes = {
  // Professional 6-color palette for categories
  professional: [
    '#64748b', // Steel Gray
    '#0ea5e9', // Modern Blue
    '#6366f1', // Professional Indigo
    '#10b981', // Enterprise Green
    '#f59e0b', // Amber (controlled warmth)
    '#8b5cf6', // Sophisticated Purple
  ],

  // Monochromatic scheme (different shades of same hue)
  monochrome: [
    '#1e293b', // Dark slate
    '#334155', // Medium slate
    '#475569', // Light slate
    '#64748b', // Lighter slate
    '#94a3b8', // Very light slate
    '#cbd5e1', // Lightest slate
  ],

  // Enterprise gradient scheme
  enterprise: [
    '#0f172a', // Deep dark
    '#1e293b', // Dark steel
    '#334155', // Steel
    '#475569', // Light steel
    '#64748b', // Very light steel
    '#94a3b8', // Lightest steel
  ],

  // High contrast professional
  contrast: [
    '#0f172a', // Dark
    '#0ea5e9', // Blue accent
    '#6366f1', // Indigo accent
    '#10b981', // Green accent
    '#f59e0b', // Amber accent
    '#64748b', // Gray balance
  ]
}

// Chart-specific color configurations
export const ChartColors = {
  // Category colors for spending analysis
  categories: {
    'Food & Dining': {
      color: ChartColorSchemes.professional[0], // Steel Gray
      gradient: 'from-slate-600 to-slate-700',
      name: 'Food & Dining'
    },
    'Transportation': {
      color: ChartColorSchemes.professional[1], // Modern Blue
      gradient: 'from-sky-600 to-sky-700',
      name: 'Transportation'
    },
    'Shopping': {
      color: ChartColorSchemes.professional[2], // Professional Indigo
      gradient: 'from-indigo-600 to-indigo-700',
      name: 'Shopping'
    },
    'Entertainment': {
      color: ChartColorSchemes.professional[3], // Enterprise Green
      gradient: 'from-emerald-600 to-emerald-700',
      name: 'Entertainment'
    },
    'Utilities': {
      color: ChartColorSchemes.professional[4], // Controlled Amber
      gradient: 'from-amber-600 to-amber-700',
      name: 'Utilities'
    },
    'Healthcare': {
      color: ChartColorSchemes.professional[5], // Sophisticated Purple
      gradient: 'from-purple-600 to-purple-700',
      name: 'Healthcare'
    }
  },

  // Bar chart daily colors (professional gradient)
  daily: [
    { day: 'Mon', color: ChartColorSchemes.enterprise[0] },
    { day: 'Tue', color: ChartColorSchemes.enterprise[1] },
    { day: 'Wed', color: ChartColorSchemes.enterprise[2] },
    { day: 'Thu', color: ChartColorSchemes.enterprise[3] },
    { day: 'Fri', color: ChartColorSchemes.enterprise[4] },
    { day: 'Sat', color: ChartColorSchemes.enterprise[5] },
    { day: 'Sun', color: ChartColorSchemes.professional[1] } // Accent for weekend
  ]
}

// Utility functions for color management
export const ColorUtils = {
  // Get category color by name
  getCategoryColor: (categoryName: string) => {
    return ChartColors.categories[categoryName as keyof typeof ChartColors.categories]?.color || ModernColors.slate[600]
  },

  // Get all category colors as array
  getAllCategoryColors: () => {
    return Object.values(ChartColors.categories).map(cat => cat.color)
  },

  // Get professional color scheme
  getProfessionalScheme: () => {
    return ChartColorSchemes.professional
  },

  // Get enterprise color scheme
  getEnterpriseScheme: () => {
    return ChartColorSchemes.enterprise
  }
}

// Export default modern theme
export const ModernTheme = {
  colors: ModernColors,
  schemes: ChartColorSchemes,
  charts: ChartColors,
  utils: ColorUtils
}

export default ModernTheme
