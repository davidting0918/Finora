# Finora Frontend API Client

A minimal API client for connecting to the Finora backend API with authentication support.

## 📁 Structure

```
src/lib/api/
├── config.ts          # API configuration and endpoints
├── client.ts           # HTTP client with auth support
├── services/
│   ├── auth.ts        # Authentication service
│   └── index.ts       # Services export
├── index.ts           # Main export
└── README.md          # This file
```

## 🚀 Quick Start

### 1. Basic Usage

```typescript
import { api } from './lib/api'

// Login with email and password
await api.auth.loginWithEmail({
  email: 'user@example.com',
  pwd: 'password'
})

// The token is automatically stored and used for future requests
```

### 2. Using Auth Context

```typescript
import { useAuth } from './lib/contexts/AuthContext'

function LoginComponent() {
  const { login, isAuthenticated, user, logout } = useAuth()

  const handleLogin = async (email: string, password: string) => {
    try {
      await login(email, password)
      // User is now logged in and token is stored
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  const handleLogout = async () => {
    await logout()
    // User is logged out and token is cleared
  }
}
```

## 🔧 Configuration

### Environment Settings

The API client automatically detects the environment:

- **Development**: Connects to `http://localhost:8000`
- **Production**: Connects to `https://api.finora.app`

Override with environment variable:
```bash
REACT_APP_ENV=staging  # or 'production'
```

### API Endpoints

Currently configured endpoints:
```typescript
{
  auth: {
    googleLogin: '/auth/google/login',
    emailLogin: '/auth/email/login',
    accessToken: '/auth/access_token'
  }
}
```

## 🔐 Authentication

### Automatic Token Management

- Login response token is automatically stored in localStorage
- All subsequent API requests include `Authorization: Bearer <token>` header
- Token is cleared on logout or 401 errors
- 401 responses automatically redirect to login page

### Auth Service Methods

```typescript
// Email login
await api.auth.loginWithEmail({ email: 'user@example.com', pwd: 'password' })

// Google OAuth login (token from Google OAuth flow)
await api.auth.loginWithGoogle({ token: 'google-oauth-token' })

// OAuth2 form login
await api.auth.getAccessToken({ username: 'user', password: 'password' })

// Logout (clears stored token)
api.auth.logout()

// Check authentication status
const isAuth = api.auth.isAuthenticated()

// Get stored token
const token = api.auth.getToken()
```

## 🏗️ Adding More API Services

When you're ready to add more functionality, create new service files:

```typescript
// src/lib/api/services/user.ts
export class UserService {
  async getCurrentUser() {
    return apiClient.get('/user/me')
  }
}

// Export in services/index.ts
export { UserService, userService } from './user'
export const api = {
  auth: authService,
  user: userService  // Add new service here
}
```

## 📝 Types

Essential types are defined in `src/lib/types.ts`:

- `AuthUser` - User info returned from login
- `LoginResponse` - Login API response format
- `ApiResponse<T>` - Standard API response wrapper
- `AuthContextType` - React context interface

## 🛠️ HTTP Client Features

The underlying HTTP client (`apiClient`) provides:

- Automatic request/response interceptors
- Token injection for authenticated requests
- Error handling and formatting
- Development environment logging
- Automatic 401 handling (logout + redirect)

## 💡 Usage Tips

1. **Always use the auth context** for login/logout operations
2. **Wrap API calls in try-catch** blocks for error handling
3. **Check authentication state** before accessing protected features
4. **Environment configuration** is automatic but can be overridden

## 🔍 Debugging

In development mode, all API requests and responses are logged to the browser console with detailed information including:
- Request method, URL, headers, and data
- Response status and data
- Error details

Check the browser's developer console for API debugging information.
