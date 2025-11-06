from decimal import Decimal
from .use_cases import CreateRecipeUseCase
from app.receipt.domain.interfaces import RecipeRepository
from app.auth.domain.interfaces import UserRepository
from ..dtos import CreateRecipeRequest, RecipeCreatedResponse
from app.auth.application.exceptions import UserNotFoundException
from app.auth.domain.user import UserId
from app.receipt.application.exceptions import RecipeValidationException
from app.receipt.domain.entities.recipe import (
    Recipe,
    Tag,
    CookingTime,
    NutritionalInfo,
    ServingInfo,
    Step,
    Quantity,
    DifficultyLevel,
    MealType,
    CuisineType,
)
from app.receipt.domain.entities.ingredient import IngredientProperties, Ingredient


class CreateRecipeUseCaseImpl(CreateRecipeUseCase):
    def __init__(
        self, recipe_repository: RecipeRepository, user_repository: UserRepository
    ) -> None:
        self.recipe_repository = recipe_repository
        self.user_repository = user_repository

    async def execute(
        self, request: CreateRecipeRequest, author_id: UserId
    ) -> RecipeCreatedResponse:
        await self._validate_author(request.name, author_id)
        recipe = self.create_recipe(request, author_id)

        saved_recipe = await self.recipe_repository.save(recipe)
        return RecipeCreatedResponse(id=saved_recipe.id.value, name=saved_recipe.name)

    async def _validate_author(self, name: str, author_id: UserId):
        await self._validate_existing_author(author_id)
        await self._validate_not_duplicated_author(name, author_id)

    async def _validate_existing_author(self, author_id: UserId):
        author = await self.user_repository.exists_by_id(author_id)
        if not author:
            raise UserNotFoundException(f"Author with ID {author_id} not found")

    async def _validate_not_duplicated_author(self, name: str, author_id: UserId):
        if await self.recipe_repository.exists_by_name_and_author(name, author_id):
            raise RecipeValidationException(
                f"Recipe with name '{name}' already exists for this author",
                "DUPLICATE_RECIPE_NAME",
            )

    def create_recipe(self, request: CreateRecipeRequest, author_id: UserId) -> Recipe:
        ingredients = []
        for ing_dto in request.ingredients:
            ingredient = Ingredient.create(
                name=ing_dto.name,
                quantity=Quantity(
                    value=ing_dto.quantity.value, unit=ing_dto.quantity.unit
                ),
                properties=IngredientProperties(
                    is_vegan=ing_dto.properties.is_vegan,
                    is_vegetarian=ing_dto.properties.is_vegetarian,
                    is_gluten_free=ing_dto.properties.is_gluten_free,
                    is_dairy_free=ing_dto.properties.is_dairy_free,
                    allergens=set(ing_dto.properties.allergens),
                ),
                is_optional=ing_dto.is_optional,
                substitutes=ing_dto.substitutes,
            )
            ingredients.append(ingredient)

        steps = []
        for step_dto in request.steps:
            step = Step(
                number=len(steps) + 1,
                description=step_dto.description,
                duration_minutes=step_dto.duration_minutes,
                technique=step_dto.technique,
                temperature=step_dto.temperature,
            )
            steps.append(step)

        tags = {Tag(name=tag.name, description=tag.description) for tag in request.tags}
        meal_types = set(request.meal_types)

        serving_info = (
            ServingInfo(servings=request.servings) if request.servings else None
        )

        cooking_time = None
        if (
            request.prep_time_minutes is not None
            or request.cook_time_minutes is not None
        ):
            cooking_time = CookingTime(
                prep_minutes=request.prep_time_minutes or 0,
                cook_minutes=request.cook_time_minutes or 0,
            )

        nutritional_info = None
        if any([request.calories, request.protein_g, request.carbs_g, request.fat_g]):
            nutritional_info = NutritionalInfo(
                calories=request.calories or 0,
                protein_g=request.protein_g or Decimal("0"),
                carbs_g=request.carbs_g or Decimal("0"),
                fat_g=request.fat_g or Decimal("0"),
            )

        # Create recipe
        recipe = Recipe.create(
            name=request.name,
            author_id=author_id,
            description=request.description,
            difficulty=DifficultyLevel(request.difficulty),
            cuisine=CuisineType(request.cuisine),
        )

        # Add all components
        for ingredient in ingredients:
            recipe.add_ingredient(ingredient)

        for step in steps:
            recipe.add_step(
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )

        for tag in tags:
            recipe.add_tag(tag)

        for meal_type in meal_types:
            recipe.add_meal_type(MealType(meal_type))

        if serving_info:
            recipe.set_serving_info(serving_info)

        if cooking_time:
            recipe.set_cooking_time(cooking_time)

        if nutritional_info:
            recipe.set_nutritional_info(nutritional_info)

        return recipe
