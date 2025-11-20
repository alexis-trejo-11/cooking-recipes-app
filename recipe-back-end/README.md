# Cooking Recipe API - Backend

A comprehensive, production-ready REST API for managing cooking recipes built with FastAPI, following Domain-Driven Design (DDD) principles and Clean Architecture.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Authentication & Security](#authentication--security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 Overview

The Cooking Recipe API is a sophisticated backend system designed to handle comprehensive recipe management, user authentication, social features, and advanced search capabilities. Built with enterprise-grade patterns and best practices, it provides a robust foundation for recipe-sharing applications.

### Key Features

#### Recipe Management

- **Complete CRUD Operations**: Create, read, update, and delete recipes with rich metadata
- **Advanced Search & Filtering**: Search by name, cuisine, difficulty, ingredients, tags, cooking time, and ratings
- **Featured Recipes**: Curated collection of highlighted recipes
- **Soft Deletion**: Recipes can be deleted and restored without data loss
- **Version Control**: Track recipe modifications with versioning
- **View Analytics**: Automatic tracking of recipe views

#### User Features

- **User Authentication**: Secure JWT-based authentication with refresh tokens
- **Profile Management**: Comprehensive user profiles with customizable information
- **Favorites System**: Save and manage favorite recipes
- **Recipe Reviews**: Rate and comment on recipes (1-5 stars)
- **User Recipes**: Manage personal recipe collections

#### Advanced Capabilities

- **Pagination**: Efficient data handling with configurable page sizes
- **Rate Limiting**: Redis-based rate limiting with configurable tiers
- **CORS Support**: Configured for frontend integration
- **SSL/HTTPS Support**: Optional secure connections
- **Structured Logging**: Comprehensive logging with color-coded console output
- **Health Checks**: Built-in health monitoring endpoints
- **Global Exception Handling**: Centralized error management with detailed responses

## 🚀 Technology Stack

### Core Framework

- **[FastAPI 0.104.1](https://fastapi.tiangolo.com/)** - Modern, high-performance web framework
- **[Uvicorn 0.24.0](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[Python 3.11+](https://www.python.org/)** - Latest Python features and performance

### Database & ORM

- **[SQLAlchemy 2.0.23](https://www.sqlalchemy.org/)** - Powerful async ORM
- **[Alembic 1.12.1](https://alembic.sqlalchemy.org/)** - Database migration tool
- **[aiosqlite 0.19.0](https://aiosqlite.omnilib.dev/)** - Async SQLite driver

### Validation & Settings

- **[Pydantic 2.5.0](https://docs.pydantic.dev/)** - Data validation using Python type hints
- **[Pydantic Settings 2.1.0](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Settings management
- **[Email Validator 2.1.0](https://github.com/JoshData/python-email-validator)** - Email validation

### Caching & Performance

- **[Redis 5.0.1](https://redis.io/)** - In-memory data store for caching and rate limiting
- **[aioredis 2.0.1](https://aioredis.readthedocs.io/)** - Async Redis client

### Security & Authentication

- **[PyJWT 2.8.0](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation
- **[bcrypt 4.1.2](https://github.com/pyca/bcrypt/)** - Password hashing

### Development & Testing

- **[pytest 7.4.3](https://pytest.org/)** - Testing framework
- **[pytest-asyncio 0.21.1](https://pytest-asyncio.readthedocs.io/)** - Async test support
- **[httpx 0.25.2](https://www.python-httpx.org/)** - Async HTTP client for testing

### Additional Tools

- **[python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)** - Environment variable management
- **[colorlog](https://github.com/borntyping/python-colorlog)** - Colored logging output
- **[python-multipart 0.0.6](https://andrew-d.github.io/python-multipart/)** - Multipart form data parser

## 🏗️ Architecture

This project implements **Clean Architecture** with **Domain-Driven Design (DDD)** principles, ensuring separation of concerns, maintainability, and testability.

### Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (Controllers, Dependencies, Request/Response DTOs)          │
│  • FastAPI Routers                                          │
│  • Request Validation                                       │
│  • Response Serialization                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Application Layer                          │
│  (Use Cases, Application DTOs, Business Workflows)           │
│  • Use Case Implementation                                  │
│  • Application Services                                     │
│  • DTO Transformations                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     Domain Layer                             │
│  (Entities, Value Objects, Domain Services, Specifications)  │
│  • Business Logic                                           │
│  • Domain Rules                                             │
│  • Entity Behaviors                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (Repositories, External Services, Database, Redis)          │
│  • Data Persistence                                         │
│  • External Integrations                                    │
│  • Technical Implementations                                │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### Repository Pattern

Abstracts data access logic and provides a collection-like interface for accessing domain entities.

```python
# Domain Interface
class IUserRepository(Protocol):
    async def add(self, user: User) -> User: ...
    async def find_by_id(self, user_id: UserId) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...
```

#### Specification Pattern

Encapsulates query logic in reusable, composable specifications.

```python
class RecipeByDifficultySpec(Specification[Recipe]):
    def __init__(self, difficulty: DifficultyLevel):
        self.difficulty = difficulty

    def to_sql_filter(self, model):
        return model.difficulty == self.difficulty.value
```

#### Use Case Pattern

Each business operation is encapsulated in a dedicated use case class.

```python
class CreateRecipeUseCase:
    async def execute(
        self,
        request: CreateRecipeRequest,
        author_id: UserId
    ) -> RecipeCreatedResponse:
        # Business logic here
```

#### Value Objects

Encapsulates related data and behavior, ensuring immutability and validation.

```python
@dataclass(frozen=True)
class CookingTime:
    prep_minutes: int
    cook_minutes: int
    rest_minutes: int

    @property
    def total_minutes(self) -> int:
        return self.prep_minutes + self.cook_minutes + self.rest_minutes
```

## 📁 Project Structure

```
recipe-back-end/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Multi-container orchestration
├── start.sh                     # Startup script with migrations
├── alembic.ini                  # Database migration config
├── pytest.ini                   # Test configuration
├── .env                         # Environment variables
│
├── alembic/                     # Database migrations
│   ├── versions/                # Migration scripts
│   ├── env.py                   # Migration environment
│   └── demo_data.sql            # Sample data
│
├── app/                         # Main application package
│   ├── __init__.py
│   │
│   ├── config/                  # Configuration modules
│   │   ├── app_settings.py      # Application settings (Pydantic)
│   │   ├── sql_session.py       # Database session management
│   │   ├── redis_config.py      # Redis connection setup
│   │   ├── rate_limiter.py      # Rate limiting configuration
│   │   ├── logging_config.py    # Logging setup
│   │   └── global_exception_handler.py  # Exception handling
│   │
│   ├── modules/                 # Feature modules (DDD bounded contexts)
│   │   │
│   │   ├── auth/                # Authentication & User Management
│   │   │   ├── domain/          # Domain layer
│   │   │   │   ├── user.py              # User entity & value objects
│   │   │   │   ├── session.py           # Session entity
│   │   │   │   ├── interfaces.py        # Repository interfaces
│   │   │   │   └── exceptions.py        # Domain exceptions
│   │   │   │
│   │   │   ├── application/     # Application layer
│   │   │   │   ├── auth_use_cases.py    # Authentication use cases
│   │   │   │   ├── user_use_cases.py    # User management use cases
│   │   │   │   ├── dtos.py              # Data transfer objects
│   │   │   │   └── exceptions.py        # Application exceptions
│   │   │   │
│   │   │   ├── infrastructure/  # Infrastructure layer
│   │   │   │   ├── persistence/         # Database repositories
│   │   │   │   ├── services/            # External services (JWT, password)
│   │   │   │   ├── middleware/          # Auth middleware
│   │   │   │   └── mocks/               # Test doubles
│   │   │   │
│   │   │   └── presentation/    # Presentation layer
│   │   │       ├── auth_controller.py   # Auth endpoints
│   │   │       ├── user_controller.py   # User endpoints
│   │   │       ├── auth_dependencies.py # Dependency injection
│   │   │       └── app_dependencies.py  # Application dependencies
│   │   │
│   │   └── recipe/              # Recipe Management
│   │       ├── domain/          # Domain layer
│   │       │   ├── models/
│   │       │   │   ├── entities/        # Domain entities
│   │       │   │   │   ├── recipe.py
│   │       │   │   │   ├── ingredient.py
│   │       │   │   │   └── review.py
│   │       │   │   └── value_objects/   # Value objects
│   │       │   │       ├── value_objects_standard.py
│   │       │   │       ├── value_objects_compound.py
│   │       │   │       ├── enums.py
│   │       │   │       └── param_dtos.py
│   │       │   ├── interfaces.py        # Repository interfaces
│   │       │   ├── specification.py     # Query specifications
│   │       │   └── exceptions.py        # Domain exceptions
│   │       │
│   │       ├── application/     # Application layer
│   │       │   ├── use_cases/           # Business use cases
│   │       │   ├── dtos.py              # Data transfer objects
│   │       │   └── exceptions.py        # Application exceptions
│   │       │
│   │       ├── infrastructure/  # Infrastructure layer
│   │       │   └── persistence/         # Database repositories
│   │       │
│   │       └── presentation/    # Presentation layer
│   │           ├── controller.py        # Recipe endpoints
│   │           └── dependencies.py      # Dependency injection
│   │
│   └── utils/                   # Shared utilities
│       ├── core/                # Core utilities
│       │   ├── pagination.py    # Pagination logic
│       │   ├── specification.py # Specification base
│       │   └── exceptions/      # Custom exceptions
│       └── external/            # External integrations
│           └── page_request.py  # Pagination DTOs
│
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── test_user_domain.py
│   │   └── test_recipe_domain.py
│   ├── application/             # Use case tests
│   │   └── test_auth_use_cases.py
│   ├── infrastructure/          # Repository tests
│   │   ├── test_sqlalchemy_repository.py
│   │   └── test_recipe_repository.py
│   └── controller/              # Integration tests
│       └── test_auth_controller.py
│
└── logs/                        # Application logs (generated)
```

## 🚦 Getting Started

### Prerequisites

- **Python 3.11+** installed
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Redis** (optional, for rate limiting and caching)

### Installation

#### Option 1: Local Development

1. **Clone the repository**

```bash
cd recipe-back-end
```

2. **Create and activate virtual environment**

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**

```bash
alembic upgrade head
```

6. **Start the development server**

```bash
python main.py
```

The API will be available at:

- **HTTP**: `http://localhost:8080`
- **HTTPS**: `https://localhost:8443` (if SSL enabled)
- **API Documentation**: `http://localhost:8080/docs`
- **Alternative Docs**: `http://localhost:8080/redoc`

#### Option 2: Docker Deployment

1. **Build and start containers**

```bash
docker-compose up -d --build
```

2. **Check container status**

```bash
docker-compose ps
```

3. **View logs**

```bash
docker-compose logs -f backend
```

4. **Stop containers**

```bash
docker-compose down
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./cooking_app.db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRES_DAYS=90

# Application Settings
DEBUG=False

# Rate Limiting
RATE_LIMIT_ENABLED=True
DEFAULT_RATE_LIMIT=default

# SSL/HTTPS Configuration (Optional)
SSL_ENABLED=False
SSL_KEYFILE=key.pem
SSL_CERTFILE=cert.pem
SERVER_PORT=8080
SSL_PORT=8443

# Database Connection Pool
DB_ECHO=False
DB_POOL_SIZE=10
DB_TIMEOUT=5.0
```

### SSL Certificate Generation (Optional)

To enable HTTPS:

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update .env
SSL_ENABLED=True
SSL_KEYFILE=key.pem
SSL_CERTFILE=cert.pem
```

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

### API Overview

See [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) for detailed endpoint documentation.

#### Authentication Endpoints

| Method | Endpoint               | Description          | Auth Required |
| ------ | ---------------------- | -------------------- | ------------- |
| POST   | `/api/v1/auth/signup`  | Register new user    | No            |
| POST   | `/api/v1/auth/login`   | User login           | No            |
| POST   | `/api/v1/auth/refresh` | Refresh access token | No            |
| POST   | `/api/v1/auth/logout`  | Logout user          | No            |
| GET    | `/api/v1/auth/me`      | Get current user     | Yes           |

#### User Endpoints

| Method | Endpoint                     | Description          | Auth Required |
| ------ | ---------------------------- | -------------------- | ------------- |
| GET    | `/api/v1/users/profile`      | Get user profile     | Yes           |
| PUT    | `/api/v1/users/profile`      | Update profile       | Yes           |
| GET    | `/api/v1/users/recipes/favs` | Get favorite recipes | Yes           |

#### Recipe Endpoints

| Method | Endpoint                                | Description            | Auth Required |
| ------ | --------------------------------------- | ---------------------- | ------------- |
| GET    | `/api/v1/recipes/featured`              | Get featured recipes   | No            |
| GET    | `/api/v1/recipes`                       | Search recipes         | No            |
| GET    | `/api/v1/recipes/{id}`                  | Get recipe details     | No            |
| POST   | `/api/v1/recipes`                       | Create recipe          | Yes           |
| PUT    | `/api/v1/recipes/{id}`                  | Update recipe          | Yes           |
| DELETE | `/api/v1/recipes/{id}`                  | Delete recipe          | Yes           |
| POST   | `/api/v1/recipes/{id}/restore`          | Restore deleted recipe | Yes           |
| GET    | `/api/v1/recipes/my`                    | Get user's recipes     | Yes           |
| GET    | `/api/v1/recipes/my/favorites`          | Get user favorites     | Yes           |
| GET    | `/api/v1/recipes/is_favorite/{id}`      | Check favorite status  | Yes           |
| PATCH  | `/api/v1/recipes/{id}/favorites/toggle` | Toggle favorite        | Yes           |
| POST   | `/api/v1/recipes/{id}/ratings`          | Add review             | Yes           |
| DELETE | `/api/v1/recipes/{id}/ratings`          | Delete review          | Yes           |

### Request/Response Examples

See [API_EXAMPLES.md](docs/API_EXAMPLES.md) for detailed examples of all endpoints.

#### Example: User Registration

**Request:**

```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "SecureP@ss123!",
  "phone_number": "+1234567890",
  "gender": "male",
  "date_of_birth": "1990-01-15"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123"
}
```

#### Example: Create Recipe

**Request:**

```http
POST /api/v1/recipes
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Classic Spaghetti Carbonara",
  "description": "Traditional Italian pasta dish",
  "difficulty": "medium",
  "cuisine": "italian",
  "meal_types": ["lunch", "dinner"],
  "servings": 4,
  "serving_size": "1 plate",
  "prep_time_minutes": 10,
  "cook_time_minutes": 20,
  "rest_time_minutes": 0,
  "ingredients": [
    {
      "name": "Spaghetti",
      "quantity_value": 400,
      "quantity_unit": "g",
      "is_optional": false
    }
  ],
  "steps": [
    {
      "step_number": 1,
      "description": "Boil water and cook pasta",
      "duration_minutes": 10
    }
  ],
  "tags": ["pasta", "italian", "quick"],
  "nutritional_info": {
    "calories": 450,
    "protein_g": 20,
    "carbs_g": 65,
    "fat_g": 15
  }
}
```

## 🗄️ Database Schema

See [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for detailed schema documentation.

### Entity Relationship Diagram

```
┌─────────────┐           ┌──────────────┐
│    Users    │───────────│   Sessions   │
│             │ 1       * │              │
│ - id (PK)   │           │ - session_id │
│ - email     │           │ - user_id    │
│ - password  │           │ - token      │
│ - roles     │           └──────────────┘
└──────┬──────┘
       │
       │ 1
       │
       │ *
┌──────▼──────────────┐
│      Recipes        │
│                     │
│ - id (PK)           │
│ - name              │
│ - author_id (FK)    │
│ - difficulty        │
│ - cuisine           │
│ - description       │
│ - version           │
│ - view_count        │
│ - created_at        │
│ - updated_at        │
│ - deleted_at        │
└──────┬──────────────┘
       │
       ├──────────┬──────────┬──────────┬──────────┬──────────┐
       │ 1        │ 1        │ 1        │ *        │ *        │
       │ *        │ *        │ *        │ *        │ *        │
       │          │          │          │          │          │
┌──────▼─────┐ ┌─▼────────┐ ┌▼────────┐ ┌▼────────┐ ┌▼────────┐
│Ingredients │ │  Steps   │ │MealTypes│ │Favorites│ │ Reviews │
│            │ │          │ │         │ │         │ │         │
│- id (PK)   │ │- id (PK) │ │- recipe │ │- recipe │ │- recipe │
│- recipe_id │ │- recipe  │ │- meal   │ │- user   │ │- user   │
│- name      │ │- number  │ │         │ │- date   │ │- rating │
│- quantity  │ │- desc    │ └─────────┘ └─────────┘ │- comment│
│- unit      │ │- duration│                          └─────────┘
│- optional  │ └──────────┘
└────────────┘
```

### Key Tables

#### Users Table

Stores user account information with authentication credentials and profile data.

#### Recipes Table

Core recipe information including metadata, cooking details, and tracking information.

#### Ingredients Table

Recipe ingredients with quantities, units, and dietary information.

#### Recipe Steps Table

Sequential cooking instructions with optional timing and technique details.

#### Recipe Favorites Table

Many-to-many relationship tracking user favorite recipes.

#### Recipe Reviews Table

User ratings and comments for recipes.

## 🔐 Authentication & Security

### JWT-Based Authentication

The API uses **JSON Web Tokens (JWT)** for stateless authentication with a two-token strategy:

#### Access Tokens

- **Purpose**: Authorize API requests
- **Lifetime**: 30 minutes (configurable)
- **Storage**: Client memory or secure storage
- **Claims**: `user_id`, `email`, `roles`, `exp`, `iat`

#### Refresh Tokens

- **Purpose**: Obtain new access tokens
- **Lifetime**: 90 days (configurable)
- **Storage**: Redis with session tracking
- **Claims**: `user_id`, `session_id`, `exp`, `iat`

### Authentication Flow

```
┌─────────┐                          ┌─────────┐
│ Client  │                          │   API   │
└────┬────┘                          └────┬────┘
     │                                    │
     │  1. POST /auth/login               │
     ├───────────────────────────────────>│
     │  (email, password)                 │
     │                                    │
     │  2. Validate credentials           │
     │     Create session in Redis        │
     │     Generate tokens                │
     │<───────────────────────────────────┤
     │  (access_token, refresh_token)     │
     │                                    │
     │  3. GET /recipes                   │
     ├───────────────────────────────────>│
     │  Authorization: Bearer <access>    │
     │                                    │
     │  4. Validate token & return data   │
     │<───────────────────────────────────┤
     │                                    │
     │  5. Access token expires           │
     │  POST /auth/refresh                │
     ├───────────────────────────────────>│
     │  (refresh_token)                   │
     │                                    │
     │  6. Validate session in Redis      │
     │     Generate new access token      │
     │<───────────────────────────────────┤
     │  (new access_token)                │
     │                                    │
     │  7. POST /auth/logout              │
     ├───────────────────────────────────>│
     │  (refresh_token)                   │
     │                                    │
     │  8. Delete session from Redis      │
     │<───────────────────────────────────┤
     │  (success)                         │
     │                                    │
```

### Password Security

- **Hashing**: Bcrypt with salt rounds
- **Validation**: Minimum 8 characters, uppercase, lowercase, number, special character
- **Storage**: Never stored in plain text
- **Transmission**: Always over HTTPS in production

### Rate Limiting

Redis-based rate limiting with multiple tiers:

| Tier          | Requests | Window | Use Case                          |
| ------------- | -------- | ------ | --------------------------------- |
| **public**    | 100      | 60s    | Public endpoints (search, browse) |
| **generous**  | 60       | 60s    | Authenticated users               |
| **moderate**  | 30       | 60s    | Token refresh operations          |
| **strict**    | 10       | 60s    | Login/signup endpoints            |
| **sensitive** | 20       | 60s    | Create/update operations          |

Rate limits are enforced per IP address and return `429 Too Many Requests` when exceeded.

### CORS Configuration

Configured for frontend integration with allowed origins:

- `http://localhost:4200` (Angular dev server)
- `https://localhost:4200` (Angular dev server HTTPS)

### Security Headers

- Content Security Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

## 🧪 Testing

The project includes comprehensive test coverage across all layers.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_domain.py

# Run specific test
pytest tests/unit/test_user_domain.py::test_create_user_success

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/controller/
```

### Test Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── unit/                        # Domain & entity tests
│   ├── test_user_domain.py
│   └── test_recipe_domain.py
├── application/                 # Use case tests
│   └── test_auth_use_cases.py
├── infrastructure/              # Repository tests
│   ├── test_sqlalchemy_repository.py
│   └── test_recipe_repository.py
└── controller/                  # Integration tests
    └── test_auth_controller.py
```

### Test Coverage Goals

- **Domain Layer**: 95%+
- **Application Layer**: 90%+
- **Infrastructure Layer**: 80%+
- **Overall**: 85%+

## 🚀 Deployment

### Docker Deployment

The application is Docker-ready with optimized production settings.

#### Build Image

```bash
docker build -t recipe-api:latest .
```

#### Run Container

```bash
docker run -d \
  --name recipe-api \
  -p 8080:8080 \
  -p 8443:8443 \
  -e DEBUG=false \
  -e DATABASE_URL=sqlite+aiosqlite:///./cooking_app.db \
  -e JWT_SECRET_KEY=your-secret-key \
  -v $(pwd)/cooking_app.db:/app/cooking_app.db \
  -v $(pwd)/logs:/app/logs \
  recipe-api:latest
```

#### Docker Compose

```bash
# Start services
docker-compose up -d

# Scale application
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

#### Environment Variables

```bash
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
JWT_SECRET_KEY=<strong-random-key>
RATE_LIMIT_ENABLED=True
SSL_ENABLED=True
```

#### Database Migration

```bash
# Upgrade to latest
alembic upgrade head

# Rollback one revision
alembic downgrade -1

# View migration history
alembic history

# Create new migration
alembic revision -m "description"
```

#### Health Checks

```bash
# Application health
curl http://localhost:8080/health

# Rate limit status
curl http://localhost:8080/admin/rate-limit-status
```

#### Logging

Logs are written to:

- **Console**: Color-coded output with log levels
- **File**: `logs/app.log` (rotated daily)

Log levels:

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Performance Optimization

#### Database Connection Pooling

```python
DB_POOL_SIZE=20
DB_TIMEOUT=30.0
```

#### Redis Caching

- Session storage
- Rate limit counters
- Query result caching

#### Async Operations

All database operations use async/await for non-blocking I/O.

## 📖 Additional Documentation

- **[API Endpoints](docs/API_ENDPOINTS.md)** - Complete API reference
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Detailed schema documentation
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Deep dive into architecture
- **[Development Guide](docs/DEVELOPMENT.md)** - Development best practices
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment strategies

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for classes and methods
- Maintain test coverage above 85%

### Commit Messages

Follow conventional commits:

- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `test: Add tests`
- `refactor: Code refactoring`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Project Team** - Initial work and ongoing maintenance

## 🙏 Acknowledgments

- FastAPI community for excellent documentation
- SQLAlchemy team for powerful ORM capabilities
- All contributors and users of this project

---

**Built with ❤️ using FastAPI and Clean Architecture principles**
