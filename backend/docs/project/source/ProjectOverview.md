---
problemStatement:
  problemTitle: "Scattered recipe data and weak discovery"
  problemDescription: "Home cooks and food bloggers need one backend to publish structured recipes (ingredients, steps, nutrition), let users search and filter by cuisine or diet, save favorites, and leave ratings—without coupling the UI to SQLite files or ad-hoc JSON."
  problemList:
    - "Recipe content lives in spreadsheets or static JSON with no auth or ownership"
    - "Search cannot combine filters (cuisine, meal type, cooking time, rating) efficiently"
    - "No session model for multi-device login and secure logout"
    - "Favorites and reviews duplicated across clients with no single source of truth"
    - "No production path from local SQLite to managed PostgreSQL on AWS"

solution:
  solutionTitle: "A FastAPI backend with DDD modules"
  solutionList:
    - title: "Auth module with JWT + Redis sessions"
      description: "Signup/login, refresh tokens stored in Redis, logout with optional revoke-all-devices; bcrypt password hashing."
    - title: "Recipe module with use cases"
      description: "Create/update/soft-delete recipes, specification-based search, featured list, view counter, favorites toggle, and reviews."
    - title: "Clean Architecture boundaries"
      description: "Domain entities and repository interfaces; application use cases; SQLAlchemy and Redis in infrastructure; FastAPI controllers in presentation."
    - title: "Operational readiness"
      description: "Docker image, health checks, Alembic migrations via start.sh, rate limiting, CORS for Angular frontend on :4200."
    - title: "AWS-ready deploy"
      description: "Documented path to ECS + RDS + ElastiCache; local docker-compose bundles Redis; production uses external managed services."

keyMetrics:
  metricsTitle: "Platform snapshot"
  metricsList:
    - "2 bounded contexts: auth, recipe (~94 Python modules under app/)"
    - "REST API v1 under /api/v1/auth, /api/v1/users, /api/v1/recipes"
    - "15+ recipe endpoints (CRUD, search, favorites, reviews, featured)"
    - "5 auth endpoints live + 2 session endpoints stubbed (hidden from OpenAPI)"
    - "Interactive docs at /docs and /redoc (FastAPI auto-generated)"

links:
  github: "https://github.com/your-org/cooking-recipes-app"
  demo: "https://api.recipes.example.com/health"
  documentation: "https://api.recipes.example.com/docs"
  dockerHub: null

mediaGallery:
  title: "Cooking Recipes API — product views"
  description: "Replace placeholder URLs with screenshots from Swagger UI, Angular app, or architecture diagrams after deploy."
  items:
    - type: "image"
      url: "https://placehold.co/1200x630/E65100/ffffff?text=Cooking+Recipes+API"
      thumbnail: "https://placehold.co/400x210/E65100/ffffff?text=Recipes+API"
      title: "API cover"
      description: "Cooking Recipes REST API for discovery and user-generated content"
      alt: "Cooking Recipes API branding placeholder"
      category: "screenshot"
    - type: "image"
      url: "https://placehold.co/1200x800/1565C0/ffffff?text=FastAPI+Swagger"
      thumbnail: "https://placehold.co/400x267/1565C0/ffffff?text=Swagger"
      title: "OpenAPI (Swagger UI)"
      description: "FastAPI auto-generated schema at /docs on production ALB"
      alt: "Swagger UI placeholder"
      category: "demo"

mediaItems:
  - type: "image"
    url: "https://placehold.co/800x500/2E7D32/ffffff?text=Clean+Architecture"
    thumbnail: "https://placehold.co/320x200/2E7D32/ffffff?text=Layers"
    title: "Layered architecture"
    description: "Presentation → Application → Domain → Infrastructure"
    alt: "Clean architecture layers placeholder"
    category: "architecture"
  - type: "image"
    url: "https://placehold.co/800x500/37474F/ffffff?text=AWS+ECS+RDS"
    thumbnail: "https://placehold.co/320x200/37474F/ffffff?text=AWS"
    title: "AWS deployment"
    description: "ECS Fargate, ALB, RDS PostgreSQL, ElastiCache Redis"
    alt: "AWS deployment diagram placeholder"
    category: "diagram"

metrics:
  - label: "API modules"
    value: "2"
    description: "auth, recipe"
  - label: "API version"
    value: "v1"
    description: "Prefix /api/v1/"
  - label: "Python runtime"
    value: "3.11"
    description: "Dockerfile python:3.11-slim"
  - label: "Access token TTL"
    value: "30 min"
    description: "JWT_ACCESS_TOKEN_EXPIRES_MINUTES in settings"
---

# Overview

> **Audience:** Developers building a cooking-recipes web or mobile app (e.g. Angular frontend on port 4200) and operators deploying to AWS.

> **Good:** Specification pattern composes SQL filters for recipe search; soft-delete with restore; view count on GET recipe.

> **Warnings:** Dockerfile copies `.env` and TLS certs into the image—use ECS task secrets and ACM at the load balancer in real production. Default local DB is SQLite (`cooking_app.db`); migrate `DATABASE_URL` to `postgresql+asyncpg://...` for RDS. In-memory rate limits are per-container; use Redis-backed limits or WAF rules when scaling ECS tasks. `include_in_schema=False` session list/revoke endpoints are stubs only.
