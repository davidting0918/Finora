/**
 * Transaction Service
 * Handles all transaction-related API calls
 */

import { apiClient } from '../client'
import { API_ENDPOINTS } from '../config'
import type {
  ApiResponse,
  Transaction,
  CreateTransactionRequest,
  UpdateTransactionRequest,
  TransactionListQuery,
  TransactionListResponse,
  Category,
  Subcategory
} from '../../types'

export class TransactionService {
  /**
   * Create a new transaction
   */
  async createTransaction(transactionData: CreateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.post<ApiResponse<Transaction>>(
      API_ENDPOINTS.transaction.create,
      transactionData
    )

    return response.data
  }

  /**
   * Get a single transaction by ID
   */
  async getTransaction(transactionId: string): Promise<Transaction> {
    const response = await apiClient.get<ApiResponse<Transaction>>(
      `${API_ENDPOINTS.transaction.info}/${transactionId}`
    )

    return response.data
  }

  /**
   * Get paginated list of transactions with filters
   */
  async getTransactionList(query: TransactionListQuery): Promise<TransactionListResponse> {
    const params = new URLSearchParams()

    // Add query parameters
    params.append('page', query.page.toString())
    params.append('limit', query.limit.toString())
    params.append('sort_by', query.sort_by)
    params.append('sort_order', query.sort_order)

    if (query.start_date) params.append('start_date', query.start_date)
    if (query.end_date) params.append('end_date', query.end_date)
    if (query.transaction_type) params.append('transaction_type', query.transaction_type)
    if (query.category_id) params.append('category_id', query.category_id)
    if (query.subcategory_id) params.append('subcategory_id', query.subcategory_id)

    const response = await apiClient.get<ApiResponse<TransactionListResponse>>(
      `${API_ENDPOINTS.transaction.list}?${params.toString()}`
    )

    return response.data
  }

  /**
   * Update an existing transaction
   */
  async updateTransaction(transactionId: string, updateData: UpdateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.post<ApiResponse<Transaction>>(
      `${API_ENDPOINTS.transaction.update}/${transactionId}`,
      updateData
    )

    return response.data
  }

  /**
   * Delete a transaction
   */
  async deleteTransaction(transactionId: string): Promise<void> {
    await apiClient.post<ApiResponse<null>>(
      `${API_ENDPOINTS.transaction.delete}/${transactionId}`
    )
  }

  /**
   * Get all available categories
   */
  async getCategories(): Promise<Record<string, Category>> {
    const response = await apiClient.get<ApiResponse<Record<string, Category>>>(
      API_ENDPOINTS.transaction.categories
    )

    return response.data
  }

  /**
   * Get subcategories for a specific category
   */
  async getSubcategories(categoryId: string): Promise<Record<string, Subcategory>> {
    const response = await apiClient.get<ApiResponse<Record<string, Subcategory>>>(
      `${API_ENDPOINTS.transaction.subcategories}/${categoryId}`
    )

    return response.data
  }

  /**
   * Helper method to get categories as an array with subcategories included
   */
  async getCategoriesWithSubcategories(): Promise<Category[]> {
    const categoriesMap = await this.getCategories()

    const categories: Category[] = []

    for (const [categoryId, category] of Object.entries(categoriesMap)) {
      try {
        const subcategoriesMap = await this.getSubcategories(categoryId)
        const subcategories = Object.entries(subcategoriesMap).map(([subId, sub]) => ({
          id: subId,
          name: sub.name,
          category_id: sub.category_id
        }))

        categories.push({
          ...category,
          subcategories
        })
      } catch (error) {
        // If subcategories fail to load, add category without subcategories
        console.warn(`Failed to load subcategories for category ${categoryId}:`, error)
        categories.push(category)
      }
    }

    return categories
  }
}

// Export singleton instance
export const transactionService = new TransactionService()
export default transactionService
