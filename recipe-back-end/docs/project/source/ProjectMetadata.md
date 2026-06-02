---
projectId: "cooking-recipes-api"
featured: true
name: "Cooking Recipes API"
language: "Python"
category: "backend"
framework: "FastAPI"
version: "1.0.0"
repositoryUrl: "https://github.com/your-org/cooking-recipes-app"
liveDemoUrl: "https://api.recipes.example.com/health"
description: "REST API for a cooking-recipes platform: user accounts with JWT sessions, recipe CRUD, advanced search, favorites, reviews, and view analytics—built with Clean Architecture and deployable on AWS."
techStack:
  - "FastAPI 0.104"
  - "Uvicorn"
  - "SQLAlchemy 2.0 (async)"
  - "Alembic"
  - "Pydantic v2"
  - "Redis (sessions)"
  - "PyJWT + bcrypt"
  - "Docker"
  - "pytest + httpx"
status: "stable"
createdAt: "2025-01-01T00:00:00.000Z"
updatedAt: "2026-06-01T00:00:00.000Z"
---

# Project Metadata

> Portfolio metadata for the **Cooking Recipes API** backend (`recipe-back-end`). Replace `your-org` and `api.recipes.example.com` with your GitHub org and production Route 53 / ALB hostname.

> **AWS (as deployed):** Container image in **ECR**, service on **ECS Fargate** behind an **Application Load Balancer**, **RDS PostgreSQL** for persistence, **ElastiCache Redis** for refresh-token sessions, **Secrets Manager** for `JWT_SECRET_KEY`, **CloudWatch** for logs.
