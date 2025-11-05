# API Endpoints

## Recipe Management

POST /api/v1/recipes # Create
GET /api/v1/recipes/{id} # Get by ID
GET /api/v1/recipes # List all
GET /api/v1/recipes/author/{id} # By author
POST /api/v1/recipes/search # Advanced search
POST /api/v1/recipes/find-by-ingredients # "What can I cook?"
PATCH /api/v1/recipes/{id} # Update
POST /api/v1/recipes/{id}/ingredients # Add ingredient
POST /api/v1/recipes/{id}/steps # Add step
POST /api/v1/recipes/{id}/rating # Rate recipe
POST /api/v1/recipes/{id}/scale # Scale servings
DELETE /api/v1/recipes/{id} # Delete
GET /api/v1/recipes/recommendations/top-rated
GET /api/v1/recipes/recommendations/quick-recipes

## Authentication

POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/refresh-token
POST /api/v1/auth/logout
