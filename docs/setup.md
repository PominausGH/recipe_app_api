# Development Setup

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for frontend)
- Git

## Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/PominausGH/recipe_app_api.git
   cd recipe_app_api
   ```

2. **Start services**
   ```bash
   docker compose up
   ```
   This starts the Django API (port 8000) and PostgreSQL database.

3. **Create a superuser** (optional, for admin access)
   ```bash
   docker compose run --rm app sh -c "python manage.py createsuperuser"
   ```

4. **Verify it's working**
   - API: http://localhost:8000/api/
   - Swagger docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

## Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start dev server**
   ```bash
   npm run dev
   ```
   Frontend runs at http://localhost:5173

## Pre-commit Hooks

Install pre-commit hooks for code quality:
```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on commit: isort, Black, flake8, mypy.

## Running Tests

```bash
# Backend tests
docker compose run --rm app sh -c "python manage.py test"

# Frontend unit tests
cd frontend && npm run test:run

# Frontend E2E tests
cd frontend && npm run test:e2e
```
