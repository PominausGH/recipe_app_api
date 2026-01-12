# React Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a React SPA frontend for the Recipe Sharing Platform API.

**Architecture:** Vite-based React app with React Query for server state, Axios for API calls with JWT interceptors, and Tailwind CSS for styling. Feature-based folder structure with shared UI components.

**Tech Stack:** React 18, Vite, React Router v6, TanStack Query, Axios, Tailwind CSS, React Hook Form

---

## Phase 1: Project Setup

### Task 1.1: Initialize Vite React Project

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`

**Step 1: Create frontend directory and initialize Vite**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
npm create vite@latest frontend -- --template react
```

**Step 2: Verify project created**

```bash
ls frontend/
```
Expected: `index.html`, `package.json`, `src/`, `vite.config.js`

**Step 3: Install dependencies**

```bash
cd frontend && npm install
```

**Step 4: Test dev server starts**

```bash
npm run dev &
sleep 3
curl -s http://localhost:5173 | head -5
pkill -f "vite"
```
Expected: HTML response with Vite app

**Step 5: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/
git commit -m "feat(frontend): initialize Vite React project"
```

---

### Task 1.2: Install Dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install production dependencies**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api/frontend
npm install react-router-dom @tanstack/react-query axios react-hook-form @headlessui/react @heroicons/react
```

**Step 2: Install Tailwind CSS**

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Step 3: Verify package.json has all dependencies**

```bash
cat package.json | grep -E "(react-router|tanstack|axios|tailwind)"
```
Expected: All packages listed

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/
git commit -m "feat(frontend): install core dependencies"
```

---

### Task 1.3: Configure Tailwind CSS

**Files:**
- Modify: `frontend/tailwind.config.js`
- Create: `frontend/src/index.css`

**Step 1: Update tailwind.config.js**

Replace `frontend/tailwind.config.js` with:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
      },
    },
  },
  plugins: [],
}
```

**Step 2: Create src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-50 text-gray-900;
}
```

**Step 3: Update src/main.jsx to import CSS**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Step 4: Verify Tailwind works**

Update `src/App.jsx`:

```jsx
function App() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <h1 className="text-4xl font-bold text-primary-600">Recipe App</h1>
    </div>
  )
}

export default App
```

**Step 5: Test in browser**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api/frontend
npm run dev &
sleep 3
curl -s http://localhost:5173 | grep -q "root" && echo "Dev server running"
pkill -f "vite"
```

**Step 6: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/
git commit -m "feat(frontend): configure Tailwind CSS with custom theme"
```

---

### Task 1.4: Configure Vite Proxy and Environment

**Files:**
- Modify: `frontend/vite.config.js`
- Create: `frontend/.env.example`
- Create: `frontend/.env`

**Step 1: Update vite.config.js with API proxy**

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**Step 2: Create .env.example**

```
VITE_API_URL=/api
```

**Step 3: Create .env**

```
VITE_API_URL=/api
```

**Step 4: Add .env to .gitignore**

```bash
echo "frontend/.env" >> /home/andrew/Documents/Python/Git/recipe_app_api/.gitignore
```

**Step 5: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add .gitignore frontend/vite.config.js frontend/.env.example
git commit -m "feat(frontend): configure Vite proxy for API"
```

---

## Phase 2: API Client and Authentication

### Task 2.1: Create Axios Client with JWT Interceptors

**Files:**
- Create: `frontend/src/api/client.js`

**Step 1: Create api directory**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/api
```

**Step 2: Create client.js**

```javascript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

export const clearTokens = () => {
  accessToken = null;
  localStorage.removeItem('refreshToken');
};

// Request interceptor - attach access token
client.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const newAccessToken = response.data.access;
          setAccessToken(newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return client(originalRequest);
        } catch (refreshError) {
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export default client;
```

**Step 3: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/api/
git commit -m "feat(frontend): add Axios client with JWT interceptors"
```

---

### Task 2.2: Create Auth API Functions

**Files:**
- Create: `frontend/src/api/auth.js`

**Step 1: Create auth.js**

```javascript
import client, { setAccessToken, clearTokens } from './client';

export const authApi = {
  async login(email, password) {
    const response = await client.post('/auth/login/', { email, password });
    const { access, refresh } = response.data;
    setAccessToken(access);
    localStorage.setItem('refreshToken', refresh);
    return response.data;
  },

  async register(email, name, password, password_confirm) {
    const response = await client.post('/auth/register/', {
      email,
      name,
      password,
      password_confirm,
    });
    return response.data;
  },

  async logout() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      try {
        await client.post('/auth/logout/', { refresh: refreshToken });
      } catch (error) {
        // Ignore logout errors
      }
    }
    clearTokens();
  },

  async getMe() {
    const response = await client.get('/auth/me/');
    return response.data;
  },

  async updateMe(data) {
    const response = await client.patch('/auth/me/', data);
    return response.data;
  },

  async updateProfilePhoto(file) {
    const formData = new FormData();
    formData.append('profile_photo', file);
    const response = await client.patch('/auth/me/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/api/auth.js
git commit -m "feat(frontend): add auth API functions"
```

---

### Task 2.3: Create Auth Context

**Files:**
- Create: `frontend/src/features/auth/AuthContext.jsx`
- Create: `frontend/src/hooks/useAuth.js`

**Step 1: Create directories**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/features/auth
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/hooks
```

**Step 2: Create AuthContext.jsx**

```jsx
import { createContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../../api/auth';
import { setAccessToken, clearTokens } from '../../api/client';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      fetchUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  const login = async (email, password) => {
    await authApi.login(email, password);
    await fetchUser();
  };

  const register = async (email, name, password, passwordConfirm) => {
    await authApi.register(email, name, password, passwordConfirm);
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const updateProfile = async (data) => {
    const updatedUser = await authApi.updateMe(data);
    setUser(updatedUser);
    return updatedUser;
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshUser: fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

**Step 3: Create useAuth.js hook**

```javascript
import { useContext } from 'react';
import { AuthContext } from '../features/auth/AuthContext';

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/features/ frontend/src/hooks/
git commit -m "feat(frontend): add AuthContext and useAuth hook"
```

---

### Task 2.4: Create ProtectedRoute Component

**Files:**
- Create: `frontend/src/features/auth/ProtectedRoute.jsx`

**Step 1: Create ProtectedRoute.jsx**

```jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/features/auth/ProtectedRoute.jsx
git commit -m "feat(frontend): add ProtectedRoute component"
```

---

## Phase 3: UI Components and Layout

### Task 3.1: Create Base UI Components

**Files:**
- Create: `frontend/src/components/ui/Button.jsx`
- Create: `frontend/src/components/ui/Input.jsx`
- Create: `frontend/src/components/ui/Card.jsx`
- Create: `frontend/src/components/ui/Spinner.jsx`
- Create: `frontend/src/components/ui/index.js`

**Step 1: Create directories**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/components/ui
```

**Step 2: Create Button.jsx**

```jsx
import { forwardRef } from 'react';

const variants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
  secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button = forwardRef(function Button(
  { variant = 'primary', size = 'md', className = '', disabled, children, ...props },
  ref
) {
  return (
    <button
      ref={ref}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center font-medium rounded-md
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors duration-200
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
});
```

**Step 3: Create Input.jsx**

```jsx
import { forwardRef } from 'react';

export const Input = forwardRef(function Input(
  { label, error, className = '', ...props },
  ref
) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        ref={ref}
        className={`
          w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${className}
        `}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
});
```

**Step 4: Create Card.jsx**

```jsx
export function Card({ className = '', children, ...props }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ className = '', children }) {
  return <div className={`px-6 py-4 border-b ${className}`}>{children}</div>;
};

Card.Body = function CardBody({ className = '', children }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
};

Card.Footer = function CardFooter({ className = '', children }) {
  return <div className={`px-6 py-4 border-t bg-gray-50 ${className}`}>{children}</div>;
};
```

**Step 5: Create Spinner.jsx**

```jsx
export function Spinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div
      className={`animate-spin rounded-full border-b-2 border-primary-600 ${sizes[size]} ${className}`}
    />
  );
}
```

**Step 6: Create index.js barrel export**

```javascript
export { Button } from './Button';
export { Input } from './Input';
export { Card } from './Card';
export { Spinner } from './Spinner';
```

**Step 7: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/components/
git commit -m "feat(frontend): add base UI components"
```

---

### Task 3.2: Create Layout Components

**Files:**
- Create: `frontend/src/layouts/MainLayout.jsx`
- Create: `frontend/src/layouts/AuthLayout.jsx`
- Create: `frontend/src/components/Navbar.jsx`

**Step 1: Create directories**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/layouts
```

**Step 2: Create Navbar.jsx**

```jsx
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              RecipeApp
            </Link>
            <div className="hidden md:flex ml-10 space-x-4">
              <Link to="/recipes" className="text-gray-700 hover:text-primary-600 px-3 py-2">
                Browse Recipes
              </Link>
              {isAuthenticated && (
                <>
                  <Link to="/recipes/new" className="text-gray-700 hover:text-primary-600 px-3 py-2">
                    Create Recipe
                  </Link>
                  <Link to="/my-recipes" className="text-gray-700 hover:text-primary-600 px-3 py-2">
                    My Recipes
                  </Link>
                  <Link to="/favorites" className="text-gray-700 hover:text-primary-600 px-3 py-2">
                    Favorites
                  </Link>
                </>
              )}
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="text-gray-700 hover:text-primary-600">
                  {user?.name || 'Profile'}
                </Link>
                <Button variant="ghost" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost">Login</Button>
                </Link>
                <Link to="/register">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t">
          <div className="px-4 py-2 space-y-1">
            <Link to="/recipes" className="block px-3 py-2 text-gray-700">
              Browse Recipes
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/recipes/new" className="block px-3 py-2 text-gray-700">
                  Create Recipe
                </Link>
                <Link to="/my-recipes" className="block px-3 py-2 text-gray-700">
                  My Recipes
                </Link>
                <Link to="/favorites" className="block px-3 py-2 text-gray-700">
                  Favorites
                </Link>
                <Link to="/profile" className="block px-3 py-2 text-gray-700">
                  Profile
                </Link>
                <button onClick={handleLogout} className="block px-3 py-2 text-gray-700">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="block px-3 py-2 text-gray-700">
                  Login
                </Link>
                <Link to="/register" className="block px-3 py-2 text-gray-700">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
```

**Step 3: Create MainLayout.jsx**

```jsx
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';

export function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-500">
          Recipe Sharing Platform
        </div>
      </footer>
    </div>
  );
}
```

**Step 4: Create AuthLayout.jsx**

```jsx
import { Outlet, Link } from 'react-router-dom';

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex justify-center">
          <span className="text-3xl font-bold text-primary-600">RecipeApp</span>
        </Link>
      </div>
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
```

**Step 5: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/layouts/ frontend/src/components/Navbar.jsx
git commit -m "feat(frontend): add layout components and navbar"
```

---

## Phase 4: Auth Pages

### Task 4.1: Create Login Page

**Files:**
- Create: `frontend/src/pages/LoginPage.jsx`
- Create: `frontend/src/features/auth/LoginForm.jsx`

**Step 1: Create pages directory**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/pages
```

**Step 2: Create LoginForm.jsx**

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../hooks/useAuth';
import { Button, Input } from '../../components/ui';

export function LoginForm({ onSuccess }) {
  const { login } = useAuth();
  const [error, setError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    try {
      setError('');
      await login(data.email, data.password);
      onSuccess?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
          {error}
        </div>
      )}

      <Input
        label="Email"
        type="email"
        {...register('email', { required: 'Email is required' })}
        error={errors.email?.message}
      />

      <Input
        label="Password"
        type="password"
        {...register('password', { required: 'Password is required' })}
        error={errors.password?.message}
      />

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Signing in...' : 'Sign In'}
      </Button>
    </form>
  );
}
```

**Step 3: Create LoginPage.jsx**

```jsx
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LoginForm } from '../features/auth/LoginForm';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const handleSuccess = () => {
    navigate(from, { replace: true });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-center mb-6">Sign In</h2>
      <LoginForm onSuccess={handleSuccess} />
      <p className="mt-6 text-center text-gray-600">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-600 hover:text-primary-500">
          Sign up
        </Link>
      </p>
    </div>
  );
}
```

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/ frontend/src/features/auth/LoginForm.jsx
git commit -m "feat(frontend): add login page and form"
```

---

### Task 4.2: Create Register Page

**Files:**
- Create: `frontend/src/pages/RegisterPage.jsx`
- Create: `frontend/src/features/auth/RegisterForm.jsx`

**Step 1: Create RegisterForm.jsx**

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../hooks/useAuth';
import { Button, Input } from '../../components/ui';

export function RegisterForm({ onSuccess }) {
  const { register: registerUser } = useAuth();
  const [error, setError] = useState('');
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm();
  const password = watch('password');

  const onSubmit = async (data) => {
    try {
      setError('');
      await registerUser(data.email, data.name, data.password, data.password_confirm);
      onSuccess?.();
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        const messages = Object.values(errorData).flat().join(' ');
        setError(messages || 'Registration failed.');
      } else {
        setError('Registration failed. Please try again.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
          {error}
        </div>
      )}

      <Input
        label="Name"
        {...register('name', { required: 'Name is required' })}
        error={errors.name?.message}
      />

      <Input
        label="Email"
        type="email"
        {...register('email', { required: 'Email is required' })}
        error={errors.email?.message}
      />

      <Input
        label="Password"
        type="password"
        {...register('password', {
          required: 'Password is required',
          minLength: { value: 8, message: 'Password must be at least 8 characters' },
        })}
        error={errors.password?.message}
      />

      <Input
        label="Confirm Password"
        type="password"
        {...register('password_confirm', {
          required: 'Please confirm your password',
          validate: (value) => value === password || 'Passwords do not match',
        })}
        error={errors.password_confirm?.message}
      />

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Creating account...' : 'Create Account'}
      </Button>
    </form>
  );
}
```

**Step 2: Create RegisterPage.jsx**

```jsx
import { Link, useNavigate } from 'react-router-dom';
import { RegisterForm } from '../features/auth/RegisterForm';

export function RegisterPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/login', { state: { message: 'Account created! Please sign in.' } });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-center mb-6">Create Account</h2>
      <RegisterForm onSuccess={handleSuccess} />
      <p className="mt-6 text-center text-gray-600">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-600 hover:text-primary-500">
          Sign in
        </Link>
      </p>
    </div>
  );
}
```

**Step 3: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/RegisterPage.jsx frontend/src/features/auth/RegisterForm.jsx
git commit -m "feat(frontend): add register page and form"
```

---

## Phase 5: Recipe API and Components

### Task 5.1: Create Recipe API Functions

**Files:**
- Create: `frontend/src/api/recipes.js`

**Step 1: Create recipes.js**

```javascript
import client from './client';

export const recipesApi = {
  async list(params = {}) {
    const response = await client.get('/recipes/', { params });
    return response.data;
  },

  async get(id) {
    const response = await client.get(`/recipes/${id}/`);
    return response.data;
  },

  async create(data) {
    const response = await client.post('/recipes/', data);
    return response.data;
  },

  async update(id, data) {
    const response = await client.patch(`/recipes/${id}/`, data);
    return response.data;
  },

  async delete(id) {
    await client.delete(`/recipes/${id}/`);
  },

  async uploadImage(id, file) {
    const formData = new FormData();
    formData.append('image', file);
    const response = await client.post(`/recipes/${id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async rate(id, score, review = '') {
    const response = await client.post(`/recipes/${id}/rate/`, { score, review });
    return response.data;
  },

  async toggleFavorite(id) {
    const response = await client.post(`/recipes/${id}/favorite/`);
    return response.data;
  },

  async getComments(id) {
    const response = await client.get(`/recipes/${id}/comments/`);
    return response.data;
  },

  async addComment(id, text, parentId = null) {
    const data = { text };
    if (parentId) data.parent = parentId;
    const response = await client.post(`/recipes/${id}/comments/`, data);
    return response.data;
  },

  async getMyRecipes(params = {}) {
    const response = await client.get('/recipes/', { params: { ...params, author: 'me' } });
    return response.data;
  },
};
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/api/recipes.js
git commit -m "feat(frontend): add recipe API functions"
```

---

### Task 5.2: Create useRecipes Hook

**Files:**
- Create: `frontend/src/hooks/useRecipes.js`

**Step 1: Create useRecipes.js**

```javascript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recipesApi } from '../api/recipes';

export const recipeKeys = {
  all: ['recipes'],
  lists: () => [...recipeKeys.all, 'list'],
  list: (filters) => [...recipeKeys.lists(), filters],
  details: () => [...recipeKeys.all, 'detail'],
  detail: (id) => [...recipeKeys.details(), id],
  comments: (id) => [...recipeKeys.detail(id), 'comments'],
  myRecipes: () => [...recipeKeys.all, 'my'],
};

export function useRecipes(filters = {}) {
  return useQuery({
    queryKey: recipeKeys.list(filters),
    queryFn: () => recipesApi.list(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecipe(id) {
  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: () => recipesApi.get(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
}

export function useRecipeComments(id) {
  return useQuery({
    queryKey: recipeKeys.comments(id),
    queryFn: () => recipesApi.getComments(id),
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useUpdateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => recipesApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useRateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, score, review }) => recipesApi.rate(id, score, review),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}

export function useToggleFavorite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.toggleFavorite,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}

export function useAddComment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recipeId, text, parentId }) => recipesApi.addComment(recipeId, text, parentId),
    onSuccess: (_, { recipeId }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.comments(recipeId) });
    },
  });
}

export function useUploadRecipeImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, file }) => recipesApi.uploadImage(id, file),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/hooks/useRecipes.js
git commit -m "feat(frontend): add useRecipes hook with React Query"
```

---

### Task 5.3: Create RecipeCard Component

**Files:**
- Create: `frontend/src/components/RecipeCard.jsx`

**Step 1: Create RecipeCard.jsx**

```jsx
import { Link } from 'react-router-dom';
import { ClockIcon, StarIcon } from '@heroicons/react/24/solid';
import { Card } from './ui';

const difficultyColors = {
  easy: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  hard: 'bg-red-100 text-red-800',
};

export function RecipeCard({ recipe }) {
  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0);

  return (
    <Link to={`/recipes/${recipe.id}`}>
      <Card className="h-full hover:shadow-lg transition-shadow">
        <div className="aspect-video bg-gray-200 relative">
          {recipe.image ? (
            <img
              src={recipe.image}
              alt={recipe.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
          {recipe.difficulty && (
            <span
              className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium ${
                difficultyColors[recipe.difficulty]
              }`}
            >
              {recipe.difficulty}
            </span>
          )}
        </div>
        <Card.Body>
          <h3 className="font-semibold text-lg mb-2 line-clamp-2">{recipe.title}</h3>
          <p className="text-gray-600 text-sm mb-3">
            by {recipe.author?.name || 'Unknown'}
          </p>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <StarIcon className="h-4 w-4 text-yellow-400" />
              <span>
                {recipe.average_rating?.toFixed(1) || 'N/A'}
                {recipe.rating_count > 0 && ` (${recipe.rating_count})`}
              </span>
            </div>
            {totalTime > 0 && (
              <div className="flex items-center gap-1">
                <ClockIcon className="h-4 w-4" />
                <span>{totalTime} min</span>
              </div>
            )}
          </div>
        </Card.Body>
      </Card>
    </Link>
  );
}
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/components/RecipeCard.jsx
git commit -m "feat(frontend): add RecipeCard component"
```

---

### Task 5.4: Create RatingStars Component

**Files:**
- Create: `frontend/src/components/RatingStars.jsx`

**Step 1: Create RatingStars.jsx**

```jsx
import { useState } from 'react';
import { StarIcon } from '@heroicons/react/24/solid';
import { StarIcon as StarOutlineIcon } from '@heroicons/react/24/outline';

export function RatingStars({
  rating = 0,
  count,
  interactive = false,
  onRate,
  size = 'md',
}) {
  const [hoverRating, setHoverRating] = useState(0);

  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  const handleClick = (star) => {
    if (interactive && onRate) {
      onRate(star);
    }
  };

  return (
    <div className="flex items-center gap-1">
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => {
          const filled = interactive
            ? star <= (hoverRating || rating)
            : star <= rating;

          return (
            <button
              key={star}
              type="button"
              disabled={!interactive}
              onClick={() => handleClick(star)}
              onMouseEnter={() => interactive && setHoverRating(star)}
              onMouseLeave={() => interactive && setHoverRating(0)}
              className={`${interactive ? 'cursor-pointer' : 'cursor-default'}`}
            >
              {filled ? (
                <StarIcon className={`${sizes[size]} text-yellow-400`} />
              ) : (
                <StarOutlineIcon className={`${sizes[size]} text-gray-300`} />
              )}
            </button>
          );
        })}
      </div>
      {count !== undefined && (
        <span className="text-sm text-gray-500 ml-1">({count})</span>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/components/RatingStars.jsx
git commit -m "feat(frontend): add RatingStars component"
```

---

### Task 5.5: Create Home Page

**Files:**
- Create: `frontend/src/pages/HomePage.jsx`

**Step 1: Create HomePage.jsx**

```jsx
import { Link } from 'react-router-dom';
import { useRecipes } from '../hooks/useRecipes';
import { RecipeCard } from '../components/RecipeCard';
import { Button, Spinner } from '../components/ui';

export function HomePage() {
  const { data: featuredData, isLoading: loadingFeatured } = useRecipes({
    ordering: '-avg_rating',
    page_size: 4,
  });
  const { data: recentData, isLoading: loadingRecent } = useRecipes({
    ordering: '-created_at',
    page_size: 4,
  });

  return (
    <div>
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-primary-500 to-primary-600 -mx-4 sm:-mx-6 lg:-mx-8 px-4 mb-12 rounded-b-3xl">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Discover Delicious Recipes
        </h1>
        <p className="text-xl text-primary-100 mb-8">
          Share your culinary creations with the world
        </p>
        <Link to="/recipes">
          <Button size="lg" variant="secondary">
            Browse Recipes
          </Button>
        </Link>
      </section>

      {/* Featured Recipes */}
      <section className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Top Rated</h2>
          <Link to="/recipes?ordering=-avg_rating" className="text-primary-600 hover:text-primary-700">
            View all
          </Link>
        </div>
        {loadingFeatured ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredData?.results?.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>

      {/* Recent Recipes */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Recently Added</h2>
          <Link to="/recipes?ordering=-created_at" className="text-primary-600 hover:text-primary-700">
            View all
          </Link>
        </div>
        {loadingRecent ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recentData?.results?.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
```

**Step 2: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/HomePage.jsx
git commit -m "feat(frontend): add home page with featured recipes"
```

---

### Task 5.6: Create Recipe List Page with Filters

**Files:**
- Create: `frontend/src/pages/RecipeListPage.jsx`
- Create: `frontend/src/components/RecipeFilters.jsx`
- Create: `frontend/src/hooks/useDebounce.js`

**Step 1: Create useDebounce.js**

```javascript
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

**Step 2: Create RecipeFilters.jsx**

```jsx
import { Input, Button } from './ui';

const difficulties = [
  { value: '', label: 'All Difficulties' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

const sortOptions = [
  { value: '-created_at', label: 'Newest First' },
  { value: 'created_at', label: 'Oldest First' },
  { value: '-avg_rating', label: 'Highest Rated' },
  { value: 'prep_time', label: 'Quickest' },
];

export function RecipeFilters({ filters, onChange, onClear }) {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Search
        </label>
        <Input
          type="text"
          placeholder="Search recipes..."
          value={filters.search || ''}
          onChange={(e) => handleChange('search', e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Difficulty
        </label>
        <select
          value={filters.difficulty || ''}
          onChange={(e) => handleChange('difficulty', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          {difficulties.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Max Time (minutes)
        </label>
        <Input
          type="number"
          placeholder="e.g., 30"
          value={filters.max_time || ''}
          onChange={(e) => handleChange('max_time', e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Sort By
        </label>
        <select
          value={filters.ordering || '-created_at'}
          onChange={(e) => handleChange('ordering', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          {sortOptions.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <Button variant="ghost" onClick={onClear} className="w-full">
        Clear Filters
      </Button>
    </div>
  );
}
```

**Step 3: Create RecipeListPage.jsx**

```jsx
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useRecipes } from '../hooks/useRecipes';
import { useDebounce } from '../hooks/useDebounce';
import { RecipeCard } from '../components/RecipeCard';
import { RecipeFilters } from '../components/RecipeFilters';
import { Spinner, Button } from '../components/ui';

export function RecipeListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    difficulty: searchParams.get('difficulty') || '',
    max_time: searchParams.get('max_time') || '',
    ordering: searchParams.get('ordering') || '-created_at',
    page: parseInt(searchParams.get('page') || '1', 10),
  });

  const debouncedSearch = useDebounce(filters.search, 300);

  const queryFilters = {
    ...filters,
    search: debouncedSearch,
  };
  Object.keys(queryFilters).forEach((key) => {
    if (!queryFilters[key]) delete queryFilters[key];
  });

  const { data, isLoading, error } = useRecipes(queryFilters);

  const handleFilterChange = (newFilters) => {
    setFilters({ ...newFilters, page: 1 });
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    setSearchParams(params);
  };

  const handleClearFilters = () => {
    setFilters({
      search: '',
      difficulty: '',
      max_time: '',
      ordering: '-created_at',
      page: 1,
    });
    setSearchParams({});
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
    searchParams.set('page', newPage.toString());
    setSearchParams(searchParams);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Browse Recipes</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1">
          <RecipeFilters
            filters={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </aside>

        <main className="lg:col-span-3">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner size="lg" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">
              Error loading recipes. Please try again.
            </div>
          ) : data?.results?.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No recipes found. Try adjusting your filters.
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {data?.results?.map((recipe) => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>

              {/* Pagination */}
              {(data?.next || data?.previous) && (
                <div className="mt-8 flex justify-center gap-2">
                  <Button
                    variant="secondary"
                    disabled={!data?.previous}
                    onClick={() => handlePageChange(filters.page - 1)}
                  >
                    Previous
                  </Button>
                  <span className="px-4 py-2">Page {filters.page}</span>
                  <Button
                    variant="secondary"
                    disabled={!data?.next}
                    onClick={() => handlePageChange(filters.page + 1)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
```

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/RecipeListPage.jsx frontend/src/components/RecipeFilters.jsx frontend/src/hooks/useDebounce.js
git commit -m "feat(frontend): add recipe list page with filters"
```

---

### Task 5.7: Create Recipe Detail Page

**Files:**
- Create: `frontend/src/pages/RecipeDetailPage.jsx`
- Create: `frontend/src/components/IngredientList.jsx`
- Create: `frontend/src/components/CommentThread.jsx`

**Step 1: Create IngredientList.jsx**

```jsx
export function IngredientList({ ingredients }) {
  if (!ingredients?.length) {
    return <p className="text-gray-500">No ingredients listed.</p>;
  }

  return (
    <ul className="space-y-2">
      {ingredients.map((ing, index) => (
        <li key={index} className="flex items-start gap-2">
          <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
          <span>
            {ing.quantity && <strong>{ing.quantity}</strong>}{' '}
            {ing.unit && ing.unit !== 'to taste' && <span>{ing.unit}</span>}{' '}
            {ing.name}
            {ing.unit === 'to taste' && <span className="text-gray-500"> (to taste)</span>}
          </span>
        </li>
      ))}
    </ul>
  );
}
```

**Step 2: Create CommentThread.jsx**

```jsx
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useAddComment } from '../hooks/useRecipes';
import { Button, Input } from './ui';

function Comment({ comment, recipeId, onReply }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyText, setReplyText] = useState('');
  const { isAuthenticated } = useAuth();
  const addComment = useAddComment();

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyText.trim()) return;
    await addComment.mutateAsync({
      recipeId,
      text: replyText,
      parentId: comment.id,
    });
    setReplyText('');
    setShowReplyForm(false);
  };

  return (
    <div className="border-l-2 border-gray-200 pl-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium">
          {comment.user?.name?.[0]?.toUpperCase() || '?'}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{comment.user?.name || 'Anonymous'}</span>
            <span className="text-gray-400 text-sm">
              {new Date(comment.created_at).toLocaleDateString()}
            </span>
          </div>
          <p className="text-gray-700 mt-1">{comment.text}</p>
          {isAuthenticated && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-sm text-primary-600 mt-2 hover:text-primary-700"
            >
              Reply
            </button>
          )}
          {showReplyForm && (
            <form onSubmit={handleReply} className="mt-2 flex gap-2">
              <Input
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Write a reply..."
                className="flex-1"
              />
              <Button type="submit" size="sm" disabled={addComment.isPending}>
                Reply
              </Button>
            </form>
          )}
          {comment.replies?.map((reply) => (
            <div key={reply.id} className="mt-3">
              <Comment comment={reply} recipeId={recipeId} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CommentThread({ comments, recipeId }) {
  const [newComment, setNewComment] = useState('');
  const { isAuthenticated } = useAuth();
  const addComment = useAddComment();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    await addComment.mutateAsync({ recipeId, text: newComment });
    setNewComment('');
  };

  const topLevelComments = comments?.filter((c) => !c.parent) || [];

  return (
    <div className="space-y-6">
      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            className="flex-1"
          />
          <Button type="submit" disabled={addComment.isPending}>
            Post
          </Button>
        </form>
      )}

      {topLevelComments.length === 0 ? (
        <p className="text-gray-500 text-center py-4">
          No comments yet. {isAuthenticated ? 'Be the first to comment!' : 'Login to comment.'}
        </p>
      ) : (
        <div className="space-y-4">
          {topLevelComments.map((comment) => (
            <Comment key={comment.id} comment={comment} recipeId={recipeId} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 3: Create RecipeDetailPage.jsx**

```jsx
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useRecipe, useRecipeComments, useRateRecipe, useToggleFavorite, useDeleteRecipe } from '../hooks/useRecipes';
import { useAuth } from '../hooks/useAuth';
import { RatingStars } from '../components/RatingStars';
import { IngredientList } from '../components/IngredientList';
import { CommentThread } from '../components/CommentThread';
import { Button, Card, Spinner } from '../components/ui';
import { HeartIcon, ClockIcon, UserGroupIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { data: recipe, isLoading, error } = useRecipe(id);
  const { data: comments } = useRecipeComments(id);
  const rateRecipe = useRateRecipe();
  const toggleFavorite = useToggleFavorite();
  const deleteRecipe = useDeleteRecipe();
  const [showRatingForm, setShowRatingForm] = useState(false);

  const isOwner = user?.id === recipe?.author?.id;
  const totalTime = (recipe?.prep_time || 0) + (recipe?.cook_time || 0);

  const handleRate = async (score) => {
    await rateRecipe.mutateAsync({ id, score });
    setShowRatingForm(false);
  };

  const handleFavorite = async () => {
    await toggleFavorite.mutateAsync(id);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this recipe?')) {
      await deleteRecipe.mutateAsync(id);
      navigate('/my-recipes');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recipe Not Found</h2>
        <Link to="/recipes">
          <Button>Browse Recipes</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header Image */}
      {recipe.image && (
        <div className="aspect-video rounded-lg overflow-hidden mb-6">
          <img src={recipe.image} alt={recipe.title} className="w-full h-full object-cover" />
        </div>
      )}

      {/* Title and Actions */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{recipe.title}</h1>
          <p className="text-gray-600">by {recipe.author?.name || 'Unknown'}</p>
        </div>
        <div className="flex gap-2">
          {isAuthenticated && !isOwner && (
            <Button
              variant="ghost"
              onClick={handleFavorite}
              disabled={toggleFavorite.isPending}
            >
              {recipe.is_favorited ? (
                <HeartSolidIcon className="h-5 w-5 text-red-500" />
              ) : (
                <HeartIcon className="h-5 w-5" />
              )}
            </Button>
          )}
          {isOwner && (
            <>
              <Link to={`/recipes/${id}/edit`}>
                <Button variant="secondary">
                  <PencilIcon className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </Link>
              <Button variant="danger" onClick={handleDelete}>
                <TrashIcon className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="flex flex-wrap gap-6 mb-6">
        <div className="flex items-center gap-2">
          <RatingStars rating={recipe.average_rating || 0} count={recipe.rating_count} />
        </div>
        {totalTime > 0 && (
          <div className="flex items-center gap-2 text-gray-600">
            <ClockIcon className="h-5 w-5" />
            <span>{totalTime} min</span>
          </div>
        )}
        {recipe.servings && (
          <div className="flex items-center gap-2 text-gray-600">
            <UserGroupIcon className="h-5 w-5" />
            <span>{recipe.servings} servings</span>
          </div>
        )}
        {recipe.difficulty && (
          <span className="px-2 py-1 bg-gray-100 rounded text-sm capitalize">
            {recipe.difficulty}
          </span>
        )}
      </div>

      {/* Rate Button */}
      {isAuthenticated && !isOwner && (
        <div className="mb-6">
          {showRatingForm ? (
            <div className="flex items-center gap-4">
              <span>Your rating:</span>
              <RatingStars interactive onRate={handleRate} size="lg" />
              <Button variant="ghost" size="sm" onClick={() => setShowRatingForm(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button variant="secondary" onClick={() => setShowRatingForm(true)}>
              Rate this recipe
            </Button>
          )}
        </div>
      )}

      {/* Description */}
      {recipe.description && (
        <Card className="mb-6">
          <Card.Body>
            <p className="text-gray-700">{recipe.description}</p>
          </Card.Body>
        </Card>
      )}

      {/* Ingredients */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-xl font-semibold">Ingredients</h2>
        </Card.Header>
        <Card.Body>
          <IngredientList ingredients={recipe.ingredients} />
        </Card.Body>
      </Card>

      {/* Instructions */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-xl font-semibold">Instructions</h2>
        </Card.Header>
        <Card.Body>
          <div className="prose max-w-none whitespace-pre-wrap">
            {recipe.instructions}
          </div>
        </Card.Body>
      </Card>

      {/* Comments */}
      <Card>
        <Card.Header>
          <h2 className="text-xl font-semibold">
            Comments ({comments?.length || 0})
          </h2>
        </Card.Header>
        <Card.Body>
          <CommentThread comments={comments} recipeId={id} />
        </Card.Body>
      </Card>
    </div>
  );
}
```

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/RecipeDetailPage.jsx frontend/src/components/IngredientList.jsx frontend/src/components/CommentThread.jsx
git commit -m "feat(frontend): add recipe detail page with comments"
```

---

## Phase 6: Recipe Management Pages

### Task 6.1: Create Recipe Form Components

**Files:**
- Create: `frontend/src/features/recipes/IngredientForm.jsx`
- Create: `frontend/src/features/recipes/RecipeForm.jsx`

**Step 1: Create directories**

```bash
mkdir -p /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/features/recipes
```

**Step 2: Create IngredientForm.jsx**

```jsx
import { Button, Input } from '../../components/ui';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

const unitOptions = [
  { value: 'cups', label: 'Cups' },
  { value: 'tbsp', label: 'Tablespoons' },
  { value: 'tsp', label: 'Teaspoons' },
  { value: 'oz', label: 'Ounces' },
  { value: 'g', label: 'Grams' },
  { value: 'kg', label: 'Kilograms' },
  { value: 'ml', label: 'Milliliters' },
  { value: 'l', label: 'Liters' },
  { value: 'pieces', label: 'Pieces' },
  { value: 'pinch', label: 'Pinch' },
  { value: 'to taste', label: 'To Taste' },
];

export function IngredientForm({ ingredients, onChange }) {
  const handleAdd = () => {
    onChange([...ingredients, { name: '', quantity: '', unit: 'pieces' }]);
  };

  const handleRemove = (index) => {
    onChange(ingredients.filter((_, i) => i !== index));
  };

  const handleChange = (index, field, value) => {
    const updated = ingredients.map((ing, i) =>
      i === index ? { ...ing, [field]: value } : ing
    );
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      {ingredients.map((ing, index) => (
        <div key={index} className="flex gap-2 items-start">
          <div className="flex-1">
            <Input
              placeholder="Ingredient name"
              value={ing.name}
              onChange={(e) => handleChange(index, 'name', e.target.value)}
            />
          </div>
          <div className="w-24">
            <Input
              type="number"
              step="0.1"
              placeholder="Qty"
              value={ing.quantity}
              onChange={(e) => handleChange(index, 'quantity', e.target.value)}
            />
          </div>
          <div className="w-32">
            <select
              value={ing.unit}
              onChange={(e) => handleChange(index, 'unit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {unitOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <Button
            type="button"
            variant="ghost"
            onClick={() => handleRemove(index)}
            className="text-red-500"
          >
            <TrashIcon className="h-5 w-5" />
          </Button>
        </div>
      ))}
      <Button type="button" variant="secondary" onClick={handleAdd}>
        <PlusIcon className="h-4 w-4 mr-2" />
        Add Ingredient
      </Button>
    </div>
  );
}
```

**Step 3: Create RecipeForm.jsx**

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card } from '../../components/ui';
import { IngredientForm } from './IngredientForm';

const difficulties = [
  { value: '', label: 'Select difficulty' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

export function RecipeForm({ initialData, onSubmit, isSubmitting }) {
  const [ingredients, setIngredients] = useState(
    initialData?.ingredients || [{ name: '', quantity: '', unit: 'pieces' }]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      instructions: initialData?.instructions || '',
      prep_time: initialData?.prep_time || '',
      cook_time: initialData?.cook_time || '',
      servings: initialData?.servings || '',
      difficulty: initialData?.difficulty || '',
      is_published: initialData?.is_published ?? true,
    },
  });

  const handleFormSubmit = (data) => {
    const validIngredients = ingredients.filter((ing) => ing.name.trim());
    onSubmit({
      ...data,
      prep_time: data.prep_time ? parseInt(data.prep_time, 10) : null,
      cook_time: data.cook_time ? parseInt(data.cook_time, 10) : null,
      servings: data.servings ? parseInt(data.servings, 10) : null,
      ingredients: validIngredients.map((ing, index) => ({
        ...ing,
        quantity: ing.quantity ? parseFloat(ing.quantity) : null,
        order: index,
      })),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Basic Information</h2>
        </Card.Header>
        <Card.Body className="space-y-4">
          <Input
            label="Recipe Title"
            {...register('title', { required: 'Title is required' })}
            error={errors.title?.message}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Brief description of your recipe"
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Input
              label="Prep Time (min)"
              type="number"
              {...register('prep_time')}
            />
            <Input
              label="Cook Time (min)"
              type="number"
              {...register('cook_time')}
            />
            <Input
              label="Servings"
              type="number"
              {...register('servings')}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Difficulty
              </label>
              <select
                {...register('difficulty')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {difficulties.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Ingredients</h2>
        </Card.Header>
        <Card.Body>
          <IngredientForm ingredients={ingredients} onChange={setIngredients} />
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Instructions</h2>
        </Card.Header>
        <Card.Body>
          <textarea
            {...register('instructions', { required: 'Instructions are required' })}
            rows={10}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Step by step instructions..."
          />
          {errors.instructions && (
            <p className="mt-1 text-sm text-red-600">{errors.instructions.message}</p>
          )}
        </Card.Body>
      </Card>

      <Card>
        <Card.Body className="flex items-center justify-between">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              {...register('is_published')}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Publish recipe (visible to others)</span>
          </label>

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Recipe'}
          </Button>
        </Card.Body>
      </Card>
    </form>
  );
}
```

**Step 4: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/features/recipes/
git commit -m "feat(frontend): add recipe form components"
```

---

### Task 6.2: Create Recipe Pages

**Files:**
- Create: `frontend/src/pages/CreateRecipePage.jsx`
- Create: `frontend/src/pages/EditRecipePage.jsx`
- Create: `frontend/src/pages/MyRecipesPage.jsx`
- Create: `frontend/src/pages/FavoritesPage.jsx`

**Step 1: Create CreateRecipePage.jsx**

```jsx
import { useNavigate } from 'react-router-dom';
import { useCreateRecipe } from '../hooks/useRecipes';
import { RecipeForm } from '../features/recipes/RecipeForm';

export function CreateRecipePage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();

  const handleSubmit = async (data) => {
    try {
      const recipe = await createRecipe.mutateAsync(data);
      navigate(`/recipes/${recipe.id}`);
    } catch (error) {
      console.error('Failed to create recipe:', error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Create New Recipe</h1>
      <RecipeForm onSubmit={handleSubmit} isSubmitting={createRecipe.isPending} />
    </div>
  );
}
```

**Step 2: Create EditRecipePage.jsx**

```jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useUpdateRecipe } from '../hooks/useRecipes';
import { RecipeForm } from '../features/recipes/RecipeForm';
import { Spinner } from '../components/ui';

export function EditRecipePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: recipe, isLoading } = useRecipe(id);
  const updateRecipe = useUpdateRecipe();

  const handleSubmit = async (data) => {
    try {
      await updateRecipe.mutateAsync({ id, data });
      navigate(`/recipes/${id}`);
    } catch (error) {
      console.error('Failed to update recipe:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!recipe) {
    return <div className="text-center py-12">Recipe not found.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Edit Recipe</h1>
      <RecipeForm
        initialData={recipe}
        onSubmit={handleSubmit}
        isSubmitting={updateRecipe.isPending}
      />
    </div>
  );
}
```

**Step 3: Create MyRecipesPage.jsx**

```jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useRecipes } from '../hooks/useRecipes';
import { useAuth } from '../hooks/useAuth';
import { RecipeCard } from '../components/RecipeCard';
import { Button, Spinner } from '../components/ui';

export function MyRecipesPage() {
  const { user } = useAuth();
  const [showDrafts, setShowDrafts] = useState(false);

  const { data, isLoading } = useRecipes({
    author: user?.id,
  });

  const recipes = data?.results || [];
  const publishedRecipes = recipes.filter((r) => r.is_published);
  const draftRecipes = recipes.filter((r) => !r.is_published);
  const displayedRecipes = showDrafts ? draftRecipes : publishedRecipes;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">My Recipes</h1>
        <Link to="/recipes/new">
          <Button>Create Recipe</Button>
        </Link>
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setShowDrafts(false)}
          className={`px-4 py-2 rounded-md ${
            !showDrafts
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Published ({publishedRecipes.length})
        </button>
        <button
          onClick={() => setShowDrafts(true)}
          className={`px-4 py-2 rounded-md ${
            showDrafts
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Drafts ({draftRecipes.length})
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : displayedRecipes.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {showDrafts
            ? 'No draft recipes.'
            : 'No published recipes yet. Create your first recipe!'}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedRecipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 4: Create FavoritesPage.jsx**

```jsx
import { useRecipes } from '../hooks/useRecipes';
import { RecipeCard } from '../components/RecipeCard';
import { Spinner } from '../components/ui';

export function FavoritesPage() {
  // Note: Backend needs to support favorites filter - this assumes it does
  const { data, isLoading } = useRecipes({ favorited: true });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">My Favorites</h1>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : !data?.results?.length ? (
        <div className="text-center py-12 text-gray-500">
          No favorite recipes yet. Browse recipes and click the heart to save them!
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.results.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 5: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/
git commit -m "feat(frontend): add recipe management pages"
```

---

### Task 6.3: Create Profile Page

**Files:**
- Create: `frontend/src/pages/ProfilePage.jsx`
- Create: `frontend/src/components/ImageUpload.jsx`

**Step 1: Create ImageUpload.jsx**

```jsx
import { useCallback, useState } from 'react';
import { PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';

export function ImageUpload({ value, onChange, className = '' }) {
  const [preview, setPreview] = useState(value);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = useCallback(
    (file) => {
      if (file && file.type.startsWith('image/')) {
        onChange(file);
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result);
        reader.readAsDataURL(file);
      }
    },
    [onChange]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      handleFile(file);
    },
    [handleFile]
  );

  const handleChange = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  const handleRemove = () => {
    onChange(null);
    setPreview(null);
  };

  return (
    <div className={className}>
      {preview ? (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded-lg"
          />
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
          `}
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <PhotoIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">
              Drag and drop an image, or click to select
            </p>
            <p className="text-sm text-gray-400 mt-1">
              JPEG, PNG, WebP up to 5MB
            </p>
          </label>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Create ProfilePage.jsx**

```jsx
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { authApi } from '../api/auth';
import { Button, Input, Card, Spinner } from '../components/ui';
import { ImageUpload } from '../components/ImageUpload';

export function ProfilePage() {
  const { user, updateProfile, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    try {
      await updateProfile({ name, bio });
      setIsEditing(false);
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePhotoChange = async (file) => {
    if (!file) return;
    try {
      await authApi.updateProfilePhoto(file);
      await refreshUser();
    } catch (err) {
      setError('Failed to upload photo.');
    }
  };

  if (!user) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">My Profile</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <Card className="mb-6">
        <Card.Body className="flex items-center gap-6">
          <div className="relative">
            {user.profile_photo ? (
              <img
                src={user.profile_photo}
                alt={user.name}
                className="w-24 h-24 rounded-full object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-3xl font-bold">
                {user.name?.[0]?.toUpperCase() || '?'}
              </div>
            )}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold">{user.name}</h2>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-400 mt-1">
              Member since {new Date(user.date_joined).toLocaleDateString()}
            </p>
          </div>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Profile Details</h2>
          {!isEditing && (
            <Button variant="secondary" onClick={() => setIsEditing(true)}>
              Edit
            </Button>
          )}
        </Card.Header>
        <Card.Body>
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bio
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Tell us about yourself..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profile Photo
                </label>
                <ImageUpload
                  value={user.profile_photo}
                  onChange={handlePhotoChange}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsEditing(false);
                    setName(user.name || '');
                    setBio(user.bio || '');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <span className="text-sm text-gray-500">Name</span>
                <p>{user.name || 'Not set'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Bio</span>
                <p>{user.bio || 'No bio yet'}</p>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
```

**Step 3: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/pages/ProfilePage.jsx frontend/src/components/ImageUpload.jsx
git commit -m "feat(frontend): add profile page with image upload"
```

---

## Phase 7: App Setup and Routing

### Task 7.1: Create NotFoundPage and Set Up Routing

**Files:**
- Create: `frontend/src/pages/NotFoundPage.jsx`
- Modify: `frontend/src/App.jsx`

**Step 1: Create NotFoundPage.jsx**

```jsx
import { Link } from 'react-router-dom';
import { Button } from '../components/ui';

export function NotFoundPage() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
      <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
      <p className="text-gray-600 mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/">
        <Button>Go Home</Button>
      </Link>
    </div>
  );
}
```

**Step 2: Update App.jsx with full routing**

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './features/auth/AuthContext';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { MainLayout } from './layouts/MainLayout';
import { AuthLayout } from './layouts/AuthLayout';
import { HomePage } from './pages/HomePage';
import { RecipeListPage } from './pages/RecipeListPage';
import { RecipeDetailPage } from './pages/RecipeDetailPage';
import { CreateRecipePage } from './pages/CreateRecipePage';
import { EditRecipePage } from './pages/EditRecipePage';
import { MyRecipesPage } from './pages/MyRecipesPage';
import { FavoritesPage } from './pages/FavoritesPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { NotFoundPage } from './pages/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Auth routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Main routes */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/recipes" element={<RecipeListPage />} />
              <Route path="/recipes/:id" element={<RecipeDetailPage />} />

              {/* Protected routes */}
              <Route
                path="/recipes/new"
                element={
                  <ProtectedRoute>
                    <CreateRecipePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recipes/:id/edit"
                element={
                  <ProtectedRoute>
                    <EditRecipePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/my-recipes"
                element={
                  <ProtectedRoute>
                    <MyRecipesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/favorites"
                element={
                  <ProtectedRoute>
                    <FavoritesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

**Step 3: Remove Vite default files**

```bash
rm -f /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/App.css
rm -f /home/andrew/Documents/Python/Git/recipe_app_api/frontend/src/assets/react.svg
rm -rf /home/andrew/Documents/Python/Git/recipe_app_api/frontend/public/vite.svg
```

**Step 4: Test build**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api/frontend
npm run build
```
Expected: Build succeeds with no errors

**Step 5: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/
git commit -m "feat(frontend): complete app setup with routing"
```

---

## Phase 8: Final Integration

### Task 8.1: Add Utils and Final Polish

**Files:**
- Create: `frontend/src/utils/formatters.js`
- Create: `frontend/src/utils/validators.js`

**Step 1: Create formatters.js**

```javascript
export function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatTime(minutes) {
  if (!minutes) return '';
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export function truncate(text, length = 100) {
  if (!text || text.length <= length) return text;
  return text.slice(0, length) + '...';
}
```

**Step 2: Create validators.js**

```javascript
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidPassword(password) {
  return password && password.length >= 8;
}

export function isValidImageFile(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  return validTypes.includes(file.type) && file.size <= maxSize;
}
```

**Step 3: Commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add frontend/src/utils/
git commit -m "feat(frontend): add utility functions"
```

---

### Task 8.2: Test Complete Frontend

**Step 1: Start backend (if not running)**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
docker-compose up -d
```

**Step 2: Start frontend dev server**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api/frontend
npm run dev
```

**Step 3: Manual testing checklist**

- [ ] Home page loads with recipes
- [ ] Recipe list page with filters works
- [ ] Recipe detail page shows ingredients and comments
- [ ] Login works
- [ ] Register works
- [ ] Create recipe works (authenticated)
- [ ] Edit recipe works (owner only)
- [ ] Rating works
- [ ] Comments work
- [ ] Favorites toggle works
- [ ] Profile page loads and edits work
- [ ] Logout works
- [ ] Protected routes redirect to login

**Step 4: Build production version**

```bash
npm run build
```
Expected: Build succeeds

**Step 5: Final commit**

```bash
cd /home/andrew/Documents/Python/Git/recipe_app_api
git add .
git commit -m "feat(frontend): complete React frontend implementation"
```

---

Plan complete and saved to `docs/plans/2026-01-12-react-frontend-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Since you asked me to continue without questions, I'll proceed with **Subagent-Driven Development** in this session.
