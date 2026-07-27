---
codeExamples:
  - id: "specification-search"
    title: "Specification-based recipe search"
    description: "RecipeSpecificationBuilder composes domain specifications into a single SQL query—keeps search logic out of controllers."
    category: "domain"
    duration: "5 min read"
    views: 0
    tags:
      - "ddd"
      - "search"
      - "sqlalchemy"
    files:
      - name: "specification_builder.py"
        path: "app/modules/recipe/infrastructure/persistence/specification_builder.py"
        language: "python"
        highlighted: true
        explanation: "Criteria DTO → AndSpecification chain → repository executes with joins."
        content: |
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

  - id: "create-recipe-use-case"
    title: "Create recipe use case"
    description: "Application layer orchestrates validation, persistence, and DTO mapping without FastAPI imports."
    category: "application"
    duration: "4 min read"
    views: 0
    tags:
      - "use-case"
      - "clean-architecture"
    files:
      - name: "create_recipe.py"
        path: "app/modules/recipe/application/use_cases/recipe/create_recipe.py"
        language: "python"
        highlighted: true
        explanation: "Injected IRecipeRepository; maps CreateRecipeRequest to domain Recipe aggregate."
        content: |
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

  - id: "rate-limit-decorator"
    title: "Declarative rate limits on routes"
    description: "@rate_limit profile names map to RATE_LIMIT_CONFIG windows per client IP."
    category: "security"
    duration: "3 min read"
    views: 0
    tags:
      - "rate-limit"
      - "fastapi"
    files:
      - name: "rate_limiter.py"
        path: "app/config/rate_limiter.py"
        language: "python"
        highlighted: true
        explanation: "Used as @rate_limit('strict') on signup/login and @rate_limit('public') on search."
        content: |
          def rate_limit(config_name: str):
              def decorator(func):
                  rate_limit_manager.set_endpoint_limit(
                      f"{func.__module__}.{func.__name__}", config_name
                  )
                  return func
              return decorator

      - name: "auth_controller.py"
        path: "app/modules/auth/presentation/auth_controller.py"
        language: "python"
        highlighted: false
        explanation: "Example: signup uses strict (10/min), refresh uses api (30/min)."
        content: |
          @router.post("/signup", ...)
          @rate_limit("strict")
          async def signup(...): ...

  - id: "fastapi-lifespan"
    title: "Application lifespan (DB + Redis)"
    description: "main.py wires async startup/shutdown for database and Redis used by auth sessions."
    category: "api"
    duration: "2 min read"
    views: 0
    tags:
      - "fastapi"
      - "async"
    files:
      - name: "main.py"
        path: "main.py"
        language: "python"
        highlighted: true
        explanation: "ECS tasks rely on successful Redis connect before accepting traffic if health checks include dependency probes."
        content: |
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
---

# Code Showcase

> Snippets are abbreviated for portfolio display; open the referenced paths for full implementations and tests under `tests/`.

> **Reading order:** specification search → create recipe use case → rate limits → lifespan wiring.

> **AWS note:** Ensure `initialize_redis()` targets ElastiCache endpoint from task env; failed Redis breaks refresh/logout flows.
