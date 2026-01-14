# API Reference

## Interactive Documentation

Full API documentation is auto-generated and available at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Tokens). Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Create new account |
| POST | `/api/auth/login/` | Get access + refresh tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Invalidate token |
| GET | `/api/auth/me/` | Get current user profile |

## Main Endpoints

| Resource | Endpoint | Description |
|----------|----------|-------------|
| Recipes | `/api/recipes/` | CRUD operations, filtering, search |
| Users | `/api/users/` | Follow, block, mute, search users |
| Notifications | `/api/notifications/` | User notifications |
| Feed | `/api/feed/` | Activity feed from followed users |

## Recipe Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recipes/{id}/rate/` | Rate a recipe (1-5) |
| POST | `/api/recipes/{id}/favorite/` | Toggle favorite |
| GET/POST | `/api/recipes/{id}/comments/` | List/create comments |
