---
features:
  - id: "jwt-auth-sessions"
    title: "JWT authentication & Redis sessions"
    description: "Signup and login return access/refresh tokens; refresh validated against Redis; logout revokes session(s) including logout-all-devices."
    icon: "shield-lock"
    category: "authentication"
    status: "stable"
    highlights:
      - "POST /api/v1/auth/signup, /login, /refresh, /logout"
      - "GET /api/v1/auth/me for current user"
      - "Device info captured on signup/login (IP, user-agent)"
    techStack:
      - "PyJWT"
      - "bcrypt"
      - "Redis"
      - "app/modules/auth"
    metrics:
      - label: "Access token TTL"
        value: "30 min"
        trend: "stable"
        icon: "clock"
      - label: "Refresh token TTL"
        value: "90 days"
        trend: "stable"
        icon: "refresh"
    codeSnippet:
      language: "python"
      filename: "app/config/app_settings.py"
      code: |
        JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
        JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 90

  - id: "recipe-crud"
    title: "Recipe CRUD & soft delete"
    description: "Authors create rich recipes (ingredients, steps, tags, meal types); update and soft-delete; restore endpoint for deleted recipes."
    icon: "book-open"
    category: "api"
    status: "stable"
    highlights:
      - "POST/PUT/DELETE /api/v1/recipes/"
      - "POST /api/v1/recipes/{id}/restore"
      - "Author-only mutations enforced in use cases"
    techStack:
      - "app/modules/recipe/application"
      - "SQLAlchemy"

  - id: "recipe-search"
    title: "Advanced recipe search"
    description: "Paginated search with filters: name, author, difficulty, cuisine, tags, meal types, ingredient, min rating, max cooking time."
    icon: "search"
    category: "api"
    status: "stable"
    highlights:
      - "GET /api/v1/recipes with query params"
      - "RecipeSpecificationBuilder composes SQL specs"
      - "Excludes soft-deleted by default"
    techStack:
      - "Specification pattern"
      - "app/modules/recipe/infrastructure/persistence"
    metrics:
      - label: "Public search rate"
        value: "100/min IP"
        trend: "stable"
        icon: "gauge"

  - id: "favorites"
    title: "Favorites"
    description: "Toggle favorite, list user favorites, check is_favorite flag for UI state."
    icon: "heart"
    category: "api"
    status: "stable"
    highlights:
      - "PATCH .../favorites/toggle"
      - "GET /my/favorites and /is_favorite/{recipe_id}"
      - "Alternate route GET /api/v1/users/recipes/favs"
    techStack:
      - "FavoriteRepository"
      - "ToggleFavoriteUseCase"

  - id: "reviews-ratings"
    title: "Reviews & ratings"
    description: "One review per user per recipe; CRUD on reviews updates aggregate recipe rating."
    icon: "star"
    category: "api"
    status: "stable"
    highlights:
      - "GET/POST/PATCH/DELETE /api/v1/recipes/{id}/reviews"
      - "GET .../reviews/my for current user's review"
    techStack:
      - "Review use cases"
      - "app/modules/recipe/domain"

  - id: "featured-analytics"
    title: "Featured list & view counter"
    description: "Curated featured recipes for homepage; each recipe detail GET increments view count."
    icon: "trending-up"
    category: "performance"
    status: "stable"
    highlights:
      - "GET /api/v1/recipes/featured"
      - "View increment on GET /recipes/{id}"
    techStack:
      - "GetFeaturedRecipesUseCase"
      - "IncrementViewCountUseCase"

  - id: "rate-limiting"
    title: "Endpoint rate limiting"
    description: "Decorator profiles (strict, sensitive, public, generous, api) with per-IP sliding windows."
    icon: "speedometer"
    category: "security"
    status: "stable"
    highlights:
      - "Global Depends(rate_limiter_dependency) on all routers"
      - "429 with reset hint via RateLimitException"
      - "GET /admin/rate-limit-status for ops"
    techStack:
      - "app/config/rate_limiter.py"
    codeSnippet:
      language: "python"
      filename: "app/config/rate_limiter.py"
      code: |
        RATE_LIMIT_CONFIG = {
            "strict": {"max_requests": 10, "window_seconds": 60},
            "sensitive": {"max_requests": 5, "window_seconds": 60},
            "public": {"max_requests": 100, "window_seconds": 60},
        }

  - id: "user-profile"
    title: "User profile management"
    description: "Authenticated users read and update profile; list favorites via users router."
    icon: "user"
    category: "api"
    status: "stable"
    highlights:
      - "GET/PUT /api/v1/users/profile"
      - "Linked to auth domain User entity"
    techStack:
      - "app/modules/auth/application/user_use_cases.py"

  - id: "docker-aws-deploy"
    title: "Docker & AWS deploy path"
    description: "Containerized API with migrations on boot; documented ECS/RDS/ElastiCache topology."
    icon: "docker"
    category: "integration"
    status: "stable"
    highlights:
      - "Dockerfile + docker-compose for local"
      - "docs/DEPLOYMENT.md for ECS and production env"
      - "Health checks on /health"
    techStack:
      - "Docker"
      - "Alembic"
      - "AWS ECS"
---

# Project Features

> **Stable:** Auth, recipe CRUD/search, favorites, reviews, featured, profile, rate limits.

> **Beta / stub:** `GET /auth/sessions` and `DELETE /auth/sessions/{id}` exist but `include_in_schema=False` and return not-implemented messages.

> **Before production AWS:** Rotate `JWT_SECRET_KEY`, point `DATABASE_URL` to RDS, Redis to ElastiCache, set `DEBUG=false`, tighten CORS to production Angular URL, enable ALB HTTPS only, consider Redis-backed rate limits for multi-task ECS.
