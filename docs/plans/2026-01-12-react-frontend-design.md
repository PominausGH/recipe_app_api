# React Frontend Design for Recipe Sharing Platform

## Overview

A modern React single-page application (SPA) that provides a user-friendly interface for the Recipe Sharing Platform API. Replaces the default DRF browsable API with a polished, responsive web application.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **TanStack Query (React Query)** - Server state management
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first styling
- **React Hook Form** - Form handling
- **Headless UI** - Accessible UI primitives

## Architecture

### Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.example
├── public/
│   └── favicon.ico
└── src/
    ├── main.jsx              # App entry point
    ├── App.jsx               # Root component with providers
    ├── api/
    │   ├── client.js         # Axios instance with interceptors
    │   ├── auth.js           # Auth API functions
    │   └── recipes.js        # Recipe API functions
    ├── components/
    │   ├── ui/               # Base UI components
    │   │   ├── Button.jsx
    │   │   ├── Input.jsx
    │   │   ├── Card.jsx
    │   │   ├── Modal.jsx
    │   │   └── Spinner.jsx
    │   ├── RecipeCard.jsx
    │   ├── RecipeFilters.jsx
    │   ├── RatingStars.jsx
    │   ├── CommentThread.jsx
    │   ├── IngredientList.jsx
    │   ├── ImageUpload.jsx
    │   └── Navbar.jsx
    ├── features/
    │   ├── auth/
    │   │   ├── AuthContext.jsx
    │   │   ├── LoginForm.jsx
    │   │   ├── RegisterForm.jsx
    │   │   └── ProtectedRoute.jsx
    │   └── recipes/
    │       ├── RecipeForm.jsx
    │       └── IngredientForm.jsx
    ├── hooks/
    │   ├── useAuth.js
    │   ├── useRecipes.js
    │   └── useDebounce.js
    ├── layouts/
    │   ├── MainLayout.jsx
    │   └── AuthLayout.jsx
    ├── pages/
    │   ├── HomePage.jsx
    │   ├── RecipeListPage.jsx
    │   ├── RecipeDetailPage.jsx
    │   ├── CreateRecipePage.jsx
    │   ├── EditRecipePage.jsx
    │   ├── MyRecipesPage.jsx
    │   ├── FavoritesPage.jsx
    │   ├── ProfilePage.jsx
    │   ├── LoginPage.jsx
    │   ├── RegisterPage.jsx
    │   └── NotFoundPage.jsx
    └── utils/
        ├── formatters.js
        └── validators.js
```

### Data Flow

```
User Action → React Query Mutation → API Call → Cache Update → UI Re-render
                                         ↓
                                   Optimistic Update (for better UX)
```

## Authentication

### JWT Token Management

1. **Login flow:**
   - POST to `/api/auth/login/` with credentials
   - Receive `access` and `refresh` tokens
   - Store access token in memory (React state)
   - Store refresh token in localStorage

2. **Request flow:**
   - Axios interceptor attaches `Authorization: Bearer <access_token>`
   - On 401 response, attempt token refresh
   - If refresh succeeds, retry original request
   - If refresh fails, redirect to login

3. **Logout flow:**
   - POST to `/api/auth/logout/` with refresh token
   - Clear all stored tokens
   - Reset auth state
   - Redirect to home

### Auth Context API

```javascript
const AuthContext = {
  user: User | null,
  isAuthenticated: boolean,
  isLoading: boolean,
  login: (email, password) => Promise<void>,
  register: (email, name, password) => Promise<void>,
  logout: () => Promise<void>,
  updateProfile: (data) => Promise<void>,
}
```

## Pages

### Public Pages

1. **Home (`/`)**
   - Hero section with search
   - Featured recipes (highest rated)
   - Recent recipes
   - Category quick links

2. **Recipe Browse (`/recipes`)**
   - Recipe grid with cards
   - Filter sidebar (category, difficulty, tags, max time)
   - Search input
   - Sort dropdown (newest, rating, cook time)
   - Pagination

3. **Recipe Detail (`/recipes/:id`)**
   - Recipe image (full width on mobile)
   - Title, author, stats (rating, time, servings)
   - Description
   - Ingredients list with quantities
   - Step-by-step instructions
   - Rating input (if authenticated)
   - Comments section with replies
   - Favorite button (if authenticated)

4. **Login (`/login`)** - Email/password form
5. **Register (`/register`)** - Registration form with validation

### Protected Pages

1. **Create Recipe (`/recipes/new`)**
   - Multi-section form
   - Dynamic ingredient list (add/remove/reorder)
   - Image upload with preview
   - Draft/Publish toggle

2. **Edit Recipe (`/recipes/:id/edit`)**
   - Same as create, pre-populated
   - Only accessible by recipe owner

3. **My Recipes (`/my-recipes`)**
   - Tab view: Published / Drafts
   - Recipe cards with edit/delete actions

4. **Favorites (`/favorites`)**
   - Grid of favorited recipes
   - Unfavorite action

5. **Profile (`/profile`)**
   - View/edit mode toggle
   - Profile photo upload
   - Bio editor
   - Account stats

## Components

### RecipeCard
Displays recipe thumbnail in grid layouts.
- Image with fallback
- Title (truncated)
- Author name
- Average rating (stars)
- Total time
- Difficulty badge

### RecipeFilters
Filter controls for recipe list.
- Category dropdown
- Difficulty checkboxes
- Tag multi-select
- Max time slider
- Clear filters button

### RatingStars
Interactive star rating component.
- Display mode: Shows filled/empty stars
- Input mode: Hover preview, click to rate
- Shows rating count

### CommentThread
Nested comment display.
- Comment text with author and timestamp
- Reply button (if authenticated)
- Nested replies (indented)
- Load more for long threads

### ImageUpload
Drag-and-drop image uploader.
- Drag zone with visual feedback
- Click to select file
- Image preview
- Remove/replace action
- Size/type validation

## API Integration

### Query Keys

```javascript
const queryKeys = {
  recipes: {
    all: ['recipes'],
    list: (filters) => ['recipes', 'list', filters],
    detail: (id) => ['recipes', 'detail', id],
    comments: (id) => ['recipes', id, 'comments'],
  },
  user: {
    me: ['user', 'me'],
    recipes: ['user', 'recipes'],
    favorites: ['user', 'favorites'],
  },
}
```

### API Functions

```javascript
// Auth
authApi.login(email, password)
authApi.register(email, name, password)
authApi.logout(refreshToken)
authApi.getMe()
authApi.updateMe(data)

// Recipes
recipesApi.list(filters)
recipesApi.get(id)
recipesApi.create(data)
recipesApi.update(id, data)
recipesApi.delete(id)
recipesApi.uploadImage(id, file)
recipesApi.rate(id, score, review)
recipesApi.toggleFavorite(id)
recipesApi.getComments(id)
recipesApi.addComment(id, text, parentId)
```

## Styling

### Design Tokens

```javascript
// tailwind.config.js
colors: {
  primary: {
    50: '#fef3e2',
    500: '#f59e0b',  // Warm amber for food theme
    600: '#d97706',
    700: '#b45309',
  },
  // ... standard Tailwind palette
}
```

### Layout Breakpoints

- Mobile: < 640px (single column)
- Tablet: 640px - 1024px (2-column grid)
- Desktop: > 1024px (3-4 column grid)

### Component Styling

All components use Tailwind utility classes with consistent patterns:
- Cards: `rounded-lg shadow-md bg-white`
- Buttons: `px-4 py-2 rounded-md font-medium`
- Inputs: `border border-gray-300 rounded-md px-3 py-2`

## Error Handling

### API Errors
- Network errors: Toast notification + retry button
- 401 Unauthorized: Redirect to login (after refresh attempt)
- 403 Forbidden: "Permission denied" message
- 404 Not Found: Not found page
- 400 Bad Request: Display validation errors inline
- 500 Server Error: Generic error message

### Form Validation
- Client-side validation with React Hook Form
- Server-side errors mapped to form fields
- Real-time validation feedback

## Performance

### Optimizations
- React Query caching (5-10 min stale time)
- Image lazy loading
- Route-based code splitting
- Optimistic updates for mutations
- Debounced search input

### Bundle Size
Target: < 200KB gzipped initial load
- Tree-shaking enabled
- Dynamic imports for heavy components

## Testing Strategy

- Unit tests: Vitest for utility functions
- Component tests: React Testing Library
- E2E tests: Optional (Playwright/Cypress)
- API mocking: MSW (Mock Service Worker)

## Environment Variables

```
VITE_API_URL=http://localhost:8000/api
```

## Development Workflow

```bash
# Install dependencies
npm install

# Start dev server (with API proxy)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

Build outputs static files to `dist/` directory. Can be served by:
- Nginx (recommended for production)
- Django static files (for simple setups)
- Any static hosting (Vercel, Netlify)
