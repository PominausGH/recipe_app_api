# Architecture

## Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   Django    │────▶│ PostgreSQL  │
│  Frontend   │     │  REST API   │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
     :5173              :8000
```

## Backend Structure

```
app/
├── app/              # Project settings, URLs
│   └── settings/     # Environment-specific settings
├── core/             # Auth, user model, utilities
├── recipe/           # Recipe CRUD, images, filtering
├── interaction/      # Social features (follows, ratings, comments)
└── taxonomy/         # Categories and tags
```

## Django Apps

| App | Purpose |
|-----|---------|
| **core** | Custom user model, JWT auth, profile management |
| **recipe** | Recipe model, images, search/filtering |
| **interaction** | Follows, blocks, ratings, comments, notifications, feed |
| **taxonomy** | Categories and tags for recipes |

## Key Design Decisions

- **Custom User Model**: Email-based auth instead of username
- **JWT Authentication**: Stateless auth via SimpleJWT
- **Nested Actions**: Recipe interactions (rate, favorite, comment) as ViewSet actions
- **Feed Service**: Aggregates activity from followed users

## Frontend Structure

```
frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── pages/        # Route pages
│   ├── contexts/     # React contexts (auth, etc.)
│   ├── services/     # API client
│   └── types/        # TypeScript types
└── e2e/              # Playwright E2E tests
```
