# API Schema

**API type:** REST

## Auth

### `POST` /api/v1/auth/signup

**Register user**

Creates account and returns JWT access/refresh tokens; stores session in Redis.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | strict — 10/min per IP |
| **Tags** | auth |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "first_name": "string (2-50)",
  "last_name": "string (2-50)",
  "email": "string",
  "password": "string (strong)",
  "phone_number": "string (optional)",
  "gender": "enum",
  "date_of_birth": "string (optional ISO)"
}
```

**Example:**

```json
{
  "first_name": "Alex",
  "last_name": "Cook",
  "email": "alex@example.com",
  "password": "SecurePass1!",
  "gender": "prefer_not_to_say"
}
```

#### Responses

- **201** — User created with tokens

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

### `POST` /api/v1/auth/login

**Login**

Authenticates email/password and returns tokens.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | strict — 10/min per IP |
| **Tags** | auth |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "email": "string",
  "password": "string"
}
```

**Example:**

```json
{
  "email": "alex@example.com",
  "password": "SecurePass1!"
}
```

#### Responses

- **200** — Authenticated

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### `POST` /api/v1/auth/refresh

**Refresh access token**

Issues new access token when refresh token and Redis session are valid.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | api — 30/min per IP |
| **Tags** | auth |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "refresh_token": "string"
}
```

**Example:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Responses

- **200** — New access token

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

- **404** — Session not found in Redis

```json
{
  "detail": "Session not found"
}
```

---

### `POST` /api/v1/auth/logout

**Logout**

Revokes refresh token session; optional logout_all query revokes all devices.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | default |
| **Tags** | auth |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| logout_all | query | boolean | No | Revoke all sessions for user |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "refresh_token": "string"
}
```

**Example:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Responses

- **200** — Logged out

```json
{
  "message": "Successfully logged out",
  "revoked_sessions": 1
}
```

---

### `GET` /api/v1/auth/me

**Current user**

Returns profile for Bearer-authenticated user.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | generous — 120/min per IP |
| **Tags** | auth |

#### Responses

- **200** — User profile

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "alex@example.com",
  "first_name": "Alex",
  "roles": [
    "common_user"
  ],
  "is_active": true
}
```

---

## Recipes

### `GET` /api/v1/recipes/featured

**Featured recipes**

Curated list for homepage; no auth required.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | public — 100/min per IP |
| **Tags** | recipes |

#### Responses

- **200** — List of recipe summaries

```json
[
  {
    "id": 1,
    "name": "Classic Margherita Pizza",
    "average_rating": 4.8
  }
]
```

---

### `GET` /api/v1/recipes

**Search recipes**

Paginated search with filters (name, cuisine, difficulty, tags, meal_types, ingredient, min_rating, max_cooking_time).

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | public — 100/min per IP |
| **Tags** | recipes |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| page | query | integer | No | Page number |
| name | query | string | No | Name contains filter |

#### Responses

- **200** — Paginated results

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 20
}
```

---

### `GET` /api/v1/recipes/{recipe_id}

**Get recipe by ID**

Full recipe detail; increments view count.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | public — 100/min per IP |
| **Tags** | recipes |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| recipe_id | path | integer | Yes | Recipe ID |

#### Responses

- **200** — Recipe detail

```json
{
  "id": 42,
  "name": "Thai Green Curry",
  "view_count": 1523
}
```

- **404** — Not found

```json
{
  "detail": "Recipe not found"
}
```

---

### `POST` /api/v1/recipes/

**Create recipe**

Authenticated author creates a new recipe with ingredients and steps.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | sensitive — 5/min per IP |
| **Tags** | recipes |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "name": "string",
  "description": "string",
  "difficulty": "enum",
  "cuisine": "enum",
  "ingredients": "array",
  "steps": "array"
}
```

**Example:**

```json
{
  "name": "Weeknight Stir Fry",
  "description": "Quick vegetable stir fry",
  "difficulty": "easy"
}
```

#### Responses

- **201** — Created

```json
{
  "id": 99,
  "message": "Recipe created"
}
```

---

### `PUT` /api/v1/recipes/{recipe_id}

**Update recipe**

Author updates recipe fields.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | sensitive — 5/min per IP |
| **Tags** | recipes |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| recipe_id | path | integer | Yes | Recipe ID |

#### Responses

- **200** — Updated

```json
{
  "id": 42,
  "version": 2
}
```

---

### `DELETE` /api/v1/recipes/{recipe_id}

**Soft delete recipe**

Marks recipe deleted; author only.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | sensitive — 5/min per IP |
| **Tags** | recipes |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| recipe_id | path | integer | Yes | Recipe ID |

#### Responses

- **204** — Deleted
---

### `PATCH` /api/v1/recipes/{recipe_id}/favorites/toggle

**Toggle favorite**

Add or remove recipe from user favorites.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | generous — 120/min per IP |
| **Tags** | recipes, favorites |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| recipe_id | path | integer | Yes | Recipe ID |

#### Responses

- **200** — Toggled

```json
{
  "message": "Favorite status updated successfully"
}
```

---

### `GET` /api/v1/recipes/{recipe_id}/reviews

**List reviews**

Paginated reviews for a recipe.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | public — 100/min per IP |
| **Tags** | recipes, reviews |

#### Parameters

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| recipe_id | path | integer | Yes | Recipe ID |

#### Responses

- **200** — Review page

```json
{
  "items": [
    {
      "rating": 5,
      "comment": "Delicious and easy!"
    }
  ],
  "total": 1
}
```

---

### `POST` /api/v1/recipes/{recipe_id}/reviews

**Create review**

Authenticated user adds rating 1-5 and optional comment; one review per user per recipe.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | sensitive — 5/min per IP |
| **Tags** | recipes, reviews |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "rating": "integer 1-5",
  "comment": "string (optional)"
}
```

**Example:**

```json
{
  "rating": 5,
  "comment": "Will make again!"
}
```

#### Responses

- **201** — Review created

```json
{
  "review_id": 7,
  "average_rating": 4.6
}
```

---

## Service

### `GET` /

**API welcome**

Simple welcome message for root path.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | default — 60/min per IP |
| **Tags** | service |

#### Responses

- **200** — Welcome JSON

```json
{
  "message": "Welcome to the Cooking Recipes API!"
}
```

---

### `GET` /health

**Health check**

Liveness probe for ALB, ECS, and Docker HEALTHCHECK.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | default — 60/min per IP |
| **Tags** | service |

#### Responses

- **200** — Service healthy

```json
{
  "status": "healthy"
}
```

---

### `GET` /docs

**Swagger UI**

FastAPI interactive OpenAPI documentation.

| | |
|---|---|
| **Auth required** | No |
| **Rate limit** | public |
| **Tags** | service |

#### Responses

- **200** — HTML Swagger UI

```json
{
  "note": "Open in browser at https://api.recipes.example.com/docs"
}
```

---

## Users

### `GET` /api/v1/users/profile

**Get user profile (extended)**

Detailed profile for current user.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | default |
| **Tags** | users |

#### Responses

- **200** — Profile

```json
{
  "user_id": "123",
  "bio": "",
  "profile_picture_url": null
}
```

---

### `PUT` /api/v1/users/profile

**Update profile**

Partial profile update; returns 204 No Content.

| | |
|---|---|
| **Auth required** | Yes |
| **Rate limit** | default |
| **Tags** | users |

#### Request body

**Content-Type:** `application/json`

**Schema (summary):**

```json
{
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "phone_number": "string (optional)"
}
```

**Example:**

```json
{
  "first_name": "Alexandra"
}
```

#### Responses

- **204** — Updated
---

## Additional notes

# API Schema

> **Production base URL (deployed):** `https://api.recipes.example.com`

> **Local:** `http://127.0.0.1:8080` or `https://127.0.0.1:8443` when SSL enabled.

> **Auth:** `Authorization: Bearer <access_token>` on protected routes.

> **Full reference:** See also [docs/API_ENDPOINTS.md](../../API_ENDPOINTS.md) for exhaustive request/response examples and error codes.

> **Warnings:** Duplicate favorites endpoints (`/recipes/my/favorites` vs `/users/recipes/favs`). Session management routes under `/auth/sessions` are stubs. Rate limits are per-container until Redis limiter is added. Do not expose `/admin/rate-limit-status` publicly in production without auth.

> **Good:** All business routes share `/api/v1/` prefix except service routes `/`, `/health`, `/docs`.

