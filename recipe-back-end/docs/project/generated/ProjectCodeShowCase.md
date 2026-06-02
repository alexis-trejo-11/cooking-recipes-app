# Code Showcase

## Specification-based recipe search

RecipeSpecificationBuilder composes domain specifications into a single SQL query—keeps search logic out of controllers.

**Category:** domain | **Duration:** 5 min read | **Tags:** ddd, search, sqlalchemy

### specification_builder.py

**Path:** `app/modules/recipe/infrastructure/persistence/specification_builder.py`

Criteria DTO → AndSpecification chain → repository executes with joins.

```python
class RecipeSpecificationBuilder:
    @staticmethod
    def build_from_criteria(criteria: RecipeSearchCriteria) -> Specification:
        if not criteria.include_deleted:
            spec = RecipeIsActiveSpecification()
        else:
            spec = None
        if criteria.name:
            name_spec = RecipeByNameSpecification(criteria.name)
            spec = name_spec if spec is None else AndSpecification(spec, name_spec)
        if criteria.author_id:
            author_spec = RecipeByAuthorSpecification(criteria.author_id)
            spec = author_spec if spec is None else AndSpecification(spec, author_spec)
        return spec
```

## Create recipe use case

Application layer orchestrates validation, persistence, and DTO mapping without FastAPI imports.

**Category:** application | **Duration:** 4 min read | **Tags:** use-case, clean-architecture

### create_recipe.py

**Path:** `app/modules/recipe/application/use_cases/recipe/create_recipe.py`

Injected IRecipeRepository; maps CreateRecipeRequest to domain Recipe aggregate.

```python
class CreateRecipeUseCase:
    def __init__(self, recipe_repository: IRecipeRepository):
        self._recipe_repository = recipe_repository

    async def execute(
        self, request: CreateRecipeRequest, author_id: UserId
    ) -> RecipeCreatedResponse:
        # Build domain entity, validate invariants, persist
        recipe = self._build_recipe_from_request(request, author_id)
        saved = await self._recipe_repository.save(recipe)
        return RecipeCreatedResponse.from_entity(saved)
```

## Declarative rate limits on routes

@rate_limit profile names map to RATE_LIMIT_CONFIG windows per client IP.

**Category:** security | **Duration:** 3 min read | **Tags:** rate-limit, fastapi

### rate_limiter.py

**Path:** `app/config/rate_limiter.py`

Used as @rate_limit('strict') on signup/login and @rate_limit('public') on search.

```python
def rate_limit(config_name: str):
    def decorator(func):
        rate_limit_manager.set_endpoint_limit(
            f"{func.__module__}.{func.__name__}", config_name
        )
        return func
    return decorator
```

### auth_controller.py

**Path:** `app/modules/auth/presentation/auth_controller.py`

Example: signup uses strict (10/min), refresh uses api (30/min).

```python
@router.post("/signup", ...)
@rate_limit("strict")
async def signup(...): ...
```

## Application lifespan (DB + Redis)

main.py wires async startup/shutdown for database and Redis used by auth sessions.

**Category:** api | **Duration:** 2 min read | **Tags:** fastapi, async

### main.py

**Path:** `main.py`

ECS tasks rely on successful Redis connect before accepting traffic if health checks include dependency probes.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await initialize_redis()
    yield
    await close_redis()
    await close_db()

app = FastAPI(
    title="Cooking Recipes API",
    version="1.0.0",
    lifespan=lifespan,
)
```

## Additional notes

# Code Showcase

> Snippets are abbreviated for portfolio display; open the referenced paths for full implementations and tests under `tests/`.

> **Reading order:** specification search → create recipe use case → rate limits → lifespan wiring.

> **AWS note:** Ensure `initialize_redis()` targets ElastiCache endpoint from task env; failed Redis breaks refresh/logout flows.

