# Finora Backend API Documentation

A comprehensive expense tracking and financial management API built with FastAPI.

**Base URL**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/scalar`

## 📋 Table of Contents

- [Authentication](#authentication)
- [API Response Format](#api-response-format)
- [Authentication Endpoints](#authentication-endpoints)
- [User Management Endpoints](#user-management-endpoints)
- [Transaction Endpoints](#transaction-endpoints)
- [Analytics Endpoints](#analytics-endpoints)
- [Categories & Subcategories](#categories--subcategories)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## 🔐 Authentication

### Authentication Methods

The API supports two authentication methods:

1. **Email/Password Authentication**
2. **Google OAuth2 Authentication**

### How to Authenticate

#### Method 1: Email/Password Login
```http
POST /auth/email/login
Content-Type: application/json

{
  "email": "user@example.com",
  "pwd": "MySecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### Method 2: Google OAuth2 Login
```http
POST /auth/google/login
Content-Type: application/json

{
  "token": "ya29.a0AfH6SMBk..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439012",
    "email": "user@gmail.com",
    "name": "John Smith"
  }
}
```

### Using Access Tokens

For all protected endpoints, include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Details:**
- **Expires in**: 120 minutes
- **Type**: Bearer token
- **Format**: JWT (JSON Web Token)

### OAuth2 Token Endpoint (Alternative)
```http
POST /auth/access_token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=MySecurePassword123!
```

## 📦 API Response Format

All endpoints return responses in this standardized format:

```json
{
  "status": 1,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

- **status**: Always `1` for successful operations
- **data**: The actual response data (varies by endpoint)
- **message**: Human-readable success message

## 👤 User Management Endpoints

### Create User Account

```http
POST /user/create
Content-Type: application/json

{
  "email": "newuser@example.com",
  "name": "Alice Johnson",
  "pwd": "SecurePassword123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*(),.?":{}|<>)

**Response:**
```json
{
  "status": 1,
  "data": {
    "id": "507f1f77bcf86cd799439013",
    "email": "newuser@example.com",
    "name": "Alice Johnson",
    "created_at": 1642694400,
    "updated_at": 1642694400,
    "is_active": true
  },
  "message": "User registered successfully"
}
```

### Get Current User Info

```http
GET /user/me
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": 1,
  "data": {
    "id": "507f1f77bcf86cd799439013",
    "email": "newuser@example.com",
    "name": "Alice Johnson",
    "created_at": 1642694400,
    "updated_at": 1642694400,
    "is_active": true
  },
  "message": "Welcome, Alice Johnson!"
}
```

## 💰 Transaction Endpoints

### Create Transaction

```http
POST /transaction/create
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "type": "expense",
  "currency": "TWD",
  "amount": 350.0,
  "transaction_date": "2024-01-15T14:30:00Z",
  "category_id": "food_dining",
  "subcategory_id": "lunch",
  "description": "Lunch at Italian restaurant",
  "notes": "Great pasta, will come back",
  "tags": ["restaurant", "italian", "weekend"]
}
```

**Response:**
```json
{
  "status": 1,
  "data": {
    "id": "65a1b2c3d4e5f6789012345",
    "user_id": "507f1f77bcf86cd799439013",
    "user_name": "Alice Johnson",
    "type": "expense",
    "currency": "TWD",
    "amount": 350.0,
    "transaction_date": "2024-01-15T14:30:00Z",
    "category_id": "food_dining",
    "subcategory_id": "lunch",
    "description": "Lunch at Italian restaurant",
    "notes": "Great pasta, will come back",
    "tags": ["restaurant", "italian", "weekend"],
    "created_at": 1642694400,
    "updated_at": 1642694400,
    "is_deleted": false
  },
  "message": "Transaction created successfully"
}
```

### Get Single Transaction

```http
GET /transaction/info/65a1b2c3d4e5f6789012345
Authorization: Bearer <your_access_token>
```

### Get Transaction List (with Pagination & Filters)

```http
GET /transaction/list?page=1&limit=10&start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&transaction_type=expense&category_id=food_dining&sort_by=transaction_date&sort_order=desc
Authorization: Bearer <your_access_token>
```

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `page` | integer | No | Page number (≥1) | `1` |
| `limit` | integer | No | Items per page (1-100) | `20` |
| `start_date` | datetime | No | Filter from date (ISO format) | `2024-01-01T00:00:00Z` |
| `end_date` | datetime | No | Filter to date (ISO format) | `2024-01-31T23:59:59Z` |
| `transaction_type` | enum | No | `income` or `expense` | `expense` |
| `category_id` | enum | No | Category filter | `food_dining` |
| `subcategory_id` | enum | No | Subcategory filter | `lunch` |
| `sort_by` | string | No | Sort field | `transaction_date` |
| `sort_order` | string | No | `asc` or `desc` | `desc` |

**Response:**
```json
{
  "status": 1,
  "data": {
    "transactions": [
      {
        "id": "65a1b2c3d4e5f6789012345",
        "type": "expense",
        "amount": 350.0,
        "transaction_date": "2024-01-15T14:30:00Z",
        "category_id": "food_dining",
        "subcategory_id": "lunch",
        "description": "Lunch at Italian restaurant",
        ...
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 10,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "Transactions fetched successfully"
}
```

### Update Transaction

```http
POST /transaction/update/65a1b2c3d4e5f6789012345
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "amount": 380.0,
  "description": "Lunch at Italian restaurant (updated price)",
  "tags": ["restaurant", "italian", "weekend", "expensive"]
}
```

### Delete Transaction

```http
POST /transaction/delete/65a1b2c3d4e5f6789012345
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": 1,
  "message": "Transaction deleted successfully"
}
```

## 📊 Analytics Endpoints

### Get Analytics Overview

Get comprehensive financial analytics including summaries, trends, and breakdowns.

```http
GET /analytics/overview?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&period=monthly&transaction_type=expense
Authorization: Bearer <your_access_token>
```

**Query Parameters:**

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `start_date` | datetime | No | Analysis start date | null |
| `end_date` | datetime | No | Analysis end date | null |
| `period` | enum | No | `daily`, `weekly`, `monthly`, `yearly` | `monthly` |
| `transaction_type` | enum | No | `income` or `expense` | null |
| `category_id` | enum | No | Filter by category | null |

**Response:**
```json
{
  "status": 1,
  "data": {
    "summary": {
      "total_income": 5000.0,
      "total_expense": 3200.0,
      "net_income": 1800.0,
      "avg_daily_expense": 103.22,
      "largest_expense": {
        "amount": 450.0,
        "description": "Monthly gym membership"
      },
      "most_frequent_category": {
        "category": "food_dining",
        "count": 25
      }
    },
    "category_breakdown": [...],
    "spending_trends": [...],
    "top_tags": [...],
    "period_comparison": [...]
  },
  "message": "Analytics overview fetched successfully"
}
```

### Get Category Breakdown

```http
GET /analytics/category-breakdown?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&transaction_type=expense
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": 1,
  "data": [
    {
      "category_id": "food_dining",
      "category_name": "Food & Dining",
      "total_amount": 1250.0,
      "transaction_count": 25,
      "percentage": 39.06,
      "subcategories": [
        {
          "subcategory_id": "lunch",
          "subcategory_name": "Lunch",
          "total_amount": 650.0,
          "transaction_count": 13
        },
        {
          "subcategory_id": "dinner",
          "subcategory_name": "Dinner",
          "total_amount": 400.0,
          "transaction_count": 8
        }
      ]
    }
  ],
  "message": "Category breakdown fetched successfully"
}
```

### Get Spending Trends

```http
GET /analytics/spending-trends?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&period=daily&category_id=food_dining
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": 1,
  "data": [
    {
      "date": "2024-01-01",
      "amount": 120.0,
      "transaction_count": 2
    },
    {
      "date": "2024-01-02",
      "amount": 85.0,
      "transaction_count": 1
    }
  ],
  "message": "Spending trends fetched successfully"
}
```

### Get Financial Summary

```http
GET /analytics/financial-summary?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
Authorization: Bearer <your_access_token>
```

### Get Tag Analytics

```http
GET /analytics/tag-analytics?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": 1,
  "data": [
    {
      "tag": "restaurant",
      "total_amount": 850.0,
      "transaction_count": 12,
      "avg_amount": 70.83
    },
    {
      "tag": "business",
      "total_amount": 320.0,
      "transaction_count": 4,
      "avg_amount": 80.0
    }
  ],
  "message": "Tag analytics fetched successfully"
}
```

## 🏷️ Categories & Subcategories

### Get All Categories

```http
GET /transaction/category
```

**Response:**
```json
{
  "status": 1,
  "data": {
    "food_dining": {
      "id": "food_dining",
      "name": "Food & Dining",
      "type": "expense",
      "color": "#FF6B6B",
      "icon": "🍽️",
      "subcategories": {
        "lunch": {
          "id": "lunch",
          "name": "Lunch",
          "color": "#FFE66D",
          "icon": "🥗"
        },
        "dinner": {
          "id": "dinner", 
          "name": "Dinner",
          "color": "#FF8E53",
          "icon": "🍽️"
        }
      }
    },
    "transportation": {
      "id": "transportation",
      "name": "Transportation",
      "type": "expense",
      "color": "#4ECDC4",
      "icon": "🚗",
      "subcategories": { ... }
    }
  },
  "message": "Categories fetched successfully"
}
```

### Get Subcategories for Specific Category

```http
GET /transaction/subcategory/food_dining
```

**Response:**
```json
{
  "status": 1,
  "data": {
    "breakfast": {
      "id": "breakfast",
      "name": "Breakfast", 
      "color": "#95E1D3",
      "icon": "🥞"
    },
    "lunch": {
      "id": "lunch",
      "name": "Lunch",
      "color": "#FFE66D", 
      "icon": "🥗"
    },
    "dinner": {
      "id": "dinner",
      "name": "Dinner",
      "color": "#FF8E53",
      "icon": "🍽️"
    }
  },
  "message": "Subcategories fetched successfully"
}
```

## 💼 Complete API Reference

### Authentication Endpoints

#### 🔑 Email/Password Login
```http
POST /auth/email/login
```

**Request Body:**
```json
{
  "email": "user@example.com",    // Valid email format
  "pwd": "SecurePassword123!"     // See password requirements below
}
```

#### 🔑 Google OAuth Login  
```http
POST /auth/google/login
```

**Request Body:**
```json
{
  "token": "google_oauth_token"   // Valid Google OAuth token
}
```

#### 🔑 OAuth2 Token Endpoint
```http
POST /auth/access_token
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
```
username=user@example.com
password=SecurePassword123!
```

#### Validation Errors (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "pwd"],
      "msg": "Password must contain at least one uppercase letter",
      "input": "weakpassword"
    }
  ]
}
```

#### Not Found Errors (404)
```json
{
  "detail": "Transaction not found"
}
```

### HTTP Status Codes Used
- `200`: Success
- `401`: Unauthorized (invalid credentials or expired token)
- `403`: Forbidden (access denied)
- `404`: Not Found (resource doesn't exist)
- `422`: Validation Error (invalid input data)
- `500`: Internal Server Error

## 🔄 Common Usage Patterns

### 1. User Registration and Login Flow
```bash
# 1. Register new user
POST /user/create

# 2. Login to get access token  
POST /auth/email/login

# 3. Use token for subsequent requests
GET /user/me (with Authorization header)
```

### 2. Transaction Management Flow
```bash
# 1. Get available categories
GET /transaction/category

# 2. Create a transaction
POST /transaction/create (with Authorization header)

# 3. List user's transactions
GET /transaction/list (with Authorization header)

# 4. Update or delete as needed
POST /transaction/update/{id} (with Authorization header)
POST /transaction/delete/{id} (with Authorization header)
```

### 3. Analytics Flow
```bash
# 1. Get overview for current month
GET /analytics/overview?period=monthly

# 2. Get detailed category breakdown
GET /analytics/category-breakdown

# 3. Analyze spending trends
GET /analytics/spending-trends?period=daily

# 4. Get tag-based analytics
GET /analytics/tag-analytics
```

---

**💡 Tip**: Use the interactive API documentation at `/scalar` to test endpoints directly in your browser with a user-friendly interface.