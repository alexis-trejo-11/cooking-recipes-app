# Cooking Recipes API

REST API for a cooking-recipes platform: user accounts with JWT sessions, recipe CRUD, advanced search, favorites, reviews, and view analytics—built with Clean Architecture and deployable on AWS.

| Field | Value |
| --- | --- |
| Project ID | cooking-recipes-api |
| Version | 1.0.0 |
| Language | Python |
| Framework | FastAPI |
| Category | backend |
| Status | stable |
| Featured | Yes |
| Repository | https://github.com/your-org/cooking-recipes-app |
| Live demo | https://api.recipes.example.com/health |
| Created | 2025-01-01T00:00:00.000Z |
| Updated | 2026-06-01T00:00:00.000Z |

## Tech stack

- FastAPI 0.104
- Uvicorn
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- Redis (sessions)
- PyJWT + bcrypt
- Docker
- pytest + httpx

## Additional notes

# Project Metadata

> Portfolio metadata for the **Cooking Recipes API** backend (`recipe-back-end`). Replace `your-org` and `api.recipes.example.com` with your GitHub org and production Route 53 / ALB hostname.

> **AWS (as deployed):** Container image in **ECR**, service on **ECS Fargate** behind an **Application Load Balancer**, **RDS PostgreSQL** for persistence, **ElastiCache Redis** for refresh-token sessions, **Secrets Manager** for `JWT_SECRET_KEY`, **CloudWatch** for logs.

