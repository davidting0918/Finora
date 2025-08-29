from backend.core.model.transaction import Transaction, transaction_collection, TransactionType
from backend.core.model.analytics import (
    AnalyticsQuery, CategoryAnalytics, PeriodAnalytics, 
    SpendingTrend, TagAnalytics, FinancialSummary, AnalyticsOverview, AnalyticsPeriod
)
from backend.core.database import MongoAsyncClient
from backend.core.model.user import User
from datetime import datetime as dt, timezone as tz, timedelta as td
from typing import List, Dict, Any
from collections import defaultdict
from fastapi import HTTPException
import calendar

class AnalyticsService:
    def __init__(self):
        self.db = MongoAsyncClient()

    async def get_analytics_overview(self, query: AnalyticsQuery, current_user: User) -> AnalyticsOverview:
        """
        Get comprehensive analytics overview for user transactions
        """
        try:
            # Get filtered transactions
            transactions = await self._get_filtered_transactions(query, current_user)
            
            if not transactions:
                return self._empty_analytics_overview()

            # Calculate different analytics components
            summary = await self._calculate_financial_summary(transactions)
            category_breakdown = await self._calculate_category_breakdown(transactions)
            spending_trends = await self._calculate_spending_trends(transactions, query)
            top_tags = await self._calculate_tag_analytics(transactions)
            period_comparison = await self._calculate_period_comparison(transactions, query)

            return AnalyticsOverview(
                summary=summary,
                category_breakdown=category_breakdown,
                spending_trends=spending_trends,
                top_tags=top_tags,
                period_comparison=period_comparison
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analytics calculation error: {str(e)}")

    async def get_category_breakdown(self, query: AnalyticsQuery, current_user: User) -> List[CategoryAnalytics]:
        """
        Get detailed category-wise spending breakdown
        """
        transactions = await self._get_filtered_transactions(query, current_user)
        return await self._calculate_category_breakdown(transactions)

    async def get_spending_trends(self, query: AnalyticsQuery, current_user: User) -> List[SpendingTrend]:
        """
        Get spending trends over time based on specified period
        """
        transactions = await self._get_filtered_transactions(query, current_user)
        return await self._calculate_spending_trends(transactions, query)

    async def get_financial_summary(self, query: AnalyticsQuery, current_user: User) -> FinancialSummary:
        """
        Get high-level financial summary
        """
        transactions = await self._get_filtered_transactions(query, current_user)
        return await self._calculate_financial_summary(transactions)

    async def get_tag_analytics(self, query: AnalyticsQuery, current_user: User) -> List[TagAnalytics]:
        """
        Get analytics based on transaction tags
        """
        transactions = await self._get_filtered_transactions(query, current_user)
        return await self._calculate_tag_analytics(transactions)

    async def _get_filtered_transactions(self, query: AnalyticsQuery, current_user: User) -> List[Transaction]:
        """
        Get transactions based on analytics query filters
        """
        filter_conditions = {
            "user_id": current_user.id,
            "is_deleted": False
        }

        # Add date range filter
        if query.start_date or query.end_date:
            date_filter = {}
            if query.start_date:
                date_filter["$gte"] = int(query.start_date.timestamp())
            if query.end_date:
                end_date = query.end_date.replace(hour=23, minute=59, second=59)
                date_filter["$lte"] = int(end_date.timestamp())
            filter_conditions["created_at"] = date_filter

        # Add transaction type filter
        if query.transaction_type:
            filter_conditions["type"] = query.transaction_type.value

        # Add category filter
        if query.category_id:
            filter_conditions["category_id"] = query.category_id.value

        # Get all matching transactions
        documents = await self.db.find_many(transaction_collection, filter_conditions)
        
        transactions = []
        for doc in documents:
            try:
                transaction = Transaction(**doc)
                transactions.append(transaction)
            except Exception as e:
                print(f"Error parsing transaction {doc.get('id', 'unknown')}: {e}")
                continue

        return transactions

    async def _calculate_financial_summary(self, transactions: List[Transaction]) -> FinancialSummary:
        """
        Calculate high-level financial metrics
        """
        if not transactions:
            return FinancialSummary(
                total_income=0.0,
                total_expense=0.0,
                net_income=0.0,
                avg_daily_expense=0.0,
                largest_expense={},
                most_frequent_category={}
            )

        total_income = sum(t.amount for t in transactions if t.type == TransactionType.income)
        total_expense = sum(t.amount for t in transactions if t.type == TransactionType.expense)
        net_income = total_income - total_expense

        # Calculate average daily expense
        expense_transactions = [t for t in transactions if t.type == TransactionType.expense]
        if expense_transactions:
            dates = set(t.transaction_date.date() for t in expense_transactions)
            avg_daily_expense = total_expense / len(dates) if dates else 0.0
        else:
            avg_daily_expense = 0.0

        # Find largest expense
        largest_expense = {}
        if expense_transactions:
            largest = max(expense_transactions, key=lambda x: x.amount)
            largest_expense = {
                "id": largest.id,
                "amount": largest.amount,
                "description": largest.description,
                "category_id": largest.category_id.value,
                "transaction_date": largest.transaction_date.isoformat()
            }

        # Find most frequent category
        category_counts = defaultdict(int)
        for t in transactions:
            category_counts[t.category_id.value] += 1
        
        most_frequent_category = {}
        if category_counts:
            most_freq_cat = max(category_counts.items(), key=lambda x: x[1])
            most_frequent_category = {
                "category_id": most_freq_cat[0],
                "count": most_freq_cat[1]
            }

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_income=net_income,
            avg_daily_expense=round(avg_daily_expense, 2),
            largest_expense=largest_expense,
            most_frequent_category=most_frequent_category
        )

    async def _calculate_category_breakdown(self, transactions: List[Transaction]) -> List[CategoryAnalytics]:
        """
        Calculate spending breakdown by category
        """
        # Group transactions by category
        category_data = defaultdict(lambda: {
            'transactions': [],
            'subcategories': defaultdict(list)
        })
        
        total_amount = sum(t.amount for t in transactions)
        
        for t in transactions:
            category_data[t.category_id.value]['transactions'].append(t)
            category_data[t.category_id.value]['subcategories'][t.subcategory_id.value].append(t)

        result = []
        for category_id, data in category_data.items():
            category_total = sum(t.amount for t in data['transactions'])
            percentage = (category_total / total_amount * 100) if total_amount > 0 else 0

            # Calculate subcategory breakdown
            subcategories = []
            for subcat_id, subcat_transactions in data['subcategories'].items():
                subcat_total = sum(t.amount for t in subcat_transactions)
                subcat_percentage = (subcat_total / category_total * 100) if category_total > 0 else 0
                
                subcategories.append({
                    "subcategory_id": subcat_id,
                    "total_amount": subcat_total,
                    "transaction_count": len(subcat_transactions),
                    "percentage": round(subcat_percentage, 2)
                })

            # Sort subcategories by amount
            subcategories.sort(key=lambda x: x['total_amount'], reverse=True)

            result.append(CategoryAnalytics(
                category_id=category_id,
                category_name=category_id.replace('_', ' ').title(),
                total_amount=category_total,
                transaction_count=len(data['transactions']),
                percentage=round(percentage, 2),
                subcategories=subcategories
            ))

        # Sort by total amount descending
        result.sort(key=lambda x: x.total_amount, reverse=True)
        return result

    async def _calculate_spending_trends(self, transactions: List[Transaction], query: AnalyticsQuery) -> List[SpendingTrend]:
        """
        Calculate spending trends based on the specified period
        """
        if not transactions:
            return []

        # Group transactions by period
        period_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        
        for t in transactions:
            period_key = self._get_period_key(t.transaction_date, query.period)
            period_data[period_key]['amount'] += t.amount
            period_data[period_key]['count'] += 1

        result = []
        for period, data in sorted(period_data.items()):
            result.append(SpendingTrend(
                date=period,
                amount=data['amount'],
                transaction_count=data['count']
            ))

        return result

    async def _calculate_tag_analytics(self, transactions: List[Transaction]) -> List[TagAnalytics]:
        """
        Calculate analytics based on transaction tags
        """
        tag_data = defaultdict(lambda: {'total': 0.0, 'count': 0, 'amounts': []})
        
        for t in transactions:
            if t.tags:
                for tag in t.tags:
                    tag_data[tag]['total'] += t.amount
                    tag_data[tag]['count'] += 1
                    tag_data[tag]['amounts'].append(t.amount)

        result = []
        for tag, data in tag_data.items():
            avg_amount = data['total'] / data['count'] if data['count'] > 0 else 0
            result.append(TagAnalytics(
                tag=tag,
                total_amount=data['total'],
                transaction_count=data['count'],
                avg_amount=round(avg_amount, 2)
            ))

        # Sort by total amount descending, limit to top 20
        result.sort(key=lambda x: x.total_amount, reverse=True)
        return result[:20]

    async def _calculate_period_comparison(self, transactions: List[Transaction], query: AnalyticsQuery) -> List[PeriodAnalytics]:
        """
        Calculate period-wise income/expense comparison
        """
        period_data = defaultdict(lambda: {'income': 0.0, 'expense': 0.0, 'count': 0})
        
        for t in transactions:
            period_key = self._get_period_key(t.transaction_date, query.period)
            if t.type == TransactionType.income:
                period_data[period_key]['income'] += t.amount
            else:
                period_data[period_key]['expense'] += t.amount
            period_data[period_key]['count'] += 1

        result = []
        for period, data in sorted(period_data.items()):
            net = data['income'] - data['expense']
            result.append(PeriodAnalytics(
                period=period,
                income=data['income'],
                expense=data['expense'],
                net=net,
                transaction_count=data['count']
            ))

        return result

    def _get_period_key(self, date: dt, period: AnalyticsPeriod) -> str:
        """
        Generate period key based on date and period type
        """
        if period == AnalyticsPeriod.daily:
            return date.strftime('%Y-%m-%d')
        elif period == AnalyticsPeriod.weekly:
            year, week, _ = date.isocalendar()
            return f"{year}-W{week:02d}"
        elif period == AnalyticsPeriod.monthly:
            return date.strftime('%Y-%m')
        elif period == AnalyticsPeriod.yearly:
            return date.strftime('%Y')
        else:
            return date.strftime('%Y-%m-%d')

    def _empty_analytics_overview(self) -> AnalyticsOverview:
        """
        Return empty analytics overview when no transactions found
        """
        return AnalyticsOverview(
            summary=FinancialSummary(
                total_income=0.0,
                total_expense=0.0,
                net_income=0.0,
                avg_daily_expense=0.0,
                largest_expense={},
                most_frequent_category={}
            ),
            category_breakdown=[],
            spending_trends=[],
            top_tags=[],
            period_comparison=[]
        )
