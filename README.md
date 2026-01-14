# Recipe App API

A full-stack recipe sharing platform with social features.

## Features

- **Recipes**: Create, browse, and manage recipes with images
- **Social**: Follow users, rate recipes, leave comments
- **Feed**: Personalized activity feed from followed users
- **Auth**: JWT-based authentication

## Tech Stack

- **Backend**: Django REST Framework, PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Infrastructure**: Docker, GitHub Actions CI/CD

## Quick Start

```bash
# Clone and start backend
docker compose up

# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/api/docs/
```

```bash
# Start frontend (separate terminal)
cd frontend && npm install && npm run dev

# Frontend runs at http://localhost:5173
```

## Documentation

- [Development Setup](docs/setup.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Contributing](docs/contributing.md)

## License

MIT
