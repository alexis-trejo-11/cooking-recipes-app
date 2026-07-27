# Architecture

## Presentation (clients)

Angular SPA and future mobile clients consuming JSON over HTTPS.

### Components

- Angular dev server (:4200)
- Production SPA (S3 + CloudFront placeholder)

### Responsibilities

- Bearer JWT on protected routes
- Recipe search UI and favorites

### Technologies

- HTTPS
- REST JSON
- OpenAPI client (optional)

## Edge & API gateway

TLS termination and routing to FastAPI on ECS.

### Components

- AWS Application Load Balancer
- ACM certificate
- CORS (Angular origins in main.py)

### Responsibilities

- HTTPS only in production
- Health checks to /health

### Technologies

- ALB
- ACM

## Application (FastAPI)

Uvicorn serves FastAPI app with global rate limit dependency and exception handlers.

### Components

- main.py — lifespan, CORS, routers
- auth — controllers, use cases, JWT middleware handlers
- recipe — controller, DTOs, use cases
- config — settings, redis, sql_session, rate_limiter

### Responsibilities

- Map HTTP to use case execute()
- Pydantic validation on requests/responses
- No business rules in controllers

### Technologies

- FastAPI
- Pydantic v2
- Uvicorn

## Domain

Entities, value objects, repository interfaces, domain exceptions.

### Components

- User, Session (auth)
- Recipe, Ingredient, Review (recipe)
- Specification criteria for search

### Responsibilities

- Invariants and enums (DifficultyLevel, CuisineType, MealType)
- Framework-agnostic rules

### Technologies

- Pure Python

## Infrastructure

SQLAlchemy async repositories, Redis session store, JWT and bcrypt services.

### Components

- SQLAlchemy models + Alembic
- RecipeSpecificationBuilder → SQL
- RedisUserSessionRepository
- JwtTokenService, BcryptPasswordHasher

### Responsibilities

- Persistence and external I/O
- Implement domain interfaces

### Technologies

- SQLAlchemy 2.0
- aiosqlite / asyncpg (RDS)
- Redis

## Design patterns

| Pattern | Category | Description |
| --- | --- | --- |
| 🏛️ Clean Architecture | Structural | Dependencies point inward: presentation → application → domain; infrastructure implements domain ports. |
| ⚙️ Use case (application service) | Behavioral | One class per operation (CreateRecipeUseCase, SearchRecipesUseCase) orchestrates domain and repositories. |
| 🔍 Specification | Data | Composable RecipeByNameSpecification, AndSpecification, etc. translated to SQL via specification_builder. |
| 🗄️ Repository | Data | IRecipeRepository, IUserRepository abstract persistence; SQLAlchemy implementations in infrastructure. |
| 💉 Dependency injection | Creational | FastAPI Depends() wires use cases and repositories per request in presentation/dependencies.py. |
| 🗑️ Soft delete | Domain | Recipes marked deleted remain in DB; restore endpoint reverses flag; search excludes deleted by default. |

## Scalability strategies

- **Horizontally scale ECS tasks** — Stateless API containers behind ALB; session state in ElastiCache Redis, not in process memory.
- **RDS PostgreSQL** — Move from SQLite to RDS with connection pool (DB_POOL_SIZE) for production traffic.
- **Read-heavy recipe search** — Specification-built queries with pagination; add DB indexes on name, author_id, rating per DATABASE_SCHEMA.md.
- **Optional CDN for static media** — Profile pictures and recipe images can later use S3 + CloudFront (profile_picture_url field ready).

## Security strategies

- **JWT access + refresh** — Short-lived access token (30 min); refresh validated against Redis session store.
- **bcrypt passwords** — BcryptPasswordHasher in infrastructure; strong password rules on signup DTO.
- **Author-only mutations** — Update/delete recipe and reviews require authenticated author checks in use cases.
- **Rate limiting** — Per-IP sliding window: strict (auth), sensitive (writes), public (browse), generous (profile).
- **Secrets in AWS** — JWT_SECRET_KEY from Secrets Manager in ECS task definition—not baked in Docker image for prod.

## Cache strategies

| Name | TTL | Coverage | Description |
| --- | --- | --- | --- |
| Redis session store | Refresh token lifetime (90 days configurable) | Auth logout and refresh flows | Refresh tokens and session metadata keyed with REDIS_SESSION_PREFIX |
| In-process rate limit counters | 60s sliding window per profile | All routed endpoints via global Depends | RateLimitManager defaultdict per endpoint:IP in app memory |
| Future: Redis rate limits | N/A | Placeholder for shared limiter across replicas | Documented in DEPLOYMENT.md for multi-task ECS fairness |

## Architecture highlights

### 📖 Auto OpenAPI

FastAPI generates /docs and /redoc from Pydantic models and route metadata.

### 🛡️ Global exception handling

GlobalExceptionHandler maps domain errors to consistent HTTP responses.

### 🔄 Lifespan hooks

init_db, initialize_redis on startup; graceful close on shutdown.

### 📊 View analytics

GET /recipes/{id} increments view count via IncrementViewCountUseCase.

## Architecture diagram

### Legend

| Type | Label |
| --- | --- |
| client | Client |
| gateway | ALB |
| service | API |
| database | Database |
| queue | Redis |
| monitoring | Monitoring |

### Nodes

| ID | Label | Type | Status |
| --- | --- | --- | --- |
| angular-app | Angular SPA | client | healthy |
| alb | ALB (HTTPS) | gateway | healthy |
| ecs-api | ECS Fargate — FastAPI | service | healthy |
| rds | RDS PostgreSQL | database | healthy |
| redis | ElastiCache Redis | queue | healthy |
| cloudwatch | CloudWatch Logs | monitoring | healthy |
| ecr | ECR image | service | healthy |

### Connections

| From | To | Label | Protocol |
| --- | --- | --- | --- |
| angular-app | alb | HTTPS | TLS 1.2+ |
| alb | ecs-api | Forward | HTTP |
| ecs-api | rds | async SQL | PostgreSQL |
| ecs-api | redis | Sessions | Redis |
| ecs-api | cloudwatch | Logs | awslogs |

### Mermaid overview

```mermaid
flowchart LR
    angular-app([Angular SPA])
    alb{ALB (HTTPS)}
    ecs-api[ECS Fargate — FastAPI]
    rds[(RDS PostgreSQL)]
    redis[/ElastiCache Redis/]
    cloudwatch>CloudWatch Logs]
    ecr[ECR image]
    angular-app -->|HTTPS| alb
    alb -->|Forward| ecs-api
    ecs-api -->|async SQL| rds
    ecs-api -->|Sessions| redis
    ecs-api -->|Logs| cloudwatch
```

## Data flow

### Request flow

1. **HTTP request** — Client calls /api/v1/... with optional Authorization Bearer token.
2. **Rate limit & auth** — Global rate_limiter_dependency runs; get_current_user decodes JWT for protected routes.
3. **Use case** — Controller invokes use case execute() with DTOs and domain IDs.
4. **Repository / spec** — Infrastructure runs SQLAlchemy query from specification or loads entity by ID.
5. **JSON response** — Pydantic response_model serializes result to client.

### Event flow

1. **Recipe viewed** — GET /recipes/{id} triggers IncrementViewCountUseCase before returning payload.
2. **Review submitted** — CreateReviewUseCase updates aggregate rating on recipe.
3. **Session created** — Login/signup stores refresh token metadata in Redis via RedisUserSessionRepository.
4. **Logout** — Logout use case deletes session key(s) from Redis; optional logout_all revokes all devices.

## Additional notes

# Architecture

> **Deployed view:** Clients hit `https://api.recipes.example.com` → ALB → ECS tasks running this repo’s Docker image; data in RDS, sessions in ElastiCache.

> **Local view:** `uvicorn` or `docker compose up` on ports 8080/8443 with SQLite file and Redis container.

> **Tech debt:** Rate limits are in-memory per task—scale ECS to 2+ tasks without Redis rate limiter and limits diverge per instance. Session list/revoke by ID not implemented. Duplicate favorite routes under `/api/v1/recipes/my/favorites` and `/api/v1/users/recipes/favs`.

