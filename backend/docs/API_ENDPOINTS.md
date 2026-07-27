# API Endpoints Documentation

Complete reference for all API endpoints in the Cooking Recipe API.

## Table of Contents

- [Authentication Endpoints](#authentication-endpoints)
- [User Endpoints](#user-endpoints)
- [Recipe Endpoints](#recipe-endpoints)
- [Common Patterns](#common-patterns)
- [Error Responses](#error-responses)

## Base URL

```
Local Development: http://localhost:8080
Production: https://api.yourdomain.com
```

## Authentication Endpoints

### POST /api/v1/auth/signup

Register a new user account.

**Request Body:**

```json
{
  "first_name": "string (2-50 chars)",
  "last_name": "string (2-50 chars)",
  "email": "string (valid email)",
  "password": "string (min 8 chars, uppercase, lowercase, number, special char)",
  "phone_number": "string (optional, international format +1234567890)",
  "gender": "male | female | prefer_not_to_say | other",
  "date_of_birth": "string (optional, ISO 8601 format)"
}
```

**Response (201 Created):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123"
}
```

**Rate Limit:** `strict` (10 requests/60s)

---

### POST /api/v1/auth/login

Authenticate user and receive tokens.

**Request Body:**

```json
{
  "email": "string",
  "password": "string"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123"
}
```

**Possible Errors:**

- `401 Unauthorized` - Invalid credentials
- `422 Validation Error` - Invalid request format

**Rate Limit:** `strict` (10 requests/60s)

---

### POST /api/v1/auth/refresh

Obtain a new access token using refresh token.

**Request Body:**

```json
{
  "refresh_token": "string"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123"
}
```

**Possible Errors:**

- `401 Unauthorized` - Invalid or expired refresh token
- `404 Not Found` - Session not found in Redis

**Rate Limit:** `api` (30 requests/60s)

---

### POST /api/v1/auth/logout

Logout user and revoke tokens.

**Query Parameters:**

- `logout_all` (boolean, optional): If true, logout from all devices. Default: false

**Request Body:**

```json
{
  "refresh_token": "string"
}
```

**Response (200 OK):**

```json
{
  "message": "Successfully logged out",
  "revoked_sessions": 1
}
```

**Possible Errors:**

- `401 Unauthorized` - Invalid refresh token

---

### GET /api/v1/auth/me

Get current authenticated user information.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "user_id": "123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "roles": ["common_user"],
  "is_active": true,
  "joined_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-11-16T08:45:00Z",
  "gender": "male",
  "date_of_birth": "1990-01-15",
  "profile_picture_url": null,
  "bio": ""
}
```

**Rate Limit:** `generous` (60 requests/60s)

---

## User Endpoints

### GET /api/v1/users/profile

Get current user's detailed profile.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "user_id": "123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "gender": "male",
  "date_of_birth": "1990-01-15",
  "profile_picture_url": null,
  "bio": "Food enthusiast and home cook",
  "roles": ["common_user"],
  "is_active": true,
  "joined_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-11-16T08:45:00Z"
}
```

---

### PUT /api/v1/users/profile

Update current user's profile information.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "first_name": "string (optional, 2-50 chars)",
  "last_name": "string (optional, 2-50 chars)",
  "phone_number": "string (optional, international format)",
  "gender": "male | female | prefer_not_to_say | other (optional)",
  "date_of_birth": "string (optional, ISO 8601)",
  "bio": "string (optional, max 500 chars)",
  "profile_picture_url": "string (optional, valid URL)"
}
```

**Response (204 No Content)**

**Possible Errors:**

- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid or expired token

---

### GET /api/v1/users/recipes/favs

Get current user's favorite recipes (paginated).

**Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:**

- `page` (integer, optional): Page number (default: 1)
- `size` (integer, optional): Items per page (default: 10, max: 100)
- `sort_by` (string, optional): Sort field (default: created_at)
- `sort_order` (string, optional): asc | desc (default: desc)

**Response (200 OK):**

```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "size": 10,
  "pages": 5
}
```

---

## Recipe Endpoints

### GET /api/v1/recipes/featured

Get featured recipes (curated collection).

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "Classic Spaghetti Carbonara",
    "description": "Traditional Italian pasta dish",
    "difficulty": "medium",
    "cuisine": "italian",
    "prep_time_minutes": 10,
    "cook_time_minutes": 20,
    "total_time_minutes": 30,
    "servings": 4,
    "average_rating": 4.5,
    "review_count": 120,
    "view_count": 1500,
    "favorite_count": 85,
    "author_name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

**Rate Limit:** `public` (100 requests/60s)

---

### GET /api/v1/recipes

Search and filter recipes with pagination.

**Query Parameters:**

**Pagination:**

- `page` (integer): Page number (default: 1)
- `size` (integer): Items per page (default: 10, max: 100)
- `sort_by` (string): Field to sort by (default: created_at)
- `sort_order` (string): asc | desc (default: desc)

**Filters:**

- `search` (string): Search in recipe names
- `author_id` (integer): Filter by author
- `difficulty` (string): easy | medium | hard
- `cuisine` (string): italian | mexican | chinese | etc.
- `meal_types` (string, comma-separated): breakfast, lunch, dinner, snack, dessert
- `tags` (string, comma-separated): Filter by tags
- `ingredients` (string, comma-separated): Filter by ingredients
- `min_rating` (float): Minimum average rating (0-5)
- `max_prep_time` (integer): Maximum prep time in minutes
- `max_cook_time` (integer): Maximum cook time in minutes
- `max_total_time` (integer): Maximum total time in minutes

**Example:**

```
GET /api/v1/recipes?search=pasta&cuisine=italian&difficulty=easy&page=1&size=20
```

**Response (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Simple Pasta Aglio e Olio",
      "description": "Quick and easy Italian pasta",
      "difficulty": "easy",
      "cuisine": "italian",
      "meal_types": ["lunch", "dinner"],
      "prep_time_minutes": 5,
      "cook_time_minutes": 15,
      "total_time_minutes": 20,
      "servings": 2,
      "average_rating": 4.8,
      "review_count": 45,
      "view_count": 500,
      "favorite_count": 30,
      "tags": ["pasta", "quick", "vegetarian"],
      "author": {
        "id": 123,
        "name": "Jane Smith"
      },
      "created_at": "2025-10-01T14:30:00Z",
      "updated_at": "2025-10-01T14:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

**Rate Limit:** `public` (100 requests/60s)

---

### GET /api/v1/recipes/{recipe_id}

Get detailed information for a specific recipe.

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Classic Spaghetti Carbonara",
  "description": "Traditional Italian pasta dish with eggs, cheese, and pancetta",
  "difficulty": "medium",
  "cuisine": "italian",
  "meal_types": ["lunch", "dinner"],
  "author": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "ingredients": [
    {
      "id": 1,
      "name": "Spaghetti",
      "quantity_value": 400,
      "quantity_unit": "g",
      "is_optional": false,
      "is_vegan": true,
      "is_vegetarian": true,
      "is_gluten_free": false,
      "is_dairy_free": true,
      "allergens": ["gluten"],
      "substitutes": ["gluten-free pasta"]
    },
    {
      "id": 2,
      "name": "Eggs",
      "quantity_value": 4,
      "quantity_unit": "whole",
      "is_optional": false,
      "is_vegan": false,
      "is_vegetarian": true,
      "is_gluten_free": true,
      "is_dairy_free": true,
      "allergens": ["eggs"],
      "substitutes": []
    }
  ],
  "steps": [
    {
      "id": 1,
      "step_number": 1,
      "description": "Bring a large pot of salted water to boil. Cook spaghetti according to package directions.",
      "duration_minutes": 10,
      "technique": "boiling",
      "temperature": "100°C",
      "ingredients_used": ["Spaghetti"]
    },
    {
      "id": 2,
      "step_number": 2,
      "description": "While pasta cooks, whisk eggs with grated Pecorino Romano cheese.",
      "duration_minutes": 3,
      "technique": "whisking",
      "temperature": null,
      "ingredients_used": ["Eggs", "Pecorino Romano"]
    }
  ],
  "prep_time_minutes": 10,
  "cook_time_minutes": 20,
  "rest_time_minutes": 0,
  "total_time_minutes": 30,
  "servings": 4,
  "serving_size": "1 plate (300g)",
  "nutritional_info": {
    "calories": 450,
    "protein_g": 20.5,
    "carbs_g": 65.0,
    "fat_g": 15.0,
    "fiber_g": 3.0,
    "sodium_mg": 450.0
  },
  "tags": ["pasta", "italian", "traditional", "eggs"],
  "average_rating": 4.7,
  "review_count": 150,
  "view_count": 2500,
  "favorite_count": 120,
  "version": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "deleted_at": null
}
```

**Possible Errors:**

- `404 Not Found` - Recipe does not exist

**Rate Limit:** `public` (100 requests/60s)

**Note:** This endpoint automatically increments the view counter.

---

### POST /api/v1/recipes

Create a new recipe.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "name": "string (required, max 200 chars)",
  "description": "string (optional, max 2000 chars)",
  "difficulty": "easy | medium | hard (required)",
  "cuisine": "italian | mexican | chinese | japanese | indian | french | thai | greek | american | mediterranean | spanish | korean | vietnamese | middle_eastern | caribbean | african | german | british | russian | other (required)",
  "meal_types": [
    "breakfast | lunch | dinner | snack | dessert (required, array)"
  ],
  "servings": "integer (required, min 1)",
  "serving_size": "string (optional, e.g., '1 plate', '200ml')",
  "prep_time_minutes": "integer (required, min 0)",
  "cook_time_minutes": "integer (required, min 0)",
  "rest_time_minutes": "integer (optional, default 0)",
  "ingredients": [
    {
      "name": "string (required)",
      "quantity_value": "number (required, positive)",
      "quantity_unit": "string (required, e.g., 'g', 'ml', 'cup', 'tsp')",
      "is_optional": "boolean (optional, default false)",
      "is_vegan": "boolean (optional, default false)",
      "is_vegetarian": "boolean (optional, default false)",
      "is_gluten_free": "boolean (optional, default false)",
      "is_dairy_free": "boolean (optional, default false)",
      "allergens": ["string array (optional)"],
      "substitutes": ["string array (optional)"]
    }
  ],
  "steps": [
    {
      "step_number": "integer (required, starts at 1)",
      "description": "string (required)",
      "duration_minutes": "integer (optional)",
      "technique": "string (optional, e.g., 'boiling', 'frying', 'baking')",
      "temperature": "string (optional, e.g., '180°C', '350°F')",
      "ingredients_used": ["string array (optional)"]
    }
  ],
  "tags": ["string array (optional, e.g., 'quick', 'healthy', 'vegan')"],
  "nutritional_info": {
    "calories": "integer (optional)",
    "protein_g": "number (optional)",
    "carbs_g": "number (optional)",
    "fat_g": "number (optional)",
    "fiber_g": "number (optional)",
    "sodium_mg": "number (optional)"
  }
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "message": "Recipe created successfully",
  "created_at": "2025-11-16T10:30:00Z"
}
```

**Possible Errors:**

- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid or expired token

**Rate Limit:** `sensitive` (20 requests/60s)

---

### PUT /api/v1/recipes/{recipe_id}

Update an existing recipe (author only).

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Request Body:** (Same as POST /recipes, all fields optional)

**Response (200 OK):**

```json
{
  "id": 1,
  "message": "Recipe updated successfully",
  "version": 2,
  "updated_at": "2025-11-16T11:00:00Z"
}
```

**Possible Errors:**

- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid token or not recipe author
- `404 Not Found` - Recipe does not exist

**Rate Limit:** `sensitive` (20 requests/60s)

---

### DELETE /api/v1/recipes/{recipe_id}

Soft delete a recipe (author only).

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (204 No Content)**

**Possible Errors:**

- `401 Unauthorized` - Invalid token or not recipe author
- `404 Not Found` - Recipe does not exist

**Rate Limit:** `sensitive` (20 requests/60s)

---

### POST /api/v1/recipes/{recipe_id}/restore

Restore a soft-deleted recipe (author only).

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (204 No Content)**

**Possible Errors:**

- `400 Bad Request` - Recipe is not deleted
- `401 Unauthorized` - Invalid token or not recipe author
- `404 Not Found` - Recipe does not exist

**Rate Limit:** `sensitive` (20 requests/60s)

---

### GET /api/v1/recipes/my

Get recipes created by the authenticated user.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:** (Standard pagination parameters)

- `page`, `size`, `sort_by`, `sort_order`

**Response (200 OK):** (Paginated recipe list)

**Rate Limit:** `generous` (60 requests/60s)

---

### GET /api/v1/recipes/my/favorites

Get recipes favorited by the authenticated user.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Query Parameters:** (Standard pagination parameters)

**Response (200 OK):** (Paginated recipe list)

**Rate Limit:** `generous` (60 requests/60s)

---

### GET /api/v1/recipes/is_favorite/{recipe_id}

Check if a recipe is in the user's favorites.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (200 OK):**

```json
{
  "is_favorite": true
}
```

**Rate Limit:** `generous` (60 requests/60s)

---

### PATCH /api/v1/recipes/{recipe_id}/favorites/toggle

Add or remove recipe from favorites.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (200 OK):**

```json
{
  "message": "Favorite status updated successfully"
}
```

**Possible Errors:**

- `404 Not Found` - Recipe does not exist

**Rate Limit:** `generous` (60 requests/60s)

---

### POST /api/v1/recipes/{recipe_id}/ratings

Add a review and rating to a recipe.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "recipe_id": "integer (required)",
  "rating": "integer (required, 1-5)",
  "comment": "string (optional, max 1000 chars)"
}
```

**Response (201 Created):**

```json
{
  "message": "Review added successfully",
  "recipe_id": 1,
  "new_average_rating": 4.6,
  "total_reviews": 151
}
```

**Possible Errors:**

- `400 Bad Request` - Validation error or duplicate review
- `404 Not Found` - Recipe does not exist

**Rate Limit:** `sensitive` (20 requests/60s)

---

### DELETE /api/v1/recipes/{recipe_id}/ratings

Delete user's review from a recipe.

**Headers:**

```
Authorization: Bearer {access_token}
```

**Path Parameters:**

- `recipe_id` (integer): Recipe ID

**Response (204 No Content)**

**Possible Errors:**

- `404 Not Found` - Recipe or review does not exist

**Rate Limit:** `sensitive` (20 requests/60s)

---

## Common Patterns

### Pagination

All list endpoints support pagination with these query parameters:

```
?page=1&size=20&sort_by=created_at&sort_order=desc
```

Response format:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### Authentication

Protected endpoints require a Bearer token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Date Formats

All dates use ISO 8601 format:

```
2025-11-16T10:30:00Z
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "field": "field_name",
    "value": "invalid_value"
  }
}
```

### Common HTTP Status Codes

| Code | Description                             |
| ---- | --------------------------------------- |
| 200  | Success                                 |
| 201  | Created                                 |
| 204  | No Content (Success, no body)           |
| 400  | Bad Request (Validation error)          |
| 401  | Unauthorized (Invalid or missing token) |
| 403  | Forbidden (Insufficient permissions)    |
| 404  | Not Found                               |
| 422  | Unprocessable Entity (Invalid data)     |
| 429  | Too Many Requests (Rate limit exceeded) |
| 500  | Internal Server Error                   |

### Rate Limit Response

When rate limit is exceeded:

```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 45
}
```

Headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700140800
```

---

## Health & Monitoring Endpoints

### GET /health

Check API health status.

**Response (200 OK):**

```json
{
  "status": "healthy"
}
```

### GET /admin/rate-limit-status

Get rate limiting statistics.

**Response (200 OK):**

```json
{
  "rate_limiting_enabled": true,
  "app_stats": {
    "total_requests": 15234,
    "blocked_requests": 45
  },
  "active_limits": 120,
  "configured_endpoints": 25
}
```

---

**Last Updated:** November 2025
**API Version:** 1.0.0
