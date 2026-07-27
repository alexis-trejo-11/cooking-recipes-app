# Database Schema Documentation

Complete database schema for the Cooking Recipe API.

## Table of Contents

- [Overview](#overview)
- [Database Technologies](#database-technologies)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tables](#tables)
- [Indexes](#indexes)
- [Constraints](#constraints)
- [Migrations](#migrations)

## Overview

The database follows a **normalized relational design** with careful attention to:

- Data integrity through foreign keys and constraints
- Query performance through strategic indexing
- Scalability through proper data types and relationships
- Soft deletion for audit trails

### Database Configuration

**Default (Development):**

- Engine: SQLite with async support
- Driver: aiosqlite
- Location: `./cooking_app.db`

**Production:**

- Recommended: PostgreSQL 13+
- Connection: `postgresql+asyncpg://user:pass@host:5432/db`

## Database Technologies

### ORM & Migrations

- **SQLAlchemy 2.0.23** - Async ORM with modern API
- **Alembic 1.12.1** - Database migration management
- **aiosqlite 0.19.0** - Async SQLite driver

### Features

- **Async Operations** - Non-blocking database I/O
- **Connection Pooling** - Efficient connection management
- **Transaction Management** - ACID compliance
- **Type Safety** - Strong typing with SQLAlchemy models

## Entity Relationship Diagram

```
                                    ┌──────────────────┐
                                    │      USERS       │
                                    │                  │
                                    │ id (PK)          │
                                    │ first_name       │
                                    │ last_name        │
                                    │ email (UNIQUE)   │
                                    │ password         │
                                    │ phone_number     │
                                    │ roles            │
                                    │ gender           │
                                    │ date_of_birth    │
                                    │ profile_pic_url  │
                                    │ bio              │
                                    │ is_active        │
                                    │ joined_at        │
                                    │ last_login       │
                                    └─────────┬────────┘
                                              │
                                              │ 1
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    │                         │                         │
                  1 │                       * │                       * │
          ┌─────────▼─────────┐   ┌──────────▼───────────┐   ┌────────▼────────┐
          │  USER_SESSIONS    │   │      RECIPES         │   │ RECIPE_REVIEWS  │
          │                   │   │                      │   │                 │
          │ session_id (PK)   │   │ id (PK)              │   │ recipe_id (FK)  │
          │ user_id (FK)      │   │ name                 │   │ user_id (FK)    │
          │ refresh_token     │   │ author_id (FK)       │   │ rating          │
          │ device_info       │   │ description          │   │ comment         │
          │ ip_address        │   │ difficulty           │   │ reviewed_at     │
          │ user_agent        │   │ cuisine              │   └─────────────────┘
          │ created_at        │   │ servings             │
          │ expires_at        │   │ serving_size         │
          │ last_activity     │   │ prep_time_minutes    │
          └───────────────────┘   │ cook_time_minutes    │
                                  │ rest_time_minutes    │
                                  │ calories             │
                                  │ protein_g            │
                                  │ carbs_g              │
                                  │ fat_g                │
                                  │ fiber_g              │
                                  │ sodium_mg            │
                                  │ version              │
                                  │ view_count           │
                                  │ created_at           │
                                  │ updated_at           │
                                  │ deleted_at           │
                                  └──────────┬───────────┘
                                             │
                                             │ 1
                                             │
            ┌────────────────────┬───────────┼───────────┬────────────────────┐
            │                    │           │           │                    │
          * │                  * │         * │         * │                  * │
   ┌────────▼─────────┐ ┌────────▼────────┐ ┌▼─────────▼────┐ ┌─────────────▼──────┐
   │   INGREDIENTS    │ │  RECIPE_STEPS   │ │RECIPE_FAVORITES│ │ RECIPE_MEAL_TYPES  │
   │                  │ │                 │ │                │ │                    │
   │ id (PK)          │ │ id (PK)         │ │ recipe_id (FK) │ │ id (PK)            │
   │ recipe_id (FK)   │ │ recipe_id (FK)  │ │ user_id (FK)   │ │ recipe_id (FK)     │
   │ name             │ │ step_number     │ │ favorited_at   │ │ meal_type          │
   │ quantity_value   │ │ description     │ └────────────────┘ └────────────────────┘
   │ quantity_unit    │ │ duration_min    │
   │ is_optional      │ │ technique       │        * │
   │ is_vegan         │ │ temperature     │          │
   │ is_vegetarian    │ │ ingredients     │          │ *
   │ is_gluten_free   │ └─────────────────┘   ┌──────▼────────┐
   │ is_dairy_free    │                       │ RECIPE_TAGS   │
   │ allergens        │                       │               │
   │ substitutes      │                       │ recipe_id(FK) │
   └──────────────────┘                       │ tag_id (FK)   │
                                              └───────┬───────┘
                                                      │
                                                      │ *
                                                      │
                                                      │ 1
                                              ┌───────▼───────┐
                                              │     TAGS      │
                                              │               │
                                              │ id (PK)       │
                                              │ name (UNIQUE) │
                                              │ description   │
                                              │ created_at    │
                                              └───────────────┘
```

## Tables

### 1. USERS

Stores user account information and authentication credentials.

**Columns:**

| Column              | Type         | Constraints                         | Description                            |
| ------------------- | ------------ | ----------------------------------- | -------------------------------------- |
| id                  | INTEGER      | PRIMARY KEY, AUTO_INCREMENT         | Unique user identifier                 |
| first_name          | VARCHAR(50)  | NOT NULL                            | User's first name                      |
| last_name           | VARCHAR(50)  | NOT NULL                            | User's last name                       |
| email               | VARCHAR(255) | NOT NULL, UNIQUE                    | User's email (login)                   |
| password            | VARCHAR(255) | NOT NULL                            | Bcrypt hashed password                 |
| phone_number        | VARCHAR(20)  | NULL                                | International format (+1234567890)     |
| roles               | JSON         | NOT NULL                            | Array of user roles                    |
| gender              | VARCHAR(20)  | NOT NULL                            | male, female, prefer_not_to_say, other |
| date_of_birth       | DATETIME     | NULL                                | User's birth date                      |
| profile_picture_url | VARCHAR(500) | NULL                                | URL to profile image                   |
| bio                 | TEXT         | NULL                                | User biography (max 500 chars)         |
| is_active           | BOOLEAN      | NOT NULL, DEFAULT TRUE              | Account active status                  |
| joined_at           | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Registration date                      |
| last_login          | DATETIME     | NULL                                | Last successful login                  |

**Indexes:**

- `idx_users_email` (UNIQUE) on `email`
- `idx_users_is_active` on `is_active`
- `idx_users_joined_at` on `joined_at`

**Sample Data:**

```sql
INSERT INTO users (first_name, last_name, email, password, roles, gender, is_active, joined_at)
VALUES ('John', 'Doe', 'john@example.com', '$2b$12$...', '["common_user"]', 'male', true, CURRENT_TIMESTAMP);
```

---

### 2. USER_SESSIONS (Redis-based)

Session information stored in Redis for fast access and automatic expiration.

**Structure (Redis Hash):**

```
Key: session:{session_id}
Fields:
  - user_id: INTEGER
  - refresh_token: STRING
  - device_info: STRING
  - ip_address: STRING
  - user_agent: STRING
  - created_at: TIMESTAMP
  - expires_at: TIMESTAMP
  - last_activity: TIMESTAMP
TTL: 90 days (configurable)
```

**Additional Indexes:**

- Set: `user_sessions:{user_id}` - List of all session IDs for a user

---

### 3. RECIPES

Main table storing recipe information.

**Columns:**

| Column            | Type         | Constraints                         | Description                    |
| ----------------- | ------------ | ----------------------------------- | ------------------------------ |
| id                | INTEGER      | PRIMARY KEY, AUTO_INCREMENT         | Unique recipe identifier       |
| name              | VARCHAR(200) | NOT NULL                            | Recipe name                    |
| author_id         | INTEGER      | NOT NULL, FK(users.id)              | Recipe creator                 |
| description       | TEXT         | NULL                                | Detailed description           |
| difficulty        | VARCHAR(20)  | NOT NULL                            | easy, medium, hard             |
| cuisine           | VARCHAR(50)  | NOT NULL                            | Cuisine type                   |
| servings          | INTEGER      | NOT NULL, CHECK(servings > 0)       | Number of servings             |
| serving_size      | VARCHAR(100) | NULL                                | Serving size description       |
| prep_time_minutes | INTEGER      | NOT NULL, CHECK(prep_time >= 0)     | Preparation time               |
| cook_time_minutes | INTEGER      | NOT NULL, CHECK(cook_time >= 0)     | Cooking time                   |
| rest_time_minutes | INTEGER      | NOT NULL, CHECK(rest_time >= 0)     | Resting time                   |
| calories          | INTEGER      | NULL                                | Calories per serving           |
| protein_g         | DECIMAL(8,2) | NULL                                | Protein in grams               |
| carbs_g           | DECIMAL(8,2) | NULL                                | Carbohydrates in grams         |
| fat_g             | DECIMAL(8,2) | NULL                                | Fat in grams                   |
| fiber_g           | DECIMAL(8,2) | NULL                                | Fiber in grams                 |
| sodium_mg         | DECIMAL(8,2) | NULL                                | Sodium in milligrams           |
| version           | INTEGER      | NOT NULL, DEFAULT 1                 | Version for optimistic locking |
| view_count        | INTEGER      | NOT NULL, DEFAULT 0                 | Number of views                |
| created_at        | DATETIME(TZ) | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp             |
| updated_at        | DATETIME(TZ) | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp          |
| deleted_at        | DATETIME(TZ) | NULL                                | Soft deletion timestamp        |

**Indexes:**

- `ix_recipes_id` on `id`
- `ix_recipes_name` on `name`
- `ix_recipes_author_id` on `author_id`
- `ix_recipes_difficulty` on `difficulty`
- `ix_recipes_cuisine` on `cuisine`
- `ix_recipes_created_at` on `created_at`
- `ix_recipes_deleted_at` on `deleted_at`
- `ix_recipes_view_count` on `view_count`
- `idx_recipes_author_created` on `(author_id, created_at)`
- `idx_recipes_difficulty_cuisine` on `(difficulty, cuisine)`
- `idx_recipes_deleted_at_created` on `(deleted_at, created_at)`

**Foreign Keys:**

- `author_id` REFERENCES `users(id)` ON DELETE CASCADE

**Check Constraints:**

- `check_servings_positive`: servings > 0
- `check_prep_time_non_negative`: prep_time_minutes >= 0
- `check_cook_time_non_negative`: cook_time_minutes >= 0
- `check_rest_time_non_negative`: rest_time_minutes >= 0
- `check_version_positive`: version > 0
- `check_view_count_non_negative`: view_count >= 0

---

### 4. INGREDIENTS

Recipe ingredients with quantities and dietary information.

**Columns:**

| Column         | Type          | Constraints                   | Description                  |
| -------------- | ------------- | ----------------------------- | ---------------------------- |
| id             | INTEGER       | PRIMARY KEY, AUTO_INCREMENT   | Unique ingredient ID         |
| recipe_id      | INTEGER       | NOT NULL, FK(recipes.id)      | Parent recipe                |
| name           | VARCHAR(100)  | NOT NULL                      | Ingredient name              |
| quantity_value | DECIMAL(10,3) | NOT NULL, CHECK(quantity > 0) | Quantity amount              |
| quantity_unit  | VARCHAR(50)   | NOT NULL                      | Unit (g, ml, cup, tsp, etc.) |
| is_optional    | BOOLEAN       | NOT NULL, DEFAULT FALSE       | Optional ingredient flag     |
| is_vegan       | BOOLEAN       | NOT NULL, DEFAULT FALSE       | Vegan-friendly flag          |
| is_vegetarian  | BOOLEAN       | NOT NULL, DEFAULT FALSE       | Vegetarian-friendly flag     |
| is_gluten_free | BOOLEAN       | NOT NULL, DEFAULT FALSE       | Gluten-free flag             |
| is_dairy_free  | BOOLEAN       | NOT NULL, DEFAULT FALSE       | Dairy-free flag              |
| allergens      | JSON          | NOT NULL, DEFAULT []          | Array of allergen strings    |
| substitutes    | JSON          | NOT NULL, DEFAULT []          | Array of substitute strings  |

**Indexes:**

- `ix_ingredients_id` on `id`
- `ix_ingredients_recipe_id` on `recipe_id`
- `ix_ingredients_name` on `name`
- `idx_ingredients_recipe_name` on `(recipe_id, name)`
- `idx_ingredients_dietary` on `(is_vegan, is_vegetarian, is_gluten_free)`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE

**Check Constraints:**

- `check_quantity_positive`: quantity_value > 0

---

### 5. RECIPE_STEPS

Sequential cooking instructions for recipes.

**Columns:**

| Column           | Type         | Constraints                      | Description              |
| ---------------- | ------------ | -------------------------------- | ------------------------ |
| id               | INTEGER      | PRIMARY KEY, AUTO_INCREMENT      | Unique step ID           |
| recipe_id        | INTEGER      | NOT NULL, FK(recipes.id)         | Parent recipe            |
| step_number      | INTEGER      | NOT NULL, CHECK(step_number > 0) | Sequential step number   |
| description      | TEXT         | NOT NULL                         | Step instructions        |
| duration_minutes | INTEGER      | NULL, CHECK(duration >= 0)       | Time for this step       |
| technique        | VARCHAR(100) | NULL                             | Cooking technique        |
| temperature      | VARCHAR(50)  | NULL                             | Temperature setting      |
| ingredients_used | JSON         | NOT NULL, DEFAULT []             | Ingredients used in step |

**Indexes:**

- `ix_recipe_steps_id` on `id`
- `ix_recipe_steps_recipe_id` on `recipe_id`
- `idx_steps_recipe_number` on `(recipe_id, step_number)`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE

**Unique Constraints:**

- `uq_recipe_step_number` on `(recipe_id, step_number)`

**Check Constraints:**

- `check_step_number_positive`: step_number > 0
- `check_duration_non_negative`: duration_minutes IS NULL OR duration_minutes >= 0

---

### 6. RECIPE_MEAL_TYPES

Many-to-many relationship between recipes and meal types.

**Columns:**

| Column    | Type        | Constraints                 | Description                              |
| --------- | ----------- | --------------------------- | ---------------------------------------- |
| id        | INTEGER     | PRIMARY KEY, AUTO_INCREMENT | Unique ID                                |
| recipe_id | INTEGER     | NOT NULL, FK(recipes.id)    | Recipe reference                         |
| meal_type | VARCHAR(20) | NOT NULL                    | breakfast, lunch, dinner, snack, dessert |

**Indexes:**

- `ix_recipe_meal_types_id` on `id`
- `ix_recipe_meal_types_recipe_id` on `recipe_id`
- `idx_meal_types_type_recipe` on `(meal_type, recipe_id)`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE

**Unique Constraints:**

- `uq_recipe_meal_type` on `(recipe_id, meal_type)`

---

### 7. TAGS

Reusable tags for categorizing recipes.

**Columns:**

| Column      | Type         | Constraints                         | Description          |
| ----------- | ------------ | ----------------------------------- | -------------------- |
| id          | INTEGER      | PRIMARY KEY, AUTO_INCREMENT         | Unique tag ID        |
| name        | VARCHAR(50)  | NOT NULL, UNIQUE                    | Tag name (lowercase) |
| description | VARCHAR(200) | NULL                                | Tag description      |
| created_at  | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp   |

**Indexes:**

- `ix_tags_id` on `id`
- `ix_tags_name` (UNIQUE) on `name`

---

### 8. RECIPE_TAGS

Many-to-many relationship between recipes and tags.

**Columns:**

| Column    | Type    | Constraints              | Description      |
| --------- | ------- | ------------------------ | ---------------- |
| recipe_id | INTEGER | NOT NULL, FK(recipes.id) | Recipe reference |
| tag_id    | INTEGER | NOT NULL, FK(tags.id)    | Tag reference    |

**Primary Key:**

- Composite: `(recipe_id, tag_id)`

**Indexes:**

- `idx_recipe_tags_recipe_id` on `recipe_id`
- `idx_recipe_tags_tag_id` on `tag_id`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE
- `tag_id` REFERENCES `tags(id)` ON DELETE CASCADE

---

### 9. RECIPE_FAVORITES

Many-to-many relationship tracking user favorite recipes.

**Columns:**

| Column       | Type         | Constraints                         | Description      |
| ------------ | ------------ | ----------------------------------- | ---------------- |
| recipe_id    | INTEGER      | NOT NULL, FK(recipes.id)            | Recipe reference |
| user_id      | INTEGER      | NOT NULL, FK(users.id)              | User reference   |
| favorited_at | DATETIME(TZ) | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When favorited   |

**Primary Key:**

- Composite: `(recipe_id, user_id)`

**Indexes:**

- `idx_recipe_favorites_recipe_id` on `recipe_id`
- `idx_recipe_favorites_user_id` on `user_id`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

---

### 10. RECIPE_REVIEWS

User ratings and comments for recipes.

**Columns:**

| Column      | Type         | Constraints                                  | Description          |
| ----------- | ------------ | -------------------------------------------- | -------------------- |
| recipe_id   | INTEGER      | NOT NULL, FK(recipes.id)                     | Recipe reference     |
| user_id     | INTEGER      | NOT NULL, FK(users.id)                       | User reference       |
| rating      | INTEGER      | NOT NULL, CHECK(rating >= 1 AND rating <= 5) | Star rating (1-5)    |
| comment     | TEXT         | NULL                                         | Optional review text |
| reviewed_at | DATETIME(TZ) | NOT NULL, DEFAULT CURRENT_TIMESTAMP          | Review timestamp     |

**Primary Key:**

- Composite: `(recipe_id, user_id)`

**Indexes:**

- `idx_recipe_reviews_recipe_id` on `recipe_id`
- `idx_recipe_reviews_user_id` on `user_id`

**Foreign Keys:**

- `recipe_id` REFERENCES `recipes(id)` ON DELETE CASCADE
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Check Constraints:**

- `check_rating_range`: rating >= 1 AND rating <= 5

---

## Indexes

### Performance-Critical Indexes

**Recipe Search:**

```sql
CREATE INDEX idx_recipes_difficulty_cuisine ON recipes(difficulty, cuisine);
CREATE INDEX idx_recipes_deleted_at_created ON recipes(deleted_at, created_at);
```

**User Recipes:**

```sql
CREATE INDEX idx_recipes_author_created ON recipes(author_id, created_at);
```

**Ingredient Filtering:**

```sql
CREATE INDEX idx_ingredients_dietary ON ingredients(is_vegan, is_vegetarian, is_gluten_free);
```

**Full-Text Search (PostgreSQL):**

```sql
CREATE INDEX idx_recipes_name_fts ON recipes USING gin(to_tsvector('english', name));
```

---

## Constraints

### Foreign Key Constraints

All foreign keys use `ON DELETE CASCADE` to maintain referential integrity:

```sql
-- When a user is deleted, all their recipes are deleted
ALTER TABLE recipes ADD CONSTRAINT fk_recipe_author
  FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE;

-- When a recipe is deleted, all related data is deleted
ALTER TABLE ingredients ADD CONSTRAINT fk_ingredient_recipe
  FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE;
```

### Check Constraints

Ensure data validity at the database level:

```sql
-- Positive values
ALTER TABLE recipes ADD CONSTRAINT check_servings_positive
  CHECK (servings > 0);

-- Non-negative values
ALTER TABLE recipes ADD CONSTRAINT check_view_count_non_negative
  CHECK (view_count >= 0);

-- Range constraints
ALTER TABLE recipe_reviews ADD CONSTRAINT check_rating_range
  CHECK (rating >= 1 AND rating <= 5);
```

### Unique Constraints

Prevent duplicate data:

```sql
-- User emails must be unique
ALTER TABLE users ADD CONSTRAINT uq_user_email UNIQUE (email);

-- Tag names must be unique
ALTER TABLE tags ADD CONSTRAINT uq_tag_name UNIQUE (name);

-- One step number per recipe
ALTER TABLE recipe_steps ADD CONSTRAINT uq_recipe_step_number
  UNIQUE (recipe_id, step_number);
```

---

## Migrations

### Alembic Configuration

**Configuration File:** `alembic.ini`

**Migration Directory:** `alembic/versions/`

### Common Migration Commands

```bash
# Create a new migration
alembic revision -m "description"

# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current

# Stamp database without running migrations
alembic stamp head
```

### Initial Migration

**File:** `c3b924712e7d_inital_migration_create_tables.py`

Creates all base tables with proper indexes and constraints.

### Migration Best Practices

1. **Always review auto-generated migrations** - Alembic may miss some details
2. **Test migrations on a copy of production data** - Before deploying
3. **Include both upgrade() and downgrade()** - Allow rollbacks
4. **Make migrations idempotent** - Can be run multiple times safely
5. **Use batch operations** - For large table alterations
6. **Add indexes in separate migrations** - For large datasets

---

## Database Optimization

### Connection Pooling

```python
# config/sql_session.py
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30.0
```

### Query Optimization Tips

1. **Use selective loading** - Only fetch needed columns
2. **Batch operations** - Use bulk inserts/updates
3. **Pagination** - Always paginate large result sets
4. **Eager loading** - Use `selectinload()` for relationships
5. **Query result caching** - Cache frequently accessed data in Redis

### Monitoring Queries

Enable SQL echo in development:

```python
DB_ECHO=True  # Logs all SQL queries
```

---

## Backup & Recovery

### SQLite Backup

```bash
# Backup
sqlite3 cooking_app.db ".backup 'backup.db'"

# Restore
cp backup.db cooking_app.db
```

### PostgreSQL Backup

```bash
# Backup
pg_dump -U user -d cooking_db > backup.sql

# Restore
psql -U user -d cooking_db < backup.sql
```

---

## Data Seeding

### Demo Data

**File:** `alembic/demo_data.sql`

Contains sample data for development and testing:

- Sample users
- Sample recipes with ingredients and steps
- Tags
- Reviews and favorites

**Load Demo Data:**

```bash
sqlite3 cooking_app.db < alembic/demo_data.sql
```

---

**Last Updated:** November 2025
**Schema Version:** 1.0.0
