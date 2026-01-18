# Development Guide

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn src.main:app --reload
```

API available at: http://localhost:8000
Swagger docs at: http://localhost:8000/docs

## Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Key variables:
- `SECRET_KEY`: Change this in production (min 32 characters)
- `ENVIRONMENT`: development | production | testing
- `DATABASE_URL`: SQLite by default, PostgreSQL for production

## Authentication Flow

Use Swagger UI at http://localhost:8000/docs:

1. **Create an API key:**
   - Open `POST /auth/keys`
   - Click "Try it out"
   - Enter: `{"name": "my-key"}`
   - Click "Execute"
   - Copy the `key` from the response (save it, shown only once)

2. **Get JWT token:**
   - Open `POST /auth/token`
   - Click "Try it out"
   - Enter: `{"api_key": "your-key-from-step-1"}`
   - Click "Execute"
   - Copy the `access_token` from the response

3. **Authorize Swagger:**
   - Click the "Authorize" button (top right)
   - Enter your token (without "Bearer" prefix)
   - Click "Authorize"

4. **Make predictions:**
   - Open `POST /predict`
   - Click "Try it out"
   - Enter house features
   - Click "Execute"

## Testing

### Test Structure

```
tests/
├── conftest.py           # Shared pytest config (markers only)
├── unit/
│   ├── conftest.py       # Lightweight fixtures
│   └── test_*.py         # Fast tests, no DB
└── integration/
    ├── conftest.py       # DB, client, auth fixtures
    └── test_*.py         # Full stack tests
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only (fast, ~6 seconds)
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# With coverage
pytest --cov=src --cov-report=html
```

### Test Isolation

- Unit tests: No database, no external dependencies
- Integration tests: In-memory SQLite, cleaned up after each test
- Rate limiter: Reset before each test automatically

## CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci.yml`) uses **fast-fail**:

```
lint → unit-tests → integration-tests → build → docker-tests
```

### Triggers

- **Push** to `main`, `master`, `develop`: Full pipeline
- **Pull Request** to `main`, `master`: Lint + tests + build (no push)

All checks run automatically when you create or update a PR.

### Stages

| Stage | Runs If | Purpose |
|-------|---------|---------|
| lint | Always | Ruff linting + formatting |
| unit-tests | lint passes | Fast feedback (~6s) |
| integration-tests | unit-tests pass | Full stack validation |
| coverage | tests pass | Coverage report (min 70%) |
| build | tests pass | Docker image build |
| docker-tests | push only | Tests inside container |
| security | push only | Trivy + pip-audit scans |

If any stage fails, subsequent stages are skipped.

### Running Locally

```bash
# Lint check
ruff check src/ tests/
ruff format --check src/ tests/

# Auto-fix
ruff check src/ tests/ --fix
ruff format src/ tests/
```

## Docker

### Development

```bash
# Start API
docker-compose up api

# Run all tests
docker-compose run --rm test

# Run unit tests only
docker-compose run --rm test-unit

# Run integration tests only
docker-compose run --rm test-integration

# Lint check
docker-compose run --rm lint
```

### Production Build

```bash
docker build --target production -t housing-api:latest .
docker run -p 8000:8000 -e SECRET_KEY=your-production-key housing-api:latest
```

## Project Structure

```
housing_prices_dashboard/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings
│   ├── constants.py         # Static values
│   ├── core/                # Shared utilities
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── security.py      # JWT, password hashing
│   │   ├── rate_limiter.py  # Slowapi config
│   │   └── logging.py       # Structured logging
│   ├── models/              # SQLAlchemy models
│   │   ├── api_key.py
│   │   ├── prediction_log.py
│   │   └── common.py        # Mixins, type annotations
│   ├── auth/                # Authentication domain
│   ├── predictions/         # ML predictions domain
│   ├── logs/                # Prediction logs domain
│   └── health/              # Health check endpoints
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/              # Alembic migrations
├── .github/workflows/       # CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View history
alembic history
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | No | Health check |
| GET | /health/detailed | No | Detailed health with model status |
| POST | /auth/keys | No | Create API key |
| POST | /auth/token | No | Exchange API key for JWT |
| POST | /predict | Yes | Single prediction |
| POST | /predict/batch | Yes | Batch predictions (max 100) |
| GET | /logs | Yes | List prediction logs |
| GET | /logs/{id} | Yes | Get specific log |

## Rate Limiting

- Default: 100 requests/minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` env var
- Returns 429 when exceeded
