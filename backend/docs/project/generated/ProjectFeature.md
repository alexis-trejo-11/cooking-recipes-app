# Project Features

## JWT authentication & Redis sessions

Signup and login return access/refresh tokens; refresh validated against Redis; logout revokes session(s) including logout-all-devices.

| Property | Value |
| --- | --- |
| ID | jwt-auth-sessions |
| Category | authentication |
| Status | stable |
| Icon | shield-lock |

### Highlights

- POST /api/v1/auth/signup, /login, /refresh, /logout
- GET /api/v1/auth/me for current user
- Device info captured on signup/login (IP, user-agent)

### Tech stack

- PyJWT
- bcrypt
- Redis
- app/modules/auth

### Metrics

| Label | Value | Trend |
| --- | --- | --- |
| Access token TTL | 30 min | stable |
| Refresh token TTL | 90 days | stable |

### Code snippet

_app/config/app_settings.py_

```python
JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 90
```

## Recipe CRUD & soft delete

Authors create rich recipes (ingredients, steps, tags, meal types); update and soft-delete; restore endpoint for deleted recipes.

| Property | Value |
| --- | --- |
| ID | recipe-crud |
| Category | api |
| Status | stable |
| Icon | book-open |

### Highlights

- POST/PUT/DELETE /api/v1/recipes/
- POST /api/v1/recipes/{id}/restore
- Author-only mutations enforced in use cases

### Tech stack

- app/modules/recipe/application
- SQLAlchemy

## Advanced recipe search

Paginated search with filters: name, author, difficulty, cuisine, tags, meal types, ingredient, min rating, max cooking time.

| Property | Value |
| --- | --- |
| ID | recipe-search |
| Category | api |
| Status | stable |
| Icon | search |

### Highlights

- GET /api/v1/recipes with query params
- RecipeSpecificationBuilder composes SQL specs
- Excludes soft-deleted by default

### Tech stack

- Specification pattern
- app/modules/recipe/infrastructure/persistence

### Metrics

| Label | Value | Trend |
| --- | --- | --- |
| Public search rate | 100/min IP | stable |

## Favorites

Toggle favorite, list user favorites, check is_favorite flag for UI state.

| Property | Value |
| --- | --- |
| ID | favorites |
| Category | api |
| Status | stable |
| Icon | heart |

### Highlights

- PATCH .../favorites/toggle
- GET /my/favorites and /is_favorite/{recipe_id}
- Alternate route GET /api/v1/users/recipes/favs

### Tech stack

- FavoriteRepository
- ToggleFavoriteUseCase

## Reviews & ratings

One review per user per recipe; CRUD on reviews updates aggregate recipe rating.

| Property | Value |
| --- | --- |
| ID | reviews-ratings |
| Category | api |
| Status | stable |
| Icon | star |

### Highlights

- GET/POST/PATCH/DELETE /api/v1/recipes/{id}/reviews
- GET .../reviews/my for current user's review

### Tech stack

- Review use cases
- app/modules/recipe/domain

## Featured list & view counter

Curated featured recipes for homepage; each recipe detail GET increments view count.

| Property | Value |
| --- | --- |
| ID | featured-analytics |
| Category | performance |
| Status | stable |
| Icon | trending-up |

### Highlights

- GET /api/v1/recipes/featured
- View increment on GET /recipes/{id}

### Tech stack

- GetFeaturedRecipesUseCase
- IncrementViewCountUseCase

## Endpoint rate limiting

Decorator profiles (strict, sensitive, public, generous, api) with per-IP sliding windows.

| Property | Value |
| --- | --- |
| ID | rate-limiting |
| Category | security |
| Status | stable |
| Icon | speedometer |

### Highlights

- Global Depends(rate_limiter_dependency) on all routers
- 429 with reset hint via RateLimitException
- GET /admin/rate-limit-status for ops

### Tech stack

- app/config/rate_limiter.py

### Code snippet

_app/config/rate_limiter.py_

```python
RATE_LIMIT_CONFIG = {
    "strict": {"max_requests": 10, "window_seconds": 60},
    "sensitive": {"max_requests": 5, "window_seconds": 60},
    "public": {"max_requests": 100, "window_seconds": 60},
}
```

## User profile management

Authenticated users read and update profile; list favorites via users router.

| Property | Value |
| --- | --- |
| ID | user-profile |
| Category | api |
| Status | stable |
| Icon | user |

### Highlights

- GET/PUT /api/v1/users/profile
- Linked to auth domain User entity

### Tech stack

- app/modules/auth/application/user_use_cases.py

## Docker & AWS deploy path

Containerized API with migrations on boot; documented ECS/RDS/ElastiCache topology.

| Property | Value |
| --- | --- |
| ID | docker-aws-deploy |
| Category | integration |
| Status | stable |
| Icon | docker |

### Highlights

- Dockerfile + docker-compose for local
- docs/DEPLOYMENT.md for ECS and production env
- Health checks on /health

### Tech stack

- Docker
- Alembic
- AWS ECS

## Additional notes

# Project Features

> **Stable:** Auth, recipe CRUD/search, favorites, reviews, featured, profile, rate limits.

> **Beta / stub:** `GET /auth/sessions` and `DELETE /auth/sessions/{id}` exist but `include_in_schema=False` and return not-implemented messages.

> **Before production AWS:** Rotate `JWT_SECRET_KEY`, point `DATABASE_URL` to RDS, Redis to ElastiCache, set `DEBUG=false`, tighten CORS to production Angular URL, enable ALB HTTPS only, consider Redis-backed rate limits for multi-task ECS.

