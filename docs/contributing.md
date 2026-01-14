# Contributing

## Code Style

This project uses automated tools to enforce consistent code style:

| Tool | Purpose |
|------|---------|
| **isort** | Sort imports |
| **Black** | Code formatting (88 char line length) |
| **flake8** | Linting |
| **mypy** | Type checking |

Pre-commit hooks run these automatically. Install with:
```bash
pip install pre-commit
pre-commit install
```

## Git Workflow

1. Create a feature branch
   ```bash
   git checkout -b feat/your-feature
   ```

2. Make changes and commit
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. Push and create PR
   ```bash
   git push -u origin feat/your-feature
   ```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

Types: feat, fix, refactor, docs, test, chore
```

Examples:
- `feat(recipe): add image upload`
- `fix(auth): handle expired tokens`
- `docs: update setup guide`

## Running CI Locally

```bash
# Backend tests + linting
docker compose run --rm app sh -c "python manage.py test && flake8"

# Frontend
cd frontend && npm run typecheck && npm run test:run && npm run lint
```

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Code follows existing patterns
- [ ] PR description explains the change
