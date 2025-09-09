/**
 * Analytics Service
 * Handles all analytics-related API calls
 */

import { apiClient } from '../client'
import { API_ENDPOINTS } from '../config'
import type {
  ApiResponse,
  AnalyticsQuery,
  AnalyticsOverview,
  FinancialSummary,
  CategoryBreakdown,
  SpendingTrend,
  TagAnalytics
} from '../../types'
import { AnalyticsPeriod } from '../../types'

export class AnalyticsService {
  /**
   * Helper method to convert analytics query to URL parameters
   */
  private buildQueryParams(query: AnalyticsQuery): URLSearchParams {
    const params = new URLSearchParams()

    if (query.start_date) params.append('start_date', query.start_date)
    if (query.end_date) params.append('end_date', query.end_date)
    if (query.period) params.append('period', query.period)
    if (query.transaction_type) params.append('transaction_type', query.transaction_type)
    if (query.category_id) params.append('category_id', query.category_id)

    return params
  }

  /**
   * Get comprehensive analytics overview
   * Includes summary, trends, and breakdowns
   */
  async getAnalyticsOverview(query: AnalyticsQuery = {}): Promise<AnalyticsOverview> {
    const params = this.buildQueryParams(query)
    const url = params.toString() ?
      `${API_ENDPOINTS.analytics.overview}?${params.toString()}` :
      API_ENDPOINTS.analytics.overview

    const response = await apiClient.get<ApiResponse<AnalyticsOverview>>(url)
    return response.data
  }

  /**
   * Get detailed breakdown of spending by categories and subcategories
   */
  async getCategoryBreakdown(query: AnalyticsQuery = {}): Promise<CategoryBreakdown[]> {
    const params = this.buildQueryParams(query)
    const url = params.toString() ?
      `${API_ENDPOINTS.analytics.categoryBreakdown}?${params.toString()}` :
      API_ENDPOINTS.analytics.categoryBreakdown

    const response = await apiClient.get<ApiResponse<CategoryBreakdown[]>>(url)
    return response.data
  }

  /**
   * Get spending trends over time with specified granularity
   */
  async getSpendingTrends(query: AnalyticsQuery = {}): Promise<SpendingTrend[]> {
    const params = this.buildQueryParams(query)
    const url = params.toString() ?
      `${API_ENDPOINTS.analytics.spendingTrends}?${params.toString()}` :
      API_ENDPOINTS.analytics.spendingTrends

    const response = await apiClient.get<ApiResponse<SpendingTrend[]>>(url)
    return response.data
  }

  /**
   * Get high-level financial summary including income, expense, and key metrics
   */
  async getFinancialSummary(query: AnalyticsQuery = {}): Promise<FinancialSummary> {
    const params = this.buildQueryParams(query)
    const url = params.toString() ?
      `${API_ENDPOINTS.analytics.financialSummary}?${params.toString()}` :
      API_ENDPOINTS.analytics.financialSummary

    const response = await apiClient.get<ApiResponse<FinancialSummary>>(url)
    return response.data
  }

  /**
   * Get analytics based on transaction tags showing spending patterns
   */
  async getTagAnalytics(query: AnalyticsQuery = {}): Promise<TagAnalytics[]> {
    const params = this.buildQueryParams(query)
    const url = params.toString() ?
      `${API_ENDPOINTS.analytics.tagAnalytics}?${params.toString()}` :
      API_ENDPOINTS.analytics.tagAnalytics

    const response = await apiClient.get<ApiResponse<TagAnalytics[]>>(url)
    return response.data
  }

  /**
   * Convenience method to get current month financial summary
   */
  async getCurrentMonthSummary(): Promise<FinancialSummary> {
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)

    return this.getFinancialSummary({
      start_date: startOfMonth.toISOString().split('T')[0],
      end_date: endOfMonth.toISOString().split('T')[0]
    })
  }

  /**
   * Convenience method to get last 30 days spending trends
   */
  async getLast30DaysTrends(): Promise<SpendingTrend[]> {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)

    return this.getSpendingTrends({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      period: AnalyticsPeriod.WEEKLY
    })
  }

  /**
   * Convenience method to get last 7 days spending trends (daily)
   */
  async getLast7DaysTrends(): Promise<SpendingTrend[]> {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 7)

    return this.getSpendingTrends({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      period: AnalyticsPeriod.WEEKLY
    })
  }

  /**
   * Convenience method to get current month category breakdown
   */
  async getCurrentMonthCategoryBreakdown(): Promise<CategoryBreakdown[]> {
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)

    return this.getCategoryBreakdown({
      start_date: startOfMonth.toISOString().split('T')[0],
      end_date: endOfMonth.toISOString().split('T')[0]
    })
  }
}

// Export singleton instance
export const analyticsService = new AnalyticsService()
export default analyticsService
