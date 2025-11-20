# Architecture Documentation

In-depth architectural overview of the Cooking Recipe API backend.

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Clean Architecture Layers](#clean-architecture-layers)
- [Domain-Driven Design](#domain-driven-design)
- [Design Patterns](#design-patterns)
- [Module Structure](#module-structure)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Performance Architecture](#performance-architecture)

## Architectural Overview

This project implements **Clean Architecture** principles combined with **Domain-Driven Design (DDD)** to create a maintainable, testable, and scalable backend system.

### Core Principles

1. **Independence of Frameworks** - Business logic doesn't depend on FastAPI
2. **Testability** - Business rules can be tested without UI, database, or external elements
3. **Independence of UI** - The UI can change without changing the business rules
4. **Independence of Database** - Business rules are not bound to the database
5. **Independence of External Agencies** - Business rules don't know about the outside world

### Architectural Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          External World                              │
│  (HTTP Clients, Web Browsers, Mobile Apps, External APIs)           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                        │   │
│  │  - Controllers (Routers)                                      │   │
│  │  - Request/Response Models (Pydantic)                         │   │
│  │  - Dependency Injection                                       │   │
│  │  - Authentication Middleware                                  │   │
│  │  - Exception Handlers                                         │   │
│  │  - Rate Limiters                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ DTOs (Data Transfer Objects)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      Use Cases                                │   │
│  │  - Business Workflows                                         │   │
│  │  - Orchestration Logic                                        │   │
│  │  - Application Services                                       │   │
│  │  - DTO Transformations                                        │   │
│  │  - Transaction Management                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Domain Entities & Value Objects
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Business Logic                              │   │
│  │  - Entities (Recipe, User, Ingredient)                        │   │
│  │  - Value Objects (RecipeId, CookingTime, Rating)             │   │
│  │  - Domain Services                                            │   │
│  │  - Domain Events                                              │   │
│  │  - Business Rules & Invariants                                │   │
│  │  - Specifications                                             │   │
│  │  - Repository Interfaces                                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Repository Implementations
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              External Dependencies                            │   │
│  │  - Database Repositories (SQLAlchemy)                         │   │
│  │  - External Services (JWT, Bcrypt, Redis)                     │   │
│  │  - ORM Models                                                 │   │
│  │  - Migrations (Alembic)                                       │   │
│  │  - Configuration                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Database (SQLite/   │
                  │   PostgreSQL)         │
                  └──────────────────────┘

                  ┌──────────────────────┐
                  │   Redis Cache        │
                  └──────────────────────┘
```

## Clean Architecture Layers

### 1. Presentation Layer (Outer Layer)

**Responsibility:** Handle HTTP communication, serialize/deserialize data, authentication.

**Components:**

- **Controllers (Routers):** Handle HTTP requests and responses
- **DTOs:** Request/Response models using Pydantic
- **Dependencies:** FastAPI dependency injection
- **Middleware:** CORS, authentication, rate limiting

**Example:**

```python
# presentation/auth_controller.py
@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignUpRequest,
    use_case: SignUpUseCaseDep,
) -> AuthResponse:
    result = await use_case.execute(request)
    return result
```

**Key Characteristics:**

- Knows about HTTP, JSON, status codes
- Transforms HTTP requests to DTOs
- Transforms use case results to HTTP responses
- No business logic
- Depends on Application Layer

---

### 2. Application Layer

**Responsibility:** Orchestrate business workflows, coordinate domain objects.

**Components:**

- **Use Cases:** Single-responsibility business operations
- **Application DTOs:** Data transfer between layers
- **Application Services:** Coordinate multiple use cases
- **Transaction Management:** Handle database transactions

**Example:**

```python
# application/auth_use_cases.py
class SignUpUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ):
        self._user_repo = user_repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, request: SignUpRequest) -> AuthResponse:
        # 1. Create domain entity
        user = User.create(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            raw_password=request.password,
            gender=request.gender,
        )

        # 2. Hash password
        hashed = await self._password_service.hash(request.password)
        user.set_hashed_password(hashed)

        # 3. Persist
        saved_user = await self._user_repo.add(user)

        # 4. Generate tokens
        tokens = await self._token_service.create_tokens(saved_user.id)

        return AuthResponse.from_tokens(tokens, saved_user.id)
```

**Key Characteristics:**

- Orchestrates domain objects
- No HTTP knowledge
- No database knowledge
- Pure business workflows
- Depends on Domain Layer

---

### 3. Domain Layer (Core)

**Responsibility:** Contains all business logic, entities, and rules.

**Components:**

- **Entities:** Objects with identity (User, Recipe)
- **Value Objects:** Immutable objects without identity (RecipeId, CookingTime)
- **Domain Services:** Business logic that doesn't fit in entities
- **Specifications:** Encapsulated query logic
- **Repository Interfaces:** Contracts for data access

**Example:**

```python
# domain/user.py
class User:
    """User entity with all business logic"""

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        raw_password: str,
        gender: UserGender,
    ) -> "User":
        # Business validation
        cls._validate_email(email)
        cls._validate_raw_password(raw_password)
        cls._validate_full_name(first_name, last_name)

        return cls(
            id=UserId.generate(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            password=raw_password,
            roles=[UserRole.COMMON_USER],
            gender=gender,
            joined_at=datetime.now(timezone.utc),
        )

    def update_email(self, new_email: str) -> None:
        """Business rule: Email must be valid"""
        self._validate_email(new_email)
        self._email = new_email.strip().lower()
```

**Key Characteristics:**

- No dependencies on outer layers
- Pure Python (no framework dependencies)
- Contains all business rules
- Highly testable
- Independent layer

---

### 4. Infrastructure Layer

**Responsibility:** Implement technical details, external dependencies.

**Components:**

- **Repositories:** SQLAlchemy implementations
- **ORM Models:** Database table mappings
- **External Services:** JWT, Bcrypt, Redis clients
- **Migrations:** Alembic scripts
- **Configuration:** Settings, database connections

**Example:**

```python
# infrastructure/persistence/user_repository.py
class SQLAlchemyUserRepository(IUserRepository):
    """Concrete implementation using SQLAlchemy"""

    async def add(self, user: User) -> User:
        # Convert domain entity to ORM model
        orm_user = UserORM(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            roles=[role.value for role in user.roles],
        )

        self._session.add(orm_user)
        await self._session.commit()

        # Convert back to domain entity
        return User.reconstruct({
            "id": UserId(orm_user.id),
            "first_name": orm_user.first_name,
            # ... other fields
        })
```

**Key Characteristics:**

- Implements repository interfaces
- Handles database operations
- Manages external service integrations
- Depends on Domain Layer (through interfaces)

---

## Domain-Driven Design

### Bounded Contexts

The application is divided into two main bounded contexts:

#### 1. Authentication Context (`auth` module)

**Purpose:** User management and authentication

**Entities:**

- `User` - User account with profile information
- `UserSession` - Active user session with tokens

**Value Objects:**

- `UserId` - Unique user identifier
- `UserRole` - User permission levels
- `UserGender` - Gender enumeration

**Aggregates:**

- `User` (aggregate root)

**Use Cases:**

- SignUpUseCase
- LoginUseCase
- RefreshTokenUseCase
- LogoutUseCase
- UpdateProfileUseCase

---

#### 2. Recipe Context (`recipe` module)

**Purpose:** Recipe management and social features

**Entities:**

- `Recipe` - Core recipe entity
- `Ingredient` - Recipe ingredient
- `Review` - User review with rating

**Value Objects:**

- `RecipeId` - Unique recipe identifier
- `CookingTime` - Prep/cook/rest times
- `ServingInfo` - Servings and serving size
- `NutritionalInfo` - Nutrition data
- `DifficultyLevel` - Recipe difficulty
- `CuisineType` - Cuisine category
- `MealType` - Meal category

**Aggregates:**

- `Recipe` (aggregate root containing ingredients, steps, tags)

**Use Cases:**

- CreateRecipeUseCase
- UpdateRecipeUseCase
- DeleteRecipeUseCase
- SearchRecipesUseCase
- ToggleFavoriteUseCase
- CreateReviewUseCase

---

### Ubiquitous Language

Key terms used consistently across the codebase:

| Term            | Definition                                                |
| --------------- | --------------------------------------------------------- |
| **Recipe**      | A complete cooking instruction with ingredients and steps |
| **Author**      | User who created the recipe                               |
| **Difficulty**  | Recipe complexity (easy, medium, hard)                    |
| **Cuisine**     | Type of cuisine (Italian, Mexican, etc.)                  |
| **Meal Type**   | When recipe is typically eaten (breakfast, lunch, etc.)   |
| **Ingredient**  | Component needed for the recipe                           |
| **Step**        | Sequential cooking instruction                            |
| **Review**      | User rating and comment for a recipe                      |
| **Favorite**    | Recipe saved by a user for later                          |
| **Tag**         | Categorization label for recipes                          |
| **Soft Delete** | Logical deletion (data remains in database)               |
| **Version**     | Recipe revision number (optimistic locking)               |

---

## Design Patterns

### 1. Repository Pattern

**Purpose:** Abstract data access logic

**Benefits:**

- Testability (mock repositories)
- Separation of concerns
- Database-agnostic domain layer

**Implementation:**

```python
# Domain layer defines interface
class IUserRepository(Protocol):
    async def add(self, user: User) -> User: ...
    async def find_by_id(self, user_id: UserId) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...
    async def update(self, user: User) -> User: ...
    async def delete(self, user_id: UserId) -> None: ...

# Infrastructure layer implements
class SQLAlchemyUserRepository(IUserRepository):
    # Concrete implementation using SQLAlchemy
```

---

### 2. Specification Pattern

**Purpose:** Encapsulate query logic in reusable, composable objects

**Benefits:**

- Reusable query components
- Composable with AND/OR/NOT
- Testable query logic

**Implementation:**

```python
class RecipeByDifficultySpec(Specification[Recipe]):
    def __init__(self, difficulty: DifficultyLevel):
        self.difficulty = difficulty

    def to_sql_filter(self, model):
        return model.difficulty == self.difficulty.value

class RecipeByCuisineSpec(Specification[Recipe]):
    def __init__(self, cuisine: CuisineType):
        self.cuisine = cuisine

    def to_sql_filter(self, model):
        return model.cuisine == self.cuisine.value

# Compose specifications
spec = RecipeByDifficultySpec(DifficultyLevel.EASY) & \
       RecipeByCuisineSpec(CuisineType.ITALIAN)
```

---

### 3. Use Case Pattern

**Purpose:** Encapsulate single business operation

**Benefits:**

- Single Responsibility Principle
- Clear business intent
- Easy to test
- Reusable workflows

**Structure:**

```python
class UseCase(ABC):
    @abstractmethod
    async def execute(self, request: RequestDTO) -> ResponseDTO:
        pass

class CreateRecipeUseCase(UseCase):
    async def execute(
        self,
        request: CreateRecipeRequest,
        author_id: UserId,
    ) -> RecipeCreatedResponse:
        # Single, focused business operation
```

---

### 4. Factory Pattern

**Purpose:** Encapsulate complex object creation

**Implementation:**

```python
class User:
    @classmethod
    def create(...) -> "User":
        # Factory method for new users

    @classmethod
    def reconstruct(...) -> "User":
        # Factory method for persistence reconstruction
```

---

### 5. Value Object Pattern

**Purpose:** Create immutable, self-validating objects

**Benefits:**

- Immutability ensures consistency
- Self-validation
- No primitive obsession

**Implementation:**

```python
@dataclass(frozen=True)  # Immutable
class CookingTime:
    prep_minutes: int
    cook_minutes: int
    rest_minutes: int

    def __post_init__(self):
        # Validation
        if self.prep_minutes < 0:
            raise ValueError("Prep time must be non-negative")

    @property
    def total_minutes(self) -> int:
        # Business logic
        return self.prep_minutes + self.cook_minutes + self.rest_minutes
```

---

### 6. Dependency Injection Pattern

**Purpose:** Invert dependencies, improve testability

**Implementation:**

```python
# FastAPI dependency injection
def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> IUserRepository:
    return SQLAlchemyUserRepository(session)

SignUpUseCaseDep = Annotated[SignUpUseCase, Depends(get_signup_use_case)]

@router.post("/signup")
async def signup(
    request: SignUpRequest,
    use_case: SignUpUseCaseDep,  # Injected
):
    return await use_case.execute(request)
```

---

### 7. Strategy Pattern

**Purpose:** Encapsulate algorithms, make them interchangeable

**Example:**

```python
class IPasswordService(Protocol):
    async def hash(self, password: str) -> str: ...
    async def verify(self, password: str, hashed: str) -> bool: ...

class BcryptPasswordService(IPasswordService):
    # Bcrypt implementation

class Argon2PasswordService(IPasswordService):
    # Argon2 implementation
```

---

## Module Structure

### Authentication Module (`app/modules/auth/`)

```
auth/
├── domain/                    # Business logic
│   ├── user.py               # User entity
│   ├── session.py            # Session entity
│   ├── interfaces.py         # Repository interfaces
│   └── exceptions.py         # Domain exceptions
│
├── application/              # Use cases
│   ├── auth_use_cases.py    # Authentication workflows
│   ├── user_use_cases.py    # User management workflows
│   ├── dtos.py              # Application DTOs
│   └── exceptions.py        # Application exceptions
│
├── infrastructure/           # Technical implementation
│   ├── persistence/         # Database repositories
│   ├── services/            # External services (JWT, bcrypt)
│   ├── middleware/          # Auth middleware
│   └── mocks/               # Test doubles
│
└── presentation/            # HTTP layer
    ├── auth_controller.py   # Auth endpoints
    ├── user_controller.py   # User endpoints
    ├── auth_dependencies.py # Auth dependencies
    └── app_dependencies.py  # Use case dependencies
```

---

### Recipe Module (`app/modules/recipe/`)

```
recipe/
├── domain/                        # Business logic
│   ├── models/
│   │   ├── entities/             # Domain entities
│   │   │   ├── recipe.py
│   │   │   ├── ingredient.py
│   │   │   └── review.py
│   │   └── value_objects/        # Value objects
│   │       ├── enums.py
│   │       ├── value_objects_standard.py
│   │       ├── value_objects_compound.py
│   │       └── param_dtos.py
│   ├── interfaces.py             # Repository interfaces
│   ├── specification.py          # Query specifications
│   └── exceptions.py             # Domain exceptions
│
├── application/                   # Use cases
│   ├── use_cases/                # Business workflows
│   ├── dtos.py                   # Application DTOs
│   └── exceptions.py             # Application exceptions
│
├── infrastructure/                # Technical implementation
│   └── persistence/              # Database repositories
│
└── presentation/                  # HTTP layer
    ├── controller.py             # Recipe endpoints
    └── dependencies.py           # Dependency injection
```

---

## Data Flow

### Request Flow (Create Recipe)

```
1. HTTP Request
   POST /api/v1/recipes
   Authorization: Bearer {token}
   Body: CreateRecipeRequest (JSON)

   ↓

2. Presentation Layer
   - auth_controller.py validates JWT token
   - Extracts user from token
   - controller.py receives request
   - Pydantic validates request body
   - FastAPI injects dependencies

   ↓

3. Application Layer
   - CreateRecipeUseCase.execute()
   - Validates business rules
   - Creates Recipe domain entity
   - Calls repository to persist

   ↓

4. Domain Layer
   - Recipe.create() factory method
   - Validates all invariants
   - Creates Ingredient entities
   - Creates Step entities
   - Sets initial metadata

   ↓

5. Infrastructure Layer
   - SQLAlchemyRecipeRepository.add()
   - Converts domain entity to ORM model
   - Saves to database
   - Converts back to domain entity

   ↓

6. Response Flow (reversed)
   Infrastructure → Domain → Application → Presentation

   ↓

7. HTTP Response
   201 Created
   Body: RecipeCreatedResponse (JSON)
```

---

### Query Flow (Search Recipes)

```
1. HTTP Request
   GET /api/v1/recipes?search=pasta&cuisine=italian&page=1

   ↓

2. Presentation Layer
   - Validates query parameters
   - Creates RecipeSearchRequest DTO

   ↓

3. Application Layer
   - SearchRecipesUseCase.execute()
   - Builds specifications from filters
   - Calls repository with specs

   ↓

4. Domain Layer
   - Specifications compose query logic
   - RecipeByNameSpec & RecipeByCuisineSpec

   ↓

5. Infrastructure Layer
   - Repository converts specs to SQL
   - Executes query with pagination
   - Maps results to domain entities

   ↓

6. Response
   - Paginated recipe list
   - Metadata (total, pages, etc.)
```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐                          ┌─────────┐
│ Client  │                          │   API   │
└────┬────┘                          └────┬────┘
     │                                    │
     │  1. POST /auth/login               │
     ├───────────────────────────────────>│
     │  {email, password}                 │
     │                                    │
     │  2. Validate credentials           │
     │     Hash password & compare        │
     │     Generate access_token (30min)  │
     │     Generate refresh_token (90d)   │
     │     Store session in Redis         │
     │<───────────────────────────────────┤
     │  {access_token, refresh_token}     │
     │                                    │
     │  3. GET /recipes (with token)      │
     ├───────────────────────────────────>│
     │  Authorization: Bearer <access>    │
     │                                    │
     │  4. Verify token signature         │
     │     Check expiration               │
     │     Extract user_id                │
     │     Execute request                │
     │<───────────────────────────────────┤
     │  {recipes}                         │
     │                                    │
     │  5. Token expires                  │
     │  POST /auth/refresh                │
     ├───────────────────────────────────>│
     │  {refresh_token}                   │
     │                                    │
     │  6. Verify refresh token           │
     │     Check session in Redis         │
     │     Generate new access_token      │
     │<───────────────────────────────────┤
     │  {access_token, refresh_token}     │
```

### Token Structure

**Access Token Payload:**

```json
{
  "user_id": 123,
  "email": "user@example.com",
  "roles": ["common_user"],
  "exp": 1700140800,
  "iat": 1700139000,
  "type": "access"
}
```

**Refresh Token Payload:**

```json
{
  "user_id": 123,
  "session_id": "uuid-here",
  "exp": 1707916800,
  "iat": 1700140800,
  "type": "refresh"
}
```

---

## Performance Architecture

### Caching Strategy

**Redis Usage:**

1. **Session Storage** - User sessions with automatic expiration
2. **Rate Limiting** - Request counters per IP/user
3. **Query Results** - Frequently accessed recipes (future enhancement)

### Database Optimization

**Connection Pooling:**

```python
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30.0
```

**Lazy Loading:**

- Relationships loaded only when accessed
- Use `selectinload()` for N+1 prevention

**Pagination:**

- All list endpoints support pagination
- Default page size: 10
- Max page size: 100

### Async Operations

All I/O operations are async:

- Database queries
- Redis operations
- External API calls

Benefits:

- Non-blocking I/O
- Higher concurrency
- Better resource utilization

---

## Testing Architecture

### Test Pyramid

```
         /\
        /  \
       / E2E\     Integration Tests (10%)
      /------\    - Full HTTP request/response
     /        \   - Real database (test DB)
    /  Integ. \
   /------------\ Application Tests (20%)
  /              \- Use case testing
 /   Application \ - Mock repositories
/------------------\
/                    \
/       Unit          \ Unit Tests (70%)
/----------------------\
  - Domain entity tests
  - Value object tests
  - Pure business logic
```

### Test Structure

```python
# Unit Test (Domain Layer)
def test_user_creation_with_valid_data():
    user = User.create(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        raw_password="SecureP@ss123",
        gender=UserGender.MALE,
    )
    assert user.email == "john@example.com"
    assert user.full_name == "John Doe"

# Application Test (Use Case)
@pytest.mark.asyncio
async def test_signup_use_case(mock_user_repo, mock_password_service):
    use_case = SignUpUseCase(mock_user_repo, mock_password_service)
    result = await use_case.execute(signup_request)
    assert result.user_id is not None

# Integration Test (Controller)
@pytest.mark.asyncio
async def test_signup_endpoint(client: AsyncClient):
    response = await client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    assert "access_token" in response.json()
```

---

## Future Architecture Enhancements

### Planned Improvements

1. **Event-Driven Architecture**

   - Domain events for audit logging
   - Recipe created/updated events
   - User registration events

2. **CQRS (Command Query Responsibility Segregation)**

   - Separate read and write models
   - Optimized query models
   - Event sourcing for audit trail

3. **Microservices Migration**

   - Split into Recipe Service and Auth Service
   - API Gateway
   - Service mesh (Istio)

4. **Advanced Caching**

   - Redis cache for popular recipes
   - Cache invalidation strategies
   - Distributed caching

5. **Message Queue**
   - RabbitMQ/Kafka for async operations
   - Email notifications
   - Image processing

---

**Last Updated:** November 2025
**Architecture Version:** 1.0.0
