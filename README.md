# Finora - Modern Financial Management Platform

A comprehensive personal expense tracking and financial management platform built with FastAPI, designed to help users track transactions, analyze spending patterns, and gain insights into their financial habits.

## 🌟 Features

### 📱 Core Functionality
- **Comprehensive Transaction Management**: Create, read, update, and delete income and expense transactions
- **Smart Categorization**: 11 main categories with 35+ detailed subcategories for precise expense tracking
- **Multi-Currency Support**: Track transactions in USD, TWD, JPY, EUR, and 5 other major currencies
- **Flexible Tagging System**: Add custom tags to transactions for personalized organization

### 🔐 Authentication & Security
- **Multiple Auth Methods**: Email/password login and Google OAuth2 integration
- **JWT Token Security**: Secure API access with Bearer token authentication
- **User Account Management**: Self-registration with secure password requirements

### 📊 Advanced Analytics
- **Financial Overview**: Comprehensive dashboard with income, expenses, and net worth tracking
- **Category Breakdown**: Detailed analysis of spending patterns by category and subcategory
- **Spending Trends**: Time-series analysis with daily, weekly, monthly, and yearly granularity
- **Tag Analytics**: Insights based on custom transaction tags
- **Financial Summary**: High-level metrics and key financial indicators

### 🛠️ Developer-Friendly
- **RESTful API**: Well-structured endpoints following REST principles
- **OpenAPI Documentation**: Interactive API documentation at `/scalar`
- **Comprehensive Filtering**: Advanced query parameters for flexible data retrieval
- **Pagination Support**: Efficient handling of large datasets

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- pip or poetry

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Finora
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the backend directory with:
   ```env
   MONGODB_URL=mongodb://localhost:27017/finora
   JWT_SECRET_KEY=your-secret-key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

4. **Start the application**
   ```bash
   python main.py
   ```

5. **Access the API**
   - Base URL: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/scalar`

## 📚 API Documentation

### Complete API Reference
👉 **[Full API Documentation](./backend/README.md)** - Comprehensive guide covering all endpoints, authentication, and usage examples.

### Key API Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| **Auth** | `POST /auth/email/login` | Email/password authentication |
| **Auth** | `POST /auth/google/login` | Google OAuth2 authentication |
| **User** | `POST /user/create` | Register new user account |
| **User** | `GET /user/me` | Get current user info |
| **Transaction** | `POST /transaction/create` | Create new transaction |
| **Transaction** | `GET /transaction/list` | List transactions with filters |
| **Transaction** | `GET /transaction/category` | Get all categories |
| **Analytics** | `GET /analytics/overview` | Comprehensive financial overview |
| **Analytics** | `GET /analytics/category-breakdown` | Category spending analysis |
| **Analytics** | `GET /analytics/spending-trends` | Time-series spending trends |

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```http
Authorization: Bearer your-jwt-token-here
```

## 🏗️ Project Structure

```
Finora/
├── backend/
│   ├── auth/                  # Authentication modules
│   │   ├── router.py         # Auth endpoints
│   │   ├── service.py        # Auth business logic
│   │   └── providers/        # OAuth providers
│   ├── user/                 # User management
│   ├── transaction/          # Transaction handling
│   ├── analytics/            # Analytics and reporting
│   ├── core/                 # Core utilities
│   │   ├── database.py       # MongoDB connection
│   │   ├── initializer.py    # App initialization
│   │   └── model/            # Data models
│   ├── data/                 # Static data and fixtures
│   ├── tests/                # Test cases
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
└── README.md                 # This file
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with OAuth2, Google OAuth
- **API Documentation**: Scalar (OpenAPI 3.1)
- **Testing**: pytest with pytest-asyncio
- **Validation**: Pydantic models

## 📊 Supported Categories

### Expense Categories
- 🛍️ **Shopping**: Clothing, Electronics, Home goods
- 🍽️ **Food & Dining**: Breakfast, Lunch, Dinner, Snacks, Drinks
- 🚗 **Transportation**: Bus, Train, Taxi, Parking
- 🎬 **Entertainment**: Movies, Concerts, Sports, Games
- 🏠 **Living**: Rent, Utilities, Telecom
- 📚 **Education**: Tuition, Software, Books
- 🏥 **Health**: Medical, Insurance
- 📈 **Investment**: Stocks, Mutual funds, Crypto
- ✈️ **Travel**: Hotels, Flights, Tours

### Income Categories
- 💼 **Income**: Salary, Freelance, Investments

## 🧪 Testing

Run the test suite:
```bash
cd backend
pytest
```

Tests are located in the `backend/tests/` directory and cover:
- Authentication endpoints
- Transaction management
- Analytics functionality
- User management

## 🔧 Development

### API Response Format
All successful API responses follow this structure:
```json
{
  "status": 1,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Currency Support
- USD (US Dollar)
- TWD (Taiwan Dollar)
- JPY (Japanese Yen)
- EUR (Euro)
- GBP (British Pound)
- CAD (Canadian Dollar)
- HKD (Hong Kong Dollar)
- CNY (Chinese Yuan)
- KRW (Korean Won)

## 📈 Analytics Features

- **Real-time Dashboard**: Live financial overview with key metrics
- **Trend Analysis**: Historical spending patterns and projections
- **Category Insights**: Detailed breakdown by expense categories
- **Budget Tracking**: Monitor spending against set budgets
- **Export Capabilities**: Download financial data for external analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For API documentation and detailed usage examples, please refer to the [Backend API Documentation](./backend/README.md).

---

*Built with ❤️ using FastAPI, MongoDB, and modern web technologies.*
