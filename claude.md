# Finora - Expense Tracking Platform Architecture Design

## Project Overview
Finora is a modern expense tracking platform that provides income and expense recording functionality with a predefined category system.

> **Note:** This is the simplified v1 design with system-defined categories only. User custom categories will be added in future versions.

## Current Architecture Analysis

### Completed Core Components
✅ **User Management System**
- JWT authentication mechanism
- Google OAuth integration
- Email/password login
- Complete user model and service layer

✅ **Database Architecture**
- MongoDB async connection (Motor)
- Clean database abstraction layer
- Test mode support

✅ **API Structure**
- FastAPI framework
- Router/service separation pattern
- Pydantic model validation
- Comprehensive error handling

## Transaction System Design

### 1. Data Model Structure

#### Transaction Model
```python
class Transaction(BaseModel):
    id: str
    user_id: str
    type: TransactionType
    amount: Decimal              # Using Decimal for financial precision
    transaction_date: datetime   # More semantic than timestamp
    category_id: str            # Consistent naming
    subcategory_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: int
    updated_at: int
    is_deleted: bool = False

    # Field validations for data integrity
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
```

#### Category Model
```python
class Category(BaseModel):
    id: str
    name: str
    type: TransactionType    # income or expense
    color: str
    icon: str
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v.strip()
```

#### SubCategory Model
```python
class SubCategory(BaseModel):
    id: str
    category_id: str         # Parent category ID
    name: str
    color: str
    icon: str
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v.strip()
```

### 2. Default Category System (JSON-based)

> **✨ New Approach**: Default categories and subcategories are now stored in a JSON configuration file (`backend/data/default_categories.json`) for easy maintenance and modification.

#### Expense Categories
```python
DEFAULT_EXPENSE_CATEGORIES = {
    "food_dining": {
        "name": "Food & Dining",
        "icon": "🍽️",
        "color": "#FF6B6B",
        "subcategories": ["Restaurant", "Fast Food", "Coffee", "Delivery", "Groceries"]
    },
    "transportation": {
        "name": "Transportation",
        "icon": "🚗",
        "color": "#4ECDC4",
        "subcategories": ["Bus", "Subway", "Taxi", "Gas", "Parking"]
    },
    "shopping": {
        "name": "Shopping",
        "icon": "🛍️",
        "color": "#45B7D1",
        "subcategories": ["Clothing", "Electronics", "Home", "Beauty", "Books"]
    },
    "entertainment": {
        "name": "Entertainment",
        "icon": "🎮",
        "color": "#96CEB4",
        "subcategories": ["Movies", "Games", "Music", "Sports", "Travel"]
    },
    "bills_utilities": {
        "name": "Bills & Utilities",
        "icon": "💡",
        "color": "#FECA57",
        "subcategories": ["Electricity", "Water", "Gas", "Internet", "Phone"]
    },
    "healthcare": {
        "name": "Healthcare",
        "icon": "🏥",
        "color": "#FF9FF3",
        "subcategories": ["Doctor", "Medicine", "Insurance", "Checkup", "Beauty"]
    },
    "education": {
        "name": "Education",
        "icon": "📚",
        "color": "#54A0FF",
        "subcategories": ["Tuition", "Courses", "Books", "Tutoring", "Certification"]
    }
}
```

#### Income Categories
```python
DEFAULT_INCOME_CATEGORIES = {
    "salary": {
        "name": "Salary",
        "icon": "💰",
        "color": "#2ECC71",
        "subcategories": ["Base Salary", "Bonus", "Overtime", "Allowance", "Year-end Bonus"]
    },
    "business": {
        "name": "Business Income",
        "icon": "🏢",
        "color": "#3498DB",
        "subcategories": ["Sales", "Services", "Consulting", "Partnership", "Commission"]
    },
    "investment": {
        "name": "Investment Returns",
        "icon": "📈",
        "color": "#9B59B6",
        "subcategories": ["Stocks", "Mutual Funds", "Bonds", "Real Estate", "Cryptocurrency"]
    },
    "freelance": {
        "name": "Freelance",
        "icon": "💻",
        "color": "#E74C3C",
        "subcategories": ["Design", "Programming", "Writing", "Translation", "Consulting"]
    },
    "passive": {
        "name": "Passive Income",
        "icon": "🎯",
        "color": "#F39C12",
        "subcategories": ["Rent", "Royalties", "Interest", "Dividends", "Licensing"]
    }
}
```

### 3. Data Management System

#### JSON Configuration Files
```
backend/data/default_categories.json    # Default categories and subcategories
```

#### Data Loading Architecture
```python
# CategoryDataLoader - Loads and validates JSON data
from backend.core.data_loader import CategoryDataLoader

loader = CategoryDataLoader()
categories = loader.get_categories()
subcategories = loader.get_subcategories()

# Get filtered data
income_cats = loader.get_categories_by_type('income')
food_subcats = loader.get_subcategories_by_category('food_dining')
```

#### Database Initialization
```python
# DatabaseInitializer - Loads from JSON and populates database
from backend.core.database_init import DatabaseInitializer

initializer = DatabaseInitializer()
await initializer.initialize_default_data()  # Only if data doesn't exist
await initializer.reset_default_data()       # Force reset (dev only)
```

#### Management Scripts
```bash
# Test JSON data validity
python scripts/test_json_data.py

# Interactive category management
python scripts/manage_categories.py

# Command-line database management
./scripts/manage_database.sh init
```

### 4. API Endpoint Design

#### Transaction Endpoints
```
POST   /transactions              # Create transaction
GET    /transactions              # Get transaction list (with filtering)
GET    /transactions/{id}         # Get single transaction
PUT    /transactions/{id}         # Update transaction
DELETE /transactions/{id}         # Delete transaction
GET    /transactions/summary      # Transaction summary statistics
GET    /transactions/analytics    # Transaction analytics data
```

#### Category Management Endpoints
```
GET    /categories               # Get all system categories
GET    /categories/income        # Get income categories
GET    /categories/expense       # Get expense categories
```

#### Subcategory Management Endpoints
```
GET    /subcategories            # Get subcategory list
GET    /categories/{id}/subcategories  # Get subcategories for specific category
```

### 5. Database Collection Structure

#### Collection List
- `transactions` - Transaction records
- `categories` - Category data
- `subcategories` - Subcategory data

#### Index Design
```python
# transactions collection indexes
{
    "user_id": 1,
    "date": -1
},
{
    "user_id": 1,
    "type": 1,
    "date": -1
},
{
    "user_id": 1,
    "category_id": 1
}

# categories collection indexes
{
    "type": 1,
    "is_active": 1
},
{
    "is_active": 1
}
```

### 6. 業務邏輯規則

### 6. Business Logic Rules

#### Transaction Validation Rules
- Amount must be greater than 0
- Date cannot be too far in the future (prevent input errors)
- Categories and subcategories must exist and be valid
- Users can only operate on their own transaction records

#### Category Validation Rules
- System default categories cannot be modified/deleted
- Categories and subcategories must exist and be valid
- Categories are read-only in the first version

### 7. Security Considerations

#### Data Isolation
- All APIs require JWT authentication
- Users can only access their own data
- Soft delete mechanism protects important data

#### Input Validation
- Use Pydantic for strict validation of all inputs
- Use Decimal for amount fields to avoid floating-point errors
- XSS protection and SQL injection prevention

### 8. Implementation Priority

#### Phase 1: Core Features
1. Transaction models and basic CRUD operations
2. System default category initialization
3. Basic transaction statistics

#### Phase 2: Advanced Features
1. Transaction filtering and search
2. Data export functionality
3. Transaction analytics and reporting

#### Phase 3: Analytics Features
1. Detailed statistical analysis
2. Chart visualization
3. Budget tracking

### 9. Testing Strategy

#### Test Coverage
- Unit testing: All service layer logic
- Integration testing: API endpoint testing
- Data validation testing: Pydantic model validation
- Security testing: Permission control testing

### 10. Deployment Considerations

#### Environment Configuration
- MongoDB connection setup
- JWT key management
- Environment variable configuration
- Docker containerization

#### Monitoring Metrics
- API response time
- Database query performance
- User usage statistics
- Error rate monitoring

---

## Development Checklist

### Required Endpoints to Implement
- [ ] POST /transactions - Create transaction
- [ ] GET /transactions - Transaction list (pagination, filtering)
- [ ] GET /transactions/{id} - Single transaction details
- [ ] PUT /transactions/{id} - Update transaction
- [ ] DELETE /transactions/{id} - Delete transaction
- [ ] GET /transactions/summary - Income/expense statistics
- [ ] GET /categories - Get all system categories
- [ ] GET /categories/income - Get income categories
- [ ] GET /categories/expense - Get expense categories
- [ ] GET /categories/{id}/subcategories - Get subcategories for category

### Data Model Checklist
- [ ] Complete Transaction model implementation
- [ ] Complete Category model implementation
- [ ] Complete SubCategory model implementation
- [ ] All necessary Pydantic validators
- [ ] Database index optimization

### Security Checklist
- [ ] All endpoints require authentication
- [ ] User data isolation verification
- [ ] Input validation and sanitization
- [ ] Error handling doesn't leak sensitive information

### Test Coverage
- [ ] Transaction CRUD operation tests
- [ ] Category retrieval tests
- [ ] Permission control tests
- [ ] Boundary condition tests
- [ ] Data validation tests

---

*This document will be continuously updated as development progresses*
