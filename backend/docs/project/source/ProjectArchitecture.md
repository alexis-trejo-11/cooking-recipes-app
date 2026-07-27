---
layers:
  - name: "Presentation (clients)"
    description: "Angular SPA and future mobile clients consuming JSON over HTTPS."
    color: "#6366F1"
    expanded: true
    components:
      - "Angular dev server (:4200)"
      - "Production SPA (S3 + CloudFront placeholder)"
    responsibilities:
      - "Bearer JWT on protected routes"
      - "Recipe search UI and favorites"
    technologies:
      - "HTTPS"
      - "REST JSON"
      - "OpenAPI client (optional)"

  - name: "Edge & API gateway"
    description: "TLS termination and routing to FastAPI on ECS."
    color: "#10B981"
    expanded: false
    components:
      - "AWS Application Load Balancer"
      - "ACM certificate"
      - "CORS (Angular origins in main.py)"
    responsibilities:
      - "HTTPS only in production"
      - "Health checks to /health"
    technologies:
      - "ALB"
      - "ACM"

  - name: "Application (FastAPI)"
    description: "Uvicorn serves FastAPI app with global rate limit dependency and exception handlers."
    color: "#F59E0B"
    expanded: true
    components:
      - "main.py — lifespan, CORS, routers"
      - "auth — controllers, use cases, JWT middleware handlers"
      - "recipe — controller, DTOs, use cases"
      - "config — settings, redis, sql_session, rate_limiter"
    responsibilities:
      - "Map HTTP to use case execute()"
      - "Pydantic validation on requests/responses"
      - "No business rules in controllers"
    technologies:
      - "FastAPI"
      - "Pydantic v2"
      - "Uvicorn"

  - name: "Domain"
    description: "Entities, value objects, repository interfaces, domain exceptions."
    color: "#EC4899"
    expanded: true
    components:
      - "User, Session (auth)"
      - "Recipe, Ingredient, Review (recipe)"
      - "Specification criteria for search"
    responsibilities:
      - "Invariants and enums (DifficultyLevel, CuisineType, MealType)"
      - "Framework-agnostic rules"
    technologies:
      - "Pure Python"

  - name: "Infrastructure"
    description: "SQLAlchemy async repositories, Redis session store, JWT and bcrypt services."
    color: "#EF4444"
    expanded: true
    components:
      - "SQLAlchemy models + Alembic"
      - "RecipeSpecificationBuilder → SQL"
      - "RedisUserSessionRepository"
      - "JwtTokenService, BcryptPasswordHasher"
    responsibilities:
      - "Persistence and external I/O"
      - "Implement domain interfaces"
    technologies:
      - "SQLAlchemy 2.0"
      - "aiosqlite / asyncpg (RDS)"
      - "Redis"

designPatterns:
  - title: "Clean Architecture"
    emoji: "🏛️"
    description: "Dependencies point inward: presentation → application → domain; infrastructure implements domain ports."
    category: "Structural"
    badge: "Core"
  - title: "Use case (application service)"
    emoji: "⚙️"
    description: "One class per operation (CreateRecipeUseCase, SearchRecipesUseCase) orchestrates domain and repositories."
    category: "Behavioral"
    badge: "Application"
  - title: "Specification"
    emoji: "🔍"
    description: "Composable RecipeByNameSpecification, AndSpecification, etc. translated to SQL via specification_builder."
    category: "Data"
    badge: "Recipe"
  - title: "Repository"
    emoji: "🗄️"
    description: "IRecipeRepository, IUserRepository abstract persistence; SQLAlchemy implementations in infrastructure."
    category: "Data"
    badge: "DDD"
  - title: "Dependency injection"
    emoji: "💉"
    description: "FastAPI Depends() wires use cases and repositories per request in presentation/dependencies.py."
    category: "Creational"
    badge: "FastAPI"
  - title: "Soft delete"
    emoji: "🗑️"
    description: "Recipes marked deleted remain in DB; restore endpoint reverses flag; search excludes deleted by default."
    category: "Domain"
    badge: "Recipe"

scalabilityStrategies:
  - title: "Horizontally scale ECS tasks"
    description: "Stateless API containers behind ALB; session state in ElastiCache Redis, not in process memory."
  - title: "RDS PostgreSQL"
    description: "Move from SQLite to RDS with connection pool (DB_POOL_SIZE) for production traffic."
  - title: "Read-heavy recipe search"
    description: "Specification-built queries with pagination; add DB indexes on name, author_id, rating per DATABASE_SCHEMA.md."
  - title: "Optional CDN for static media"
    description: "Profile pictures and recipe images can later use S3 + CloudFront (profile_picture_url field ready)."

securityStrategies:
  - title: "JWT access + refresh"
    description: "Short-lived access token (30 min); refresh validated against Redis session store."
  - title: "bcrypt passwords"
    description: "BcryptPasswordHasher in infrastructure; strong password rules on signup DTO."
  - title: "Author-only mutations"
    description: "Update/delete recipe and reviews require authenticated author checks in use cases."
  - title: "Rate limiting"
    description: "Per-IP sliding window: strict (auth), sensitive (writes), public (browse), generous (profile)."
  - title: "Secrets in AWS"
    description: "JWT_SECRET_KEY from Secrets Manager in ECS task definition—not baked in Docker image for prod."

cacheStrategies:
  - name: "Redis session store"
    description: "Refresh tokens and session metadata keyed with REDIS_SESSION_PREFIX"
    ttl: "Refresh token lifetime (90 days configurable)"
    coverage: "Auth logout and refresh flows"
  - name: "In-process rate limit counters"
    description: "RateLimitManager defaultdict per endpoint:IP in app memory"
    ttl: "60s sliding window per profile"
    coverage: "All routed endpoints via global Depends"
  - name: "Future: Redis rate limits"
    description: "Documented in DEPLOYMENT.md for multi-task ECS fairness"
    ttl: "N/A"
    coverage: "Placeholder for shared limiter across replicas"

architectureFeatures:
  - title: "Auto OpenAPI"
    emoji: "📖"
    description: "FastAPI generates /docs and /redoc from Pydantic models and route metadata."
  - title: "Global exception handling"
    emoji: "🛡️"
    description: "GlobalExceptionHandler maps domain errors to consistent HTTP responses."
  - title: "Lifespan hooks"
    emoji: "🔄"
    description: "init_db, initialize_redis on startup; graceful close on shutdown."
  - title: "View analytics"
    emoji: "📊"
    description: "GET /recipes/{id} increments view count via IncrementViewCountUseCase."

architectureDiagram:
  legendItems:
    - type: "client"
      label: "Client"
      color: "#6366F1"
      icon: "monitor"
    - type: "gateway"
      label: "ALB"
      color: "#10B981"
      icon: "shield"
    - type: "service"
      label: "API"
      color: "#F59E0B"
      icon: "server"
    - type: "database"
      label: "Database"
      color: "#EF4444"
      icon: "database"
    - type: "queue"
      label: "Redis"
      color: "#8B5CF6"
      icon: "layers"
    - type: "monitoring"
      label: "Monitoring"
      color: "#64748B"
      icon: "activity"

  nodes:
    - id: "angular-app"
      label: "Angular SPA"
      type: "client"
      x: 80
      y: 120
      connections: ["alb"]
      status: "healthy"
      traffic: 200
    - id: "alb"
      label: "ALB (HTTPS)"
      type: "gateway"
      x: 280
      y: 120
      connections: ["ecs-api"]
      status: "healthy"
      traffic: 200
    - id: "ecs-api"
      label: "ECS Fargate — FastAPI"
      type: "service"
      x: 480
      y: 120
      connections: ["rds", "redis"]
      status: "healthy"
      traffic: 180
    - id: "rds"
      label: "RDS PostgreSQL"
      type: "database"
      x: 680
      y: 60
      connections: []
      status: "healthy"
      traffic: 90
    - id: "redis"
      label: "ElastiCache Redis"
      type: "queue"
      x: 680
      y: 180
      connections: []
      status: "healthy"
      traffic: 60
    - id: "cloudwatch"
      label: "CloudWatch Logs"
      type: "monitoring"
      x: 280
      y: 260
      connections: ["ecs-api"]
      status: "healthy"
      traffic: 10
    - id: "ecr"
      label: "ECR image"
      type: "service"
      x: 480
      y: 260
      connections: ["ecs-api"]
      status: "healthy"
      traffic: 5

  connections:
    - id: "c1"
      from: "angular-app"
      to: "alb"
      label: "HTTPS"
      protocol: "TLS 1.2+"
      isActive: true
    - id: "c2"
      from: "alb"
      to: "ecs-api"
      label: "Forward"
      protocol: "HTTP"
      isActive: true
    - id: "c3"
      from: "ecs-api"
      to: "rds"
      label: "async SQL"
      protocol: "PostgreSQL"
      isActive: true
    - id: "c4"
      from: "ecs-api"
      to: "redis"
      label: "Sessions"
      protocol: "Redis"
      isActive: true
    - id: "c5"
      from: "ecs-api"
      to: "cloudwatch"
      label: "Logs"
      protocol: "awslogs"
      isActive: true

dataFlow:
  requestFlow:
    - number: 1
      title: "HTTP request"
      description: "Client calls /api/v1/... with optional Authorization Bearer token."
      icon: "send"
    - number: 2
      title: "Rate limit & auth"
      description: "Global rate_limiter_dependency runs; get_current_user decodes JWT for protected routes."
      icon: "shield"
    - number: 3
      title: "Use case"
      description: "Controller invokes use case execute() with DTOs and domain IDs."
      icon: "cog"
    - number: 4
      title: "Repository / spec"
      description: "Infrastructure runs SQLAlchemy query from specification or loads entity by ID."
      icon: "database"
    - number: 5
      title: "JSON response"
      description: "Pydantic response_model serializes result to client."
      icon: "reply"

  eventFlow:
    - number: 1
      title: "Recipe viewed"
      description: "GET /recipes/{id} triggers IncrementViewCountUseCase before returning payload."
      icon: "eye"
    - number: 2
      title: "Review submitted"
      description: "CreateReviewUseCase updates aggregate rating on recipe."
      icon: "star"
    - number: 3
      title: "Session created"
      description: "Login/signup stores refresh token metadata in Redis via RedisUserSessionRepository."
      icon: "key"
    - number: 4
      title: "Logout"
      description: "Logout use case deletes session key(s) from Redis; optional logout_all revokes all devices."
      icon: "log-out"

techDecisions:
  - title: "FastAPI over Django"
    problem: "API-only backend with async I/O and automatic OpenAPI for a separate Angular frontend."
    solution: "FastAPI + Pydantic for validation and docs; async SQLAlchemy sessions."
    alternatives:
      - "Django REST Framework"
      - "Node/NestJS"
    outcome: "Lightweight, typed DTOs, fast iteration for recipe search endpoints."
    icon: "zap"
  - title: "Clean Architecture + DDD"
    problem: "Recipe domain complexity (search specs, reviews, soft delete) must stay testable."
    solution: "Separate domain/application/infrastructure per module; use cases as single entry points."
    alternatives:
      - "Anemic models in controllers"
      - "Active record only"
    outcome: "Unit tests on use cases and specifications without HTTP."
    icon: "layers"
  - title: "SQLite local, PostgreSQL AWS"
    problem: "Simple local dev; production needs managed RDS."
    solution: "DATABASE_URL drives engine; docker-compose mounts cooking_app.db for quick demos."
    alternatives:
      - "PostgreSQL everywhere"
    outcome: "Alembic migrations via start.sh; switch env for ECS deploy."
    icon: "database"
  - title: "Redis for sessions only"
    problem: "Refresh token revocation and multi-device logout require server-side state."
    solution: "ElastiCache Redis in AWS; docker-compose redis service on port 6378 locally."
    alternatives:
      - "Stateless JWT only"
      - "Database session table"
    outcome: "Secure logout; refresh fails with 404 if session removed."
    icon: "redis"
---

# Architecture

> **Deployed view:** Clients hit `https://api.recipes.example.com` → ALB → ECS tasks running this repo’s Docker image; data in RDS, sessions in ElastiCache.

> **Local view:** `uvicorn` or `docker compose up` on ports 8080/8443 with SQLite file and Redis container.

> **Tech debt:** Rate limits are in-memory per task—scale ECS to 2+ tasks without Redis rate limiter and limits diverge per instance. Session list/revoke by ID not implemented. Duplicate favorite routes under `/api/v1/recipes/my/favorites` and `/api/v1/users/recipes/favs`.
