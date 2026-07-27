# Project Overview

## Scattered recipe data and weak discovery

Home cooks and food bloggers need one backend to publish structured recipes (ingredients, steps, nutrition), let users search and filter by cuisine or diet, save favorites, and leave ratings—without coupling the UI to SQLite files or ad-hoc JSON.

### Pain points

- Recipe content lives in spreadsheets or static JSON with no auth or ownership
- Search cannot combine filters (cuisine, meal type, cooking time, rating) efficiently
- No session model for multi-device login and secure logout
- Favorites and reviews duplicated across clients with no single source of truth
- No production path from local SQLite to managed PostgreSQL on AWS

## A FastAPI backend with DDD modules

- **Auth module with JWT + Redis sessions** — Signup/login, refresh tokens stored in Redis, logout with optional revoke-all-devices; bcrypt password hashing.
- **Recipe module with use cases** — Create/update/soft-delete recipes, specification-based search, featured list, view counter, favorites toggle, and reviews.
- **Clean Architecture boundaries** — Domain entities and repository interfaces; application use cases; SQLAlchemy and Redis in infrastructure; FastAPI controllers in presentation.
- **Operational readiness** — Docker image, health checks, Alembic migrations via start.sh, rate limiting, CORS for Angular frontend on :4200.
- **AWS-ready deploy** — Documented path to ECS + RDS + ElastiCache; local docker-compose bundles Redis; production uses external managed services.

## Platform snapshot

- 2 bounded contexts: auth, recipe (~94 Python modules under app/)
- REST API v1 under /api/v1/auth, /api/v1/users, /api/v1/recipes
- 15+ recipe endpoints (CRUD, search, favorites, reviews, featured)
- 5 auth endpoints live + 2 session endpoints stubbed (hidden from OpenAPI)
- Interactive docs at /docs and /redoc (FastAPI auto-generated)

## Links

| Resource | URL |
| --- | --- |
| Github | https://github.com/your-org/cooking-recipes-app |
| Demo | https://api.recipes.example.com/health |
| Documentation | https://api.recipes.example.com/docs |
| Dockerhub | None |

## Cooking Recipes API — product views

Replace placeholder URLs with screenshots from Swagger UI, Angular app, or architecture diagrams after deploy.

### API cover

Cooking Recipes REST API for discovery and user-generated content

- **Type:** image | **Category:** screenshot
- ![Cooking Recipes API branding placeholder](https://placehold.co/1200x630/E65100/ffffff?text=Cooking+Recipes+API)

### OpenAPI (Swagger UI)

FastAPI auto-generated schema at /docs on production ALB

- **Type:** image | **Category:** demo
- ![Swagger UI placeholder](https://placehold.co/1200x800/1565C0/ffffff?text=FastAPI+Swagger)

## Additional media

### Layered architecture

Presentation → Application → Domain → Infrastructure

### AWS deployment

ECS Fargate, ALB, RDS PostgreSQL, ElastiCache Redis

## Metrics

| Label | Value | Description |
| --- | --- | --- |
| API modules | 2 | auth, recipe |
| API version | v1 | Prefix /api/v1/ |
| Python runtime | 3.11 | Dockerfile python:3.11-slim |
| Access token TTL | 30 min | JWT_ACCESS_TOKEN_EXPIRES_MINUTES in settings |

## Additional notes

# Overview

> **Audience:** Developers building a cooking-recipes web or mobile app (e.g. Angular frontend on port 4200) and operators deploying to AWS.

> **Good:** Specification pattern composes SQL filters for recipe search; soft-delete with restore; view count on GET recipe.

> **Warnings:** Dockerfile copies `.env` and TLS certs into the image—use ECS task secrets and ACM at the load balancer in real production. Default local DB is SQLite (`cooking_app.db`); migrate `DATABASE_URL` to `postgresql+asyncpg://...` for RDS. In-memory rate limits are per-container; use Redis-backed limits or WAF rules when scaling ECS tasks. `include_in_schema=False` session list/revoke endpoints are stubs only.

