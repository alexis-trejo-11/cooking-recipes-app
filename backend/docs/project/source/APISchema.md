---
type: "REST"

httpEndpoints:
  - id: "root"
    method: "GET"
    urlPath: "/"
    summary: "API welcome"
    description: "Simple welcome message for root path."
    tags: ["service"]
    authenticated: false
    rateLimit: "default — 60/min per IP"
    responses:
      - status: 200
        description: "Welcome JSON"
        example:
          message: "Welcome to the Cooking Recipes API!"

  - id: "health"
    method: "GET"
    urlPath: "/health"
    summary: "Health check"
    description: "Liveness probe for ALB, ECS, and Docker HEALTHCHECK."
    tags: ["service"]
    authenticated: false
    rateLimit: "default — 60/min per IP"
    responses:
      - status: 200
        description: "Service healthy"
        example:
          status: "healthy"

  - id: "auth-signup"
    method: "POST"
    urlPath: "/api/v1/auth/signup"
    summary: "Register user"
    description: "Creates account and returns JWT access/refresh tokens; stores session in Redis."
    tags: ["auth"]
    authenticated: false
    rateLimit: "strict — 10/min per IP"
    requestBody:
      contentType: "application/json"
      schema:
        first_name: "string (2-50)"
        last_name: "string (2-50)"
        email: "string"
        password: "string (strong)"
        phone_number: "string (optional)"
        gender: "enum"
        date_of_birth: "string (optional ISO)"
      example:
        first_name: "Alex"
        last_name: "Cook"
        email: "alex@example.com"
        password: "SecurePass1!"
        gender: "prefer_not_to_say"
    responses:
      - status: 201
        description: "User created with tokens"
        example:
          access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          token_type: "bearer"
          expires_in: 1800
          user_id: "123e4567-e89b-12d3-a456-426614174000"

  - id: "auth-login"
    method: "POST"
    urlPath: "/api/v1/auth/login"
    summary: "Login"
    description: "Authenticates email/password and returns tokens."
    tags: ["auth"]
    authenticated: false
    rateLimit: "strict — 10/min per IP"
    requestBody:
      contentType: "application/json"
      schema:
        email: "string"
        password: "string"
      example:
        email: "alex@example.com"
        password: "SecurePass1!"
    responses:
      - status: 200
        description: "Authenticated"
        example:
          access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          token_type: "bearer"
          expires_in: 1800

  - id: "auth-refresh"
    method: "POST"
    urlPath: "/api/v1/auth/refresh"
    summary: "Refresh access token"
    description: "Issues new access token when refresh token and Redis session are valid."
    tags: ["auth"]
    authenticated: false
    rateLimit: "api — 30/min per IP"
    requestBody:
      contentType: "application/json"
      schema:
        refresh_token: "string"
      example:
        refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      - status: 200
        description: "New access token"
        example:
          access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          expires_in: 1800
      - status: 404
        description: "Session not found in Redis"
        example:
          detail: "Session not found"

  - id: "auth-logout"
    method: "POST"
    urlPath: "/api/v1/auth/logout"
    summary: "Logout"
    description: "Revokes refresh token session; optional logout_all query revokes all devices."
    tags: ["auth"]
    authenticated: false
    rateLimit: "default"
    parameters:
      - name: "logout_all"
        in: "query"
        type: "boolean"
        required: false
        description: "Revoke all sessions for user"
        example: false
    requestBody:
      contentType: "application/json"
      schema:
        refresh_token: "string"
      example:
        refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      - status: 200
        description: "Logged out"
        example:
          message: "Successfully logged out"
          revoked_sessions: 1

  - id: "auth-me"
    method: "GET"
    urlPath: "/api/v1/auth/me"
    summary: "Current user"
    description: "Returns profile for Bearer-authenticated user."
    tags: ["auth"]
    authenticated: true
    rateLimit: "generous — 120/min per IP"
    responses:
      - status: 200
        description: "User profile"
        example:
          user_id: "123e4567-e89b-12d3-a456-426614174000"
          email: "alex@example.com"
          first_name: "Alex"
          roles: ["common_user"]
          is_active: true

  - id: "users-profile-get"
    method: "GET"
    urlPath: "/api/v1/users/profile"
    summary: "Get user profile (extended)"
    description: "Detailed profile for current user."
    tags: ["users"]
    authenticated: true
    rateLimit: "default"
    responses:
      - status: 200
        description: "Profile"
        example:
          user_id: "123"
          bio: ""
          profile_picture_url: null

  - id: "users-profile-put"
    method: "PUT"
    urlPath: "/api/v1/users/profile"
    summary: "Update profile"
    description: "Partial profile update; returns 204 No Content."
    tags: ["users"]
    authenticated: true
    rateLimit: "default"
    requestBody:
      contentType: "application/json"
      schema:
        first_name: "string (optional)"
        last_name: "string (optional)"
        phone_number: "string (optional)"
      example:
        first_name: "Alexandra"
    responses:
      - status: 204
        description: "Updated"
        example: null

  - id: "recipes-featured"
    method: "GET"
    urlPath: "/api/v1/recipes/featured"
    summary: "Featured recipes"
    description: "Curated list for homepage; no auth required."
    tags: ["recipes"]
    authenticated: false
    rateLimit: "public — 100/min per IP"
    responses:
      - status: 200
        description: "List of recipe summaries"
        example:
          - id: 1
            name: "Classic Margherita Pizza"
            average_rating: 4.8

  - id: "recipes-search"
    method: "GET"
    urlPath: "/api/v1/recipes"
    summary: "Search recipes"
    description: "Paginated search with filters (name, cuisine, difficulty, tags, meal_types, ingredient, min_rating, max_cooking_time)."
    tags: ["recipes"]
    authenticated: false
    rateLimit: "public — 100/min per IP"
    parameters:
      - name: "page"
        in: "query"
        type: "integer"
        required: false
        description: "Page number"
        example: 1
      - name: "name"
        in: "query"
        type: "string"
        required: false
        description: "Name contains filter"
        example: "pasta"
    responses:
      - status: 200
        description: "Paginated results"
        example:
          items: []
          total: 0
          page: 1
          size: 20

  - id: "recipes-get"
    method: "GET"
    urlPath: "/api/v1/recipes/{recipe_id}"
    summary: "Get recipe by ID"
    description: "Full recipe detail; increments view count."
    tags: ["recipes"]
    authenticated: false
    rateLimit: "public — 100/min per IP"
    parameters:
      - name: "recipe_id"
        in: "path"
        type: "integer"
        required: true
        description: "Recipe ID"
        example: 42
    responses:
      - status: 200
        description: "Recipe detail"
        example:
          id: 42
          name: "Thai Green Curry"
          view_count: 1523
      - status: 404
        description: "Not found"
        example:
          detail: "Recipe not found"

  - id: "recipes-create"
    method: "POST"
    urlPath: "/api/v1/recipes/"
    summary: "Create recipe"
    description: "Authenticated author creates a new recipe with ingredients and steps."
    tags: ["recipes"]
    authenticated: true
    rateLimit: "sensitive — 5/min per IP"
    requestBody:
      contentType: "application/json"
      schema:
        name: "string"
        description: "string"
        difficulty: "enum"
        cuisine: "enum"
        ingredients: "array"
        steps: "array"
      example:
        name: "Weeknight Stir Fry"
        description: "Quick vegetable stir fry"
        difficulty: "easy"
    responses:
      - status: 201
        description: "Created"
        example:
          id: 99
          message: "Recipe created"

  - id: "recipes-update"
    method: "PUT"
    urlPath: "/api/v1/recipes/{recipe_id}"
    summary: "Update recipe"
    description: "Author updates recipe fields."
    tags: ["recipes"]
    authenticated: true
    rateLimit: "sensitive — 5/min per IP"
    parameters:
      - name: "recipe_id"
        in: "path"
        type: "integer"
        required: true
        description: "Recipe ID"
        example: 42
    responses:
      - status: 200
        description: "Updated"
        example:
          id: 42
          version: 2

  - id: "recipes-delete"
    method: "DELETE"
    urlPath: "/api/v1/recipes/{recipe_id}"
    summary: "Soft delete recipe"
    description: "Marks recipe deleted; author only."
    tags: ["recipes"]
    authenticated: true
    rateLimit: "sensitive — 5/min per IP"
    parameters:
      - name: "recipe_id"
        in: "path"
        type: "integer"
        required: true
        description: "Recipe ID"
        example: 42
    responses:
      - status: 204
        description: "Deleted"
        example: null

  - id: "recipes-favorites-toggle"
    method: "PATCH"
    urlPath: "/api/v1/recipes/{recipe_id}/favorites/toggle"
    summary: "Toggle favorite"
    description: "Add or remove recipe from user favorites."
    tags: ["recipes", "favorites"]
    authenticated: true
    rateLimit: "generous — 120/min per IP"
    parameters:
      - name: "recipe_id"
        in: "path"
        type: "integer"
        required: true
        description: "Recipe ID"
        example: 42
    responses:
      - status: 200
        description: "Toggled"
        example:
          message: "Favorite status updated successfully"

  - id: "recipes-reviews-list"
    method: "GET"
    urlPath: "/api/v1/recipes/{recipe_id}/reviews"
    summary: "List reviews"
    description: "Paginated reviews for a recipe."
    tags: ["recipes", "reviews"]
    authenticated: false
    rateLimit: "public — 100/min per IP"
    parameters:
      - name: "recipe_id"
        in: "path"
        type: "integer"
        required: true
        description: "Recipe ID"
        example: 42
    responses:
      - status: 200
        description: "Review page"
        example:
          items:
            - rating: 5
              comment: "Delicious and easy!"
          total: 1

  - id: "recipes-reviews-create"
    method: "POST"
    urlPath: "/api/v1/recipes/{recipe_id}/reviews"
    summary: "Create review"
    description: "Authenticated user adds rating 1-5 and optional comment; one review per user per recipe."
    tags: ["recipes", "reviews"]
    authenticated: true
    rateLimit: "sensitive — 5/min per IP"
    requestBody:
      contentType: "application/json"
      schema:
        rating: "integer 1-5"
        comment: "string (optional)"
      example:
        rating: 5
        comment: "Will make again!"
    responses:
      - status: 201
        description: "Review created"
        example:
          review_id: 7
          average_rating: 4.6

  - id: "openapi-docs"
    method: "GET"
    urlPath: "/docs"
    summary: "Swagger UI"
    description: "FastAPI interactive OpenAPI documentation."
    tags: ["service"]
    authenticated: false
    rateLimit: "public"
    responses:
      - status: 200
        description: "HTML Swagger UI"
        example:
          note: "Open in browser at https://api.recipes.example.com/docs"
---

# API Schema

> **Production base URL (deployed):** `https://api.recipes.example.com`

> **Local:** `http://127.0.0.1:8080` or `https://127.0.0.1:8443` when SSL enabled.

> **Auth:** `Authorization: Bearer <access_token>` on protected routes.

> **Full reference:** See also [docs/API_ENDPOINTS.md](../../API_ENDPOINTS.md) for exhaustive request/response examples and error codes.

> **Warnings:** Duplicate favorites endpoints (`/recipes/my/favorites` vs `/users/recipes/favs`). Session management routes under `/auth/sessions` are stubs. Rate limits are per-container until Redis limiter is added. Do not expose `/admin/rate-limit-status` publicly in production without auth.

> **Good:** All business routes share `/api/v1/` prefix except service routes `/`, `/health`, `/docs`.
