from typing import List, Optional, Set
from app.application.dto.recipe_dtos import (
    CreateRecipeRequest,
    UpdateRecipeRequest,
    RecipeResponse,
    RecipeSummaryResponse,
    PaginatedRecipesResponse,
    CreateIngredientRequest,
    CreateStepRequest,
    RecipeSearchRequest,
    FindByIngredientsRequest,
    ScaleRecipeRequest,
    AddRatingRequest,
)
from app.domain.interfaces.recipe_repository import RecipeRepository
from app.application.exceptions import (
    RecipeNotFoundException,
    RecipeAlreadyExistsException,
    UnauthorizedException,
    InvalidRecipeDataException,
)
from app.domain.entities.recipe import (
    Recipe,
    RecipeId,
    Ingredient,
    IngredientId,
    UserId,
    Quantity,
    IngredientProperties,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
    Tag,
    DietType,
    DifficultyLevel,
    MealType,
    CuisineType,
)


# ============================================================================
# CREATE RECIPES
# ============================================================================


class CreateRecipeUseCase:
    """Create a new recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, request: CreateRecipeRequest, author_id: UUID
    ) -> RecipeResponse:
        """Execute recipe creation"""

        try:
            # Create recipe entity
            recipe = Recipe(
                id=RecipeId(),
                name=request.name,
                author_id=UserId(author_id),
                description=request.description,
                difficulty=DifficultyLevel(request.difficulty.value),
                cuisine=CuisineType(request.cuisine.value) if request.cuisine else None,
            )

            # Add ingredients
            for ing_req in request.ingredients:
                ingredient = Ingredient(
                    id=IngredientId(),
                    name=ing_req.name,
                    quantity=Quantity(
                        value=ing_req.quantity.value, unit=ing_req.quantity.unit
                    ),
                    properties=IngredientProperties(
                        is_vegetarian=ing_req.properties.is_vegetarian,
                        is_vegan=ing_req.properties.is_vegan,
                        is_gluten_free=ing_req.properties.is_gluten_free,
                        is_dairy_free=ing_req.properties.is_dairy_free,
                        allergens=ing_req.properties.allergens,
                    ),
                    is_optional=ing_req.is_optional,
                    substitutes=ing_req.substitutes,
                )
                recipe.add_ingredient(ingredient)

            # Add steps
            for step_req in request.steps:
                recipe.add_step(
                    description=step_req.description,
                    duration_minutes=step_req.duration_minutes,
                    technique=step_req.technique,
                    temperature=step_req.temperature,
                )

            # Add tags
            for tag_name in request.tags:
                recipe.add_tag(Tag(tag_name))

            # Add meal types
            for meal_type in request.meal_types:
                recipe.add_meal_type(MealType(meal_type.value))

            # Set serving info
            if request.serving_info:
                recipe.set_serving_info(
                    ServingInfo(
                        servings=request.serving_info.servings,
                        serving_size=request.serving_info.serving_size,
                    )
                )

            # Set cooking time
            if request.cooking_time:
                recipe.set_cooking_time(
                    CookingTime(
                        prep_minutes=request.cooking_time.prep_minutes,
                        cook_minutes=request.cooking_time.cook_minutes,
                    )
                )

            # Set nutritional info
            if request.nutritional_info:
                recipe.set_nutritional_info(
                    NutritionalInfo(
                        calories=request.nutritional_info.calories,
                        protein_g=request.nutritional_info.protein_g,
                        carbs_g=request.nutritional_info.carbs_g,
                        fat_g=request.nutritional_info.fat_g,
                        fiber_g=request.nutritional_info.fiber_g,
                        sodium_mg=request.nutritional_info.sodium_mg,
                    )
                )

            # Save to repository
            saved_recipe = await self.recipe_repository.save(recipe)

            return self._map_to_response(saved_recipe)

        except ValueError as e:
            raise InvalidRecipeDataException(f"Invalid recipe data: {str(e)}")

    def _map_to_response(self, recipe: Recipe) -> RecipeResponse:
        """Map domain entity to response DTO"""
        return RecipeResponse(
            id=recipe.id.value,
            name=recipe.name,
            author_id=recipe.author_id.value,
            description=recipe.description,
            difficulty=recipe.difficulty.value,
            cuisine=recipe.cuisine.value if recipe.cuisine else None,
            ingredients=[
                {
                    "id": ing.id.value,
                    "name": ing.name,
                    "quantity": {
                        "value": ing.quantity.value,
                        "unit": ing.quantity.unit,
                    },
                    "properties": {
                        "is_vegetarian": ing.properties.is_vegetarian,
                        "is_vegan": ing.properties.is_vegan,
                        "is_gluten_free": ing.properties.is_gluten_free,
                        "is_dairy_free": ing.properties.is_dairy_free,
                        "allergens": ing.properties.allergens,
                    },
                    "is_optional": ing.is_optional,
                    "substitutes": ing.substitutes,
                }
                for ing in recipe.get_ingredients()
            ],
            steps=[
                {
                    "number": step.number,
                    "description": step.description,
                    "duration_minutes": step.duration_minutes,
                    "technique": step.technique,
                    "temperature": step.temperature,
                }
                for step in recipe.get_steps()
            ],
            tags={tag.name for tag in recipe.get_tags()},
            meal_types={mt.value for mt in recipe.get_meal_types()},
            serving_info=(
                {
                    "servings": recipe.get_serving_info().servings,
                    "serving_size": recipe.get_serving_info().serving_size,
                }
                if recipe.get_serving_info()
                else None
            ),
            cooking_time=(
                {
                    "prep_minutes": recipe.get_cooking_time().prep_minutes,
                    "cook_minutes": recipe.get_cooking_time().cook_minutes,
                }
                if recipe.get_cooking_time()
                else None
            ),
            nutritional_info=(
                {
                    "calories": recipe.get_nutritional_info().calories,
                    "protein_g": recipe.get_nutritional_info().protein_g,
                    "carbs_g": recipe.get_nutritional_info().carbs_g,
                    "fat_g": recipe.get_nutritional_info().fat_g,
                    "fiber_g": recipe.get_nutritional_info().fiber_g,
                    "sodium_mg": recipe.get_nutritional_info().sodium_mg,
                }
                if recipe.get_nutritional_info()
                else None
            ),
            average_rating=recipe.get_average_rating(),
            rating_count=recipe.get_rating_count(),
            compatible_diets={diet.value for diet in recipe.get_compatible_diets()},
            allergens=recipe.get_allergens(),
            created_at=recipe.get_created_at(),
            updated_at=recipe.get_updated_at(),
        )


# ============================================================================
# GET RECIPES
# ============================================================================


class GetRecipeByIdUseCase:
    """Get a single recipe by ID"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: UUID) -> RecipeResponse:
        """Execute get recipe by ID"""
        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))

        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        # Reuse mapper from CreateRecipeUseCase
        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(recipe)


class GetAllRecipesUseCase:
    """Get all recipes with pagination"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, skip: int = 0, limit: int = 20) -> PaginatedRecipesResponse:
        """Execute get all recipes"""
        recipes = await self.recipe_repository.find_all(skip=skip, limit=limit)
        total = await self.recipe_repository.count()

        items = [self._map_to_summary(r) for r in recipes]

        return PaginatedRecipesResponse(
            items=items, total=total, skip=skip, limit=limit
        )

    def _map_to_summary(self, recipe: Recipe) -> RecipeSummaryResponse:
        return RecipeSummaryResponse(
            id=recipe.id.value,
            name=recipe.name,
            author_id=recipe.author_id.value,
            description=recipe.description,
            difficulty=recipe.difficulty.value,
            cuisine=recipe.cuisine.value if recipe.cuisine else None,
            tags={tag.name for tag in recipe.get_tags()},
            meal_types={mt.value for mt in recipe.get_meal_types()},
            total_time_minutes=recipe.calculate_total_time(),
            servings=(
                recipe.get_serving_info().servings
                if recipe.get_serving_info()
                else None
            ),
            average_rating=recipe.get_average_rating(),
            rating_count=recipe.get_rating_count(),
            created_at=recipe.get_created_at(),
        )


class GetRecipesByAuthorUseCase:
    """Get recipes by author"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, author_id: UUID, skip: int = 0, limit: int = 20
    ) -> PaginatedRecipesResponse:
        """Execute get recipes by author"""
        recipes = await self.recipe_repository.find_by_author(
            UserId(author_id), skip=skip, limit=limit
        )

        items = [
            GetAllRecipesUseCase(self.recipe_repository)._map_to_summary(r)
            for r in recipes
        ]

        return PaginatedRecipesResponse(
            items=items, total=len(items), skip=skip, limit=limit
        )


# ============================================================================
# SEARCH RECIPES
# ============================================================================


class SearchRecipesUseCase:
    """Advanced recipe search"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, request: RecipeSearchRequest) -> PaginatedRecipesResponse:
        """Execute advanced search"""

        # Convert DTOs to domain types
        diets = {DietType(d.value) for d in request.diets} if request.diets else None
        difficulties = (
            {DifficultyLevel(d.value) for d in request.difficulties}
            if request.difficulties
            else None
        )
        meal_types = (
            {MealType(m.value) for m in request.meal_types}
            if request.meal_types
            else None
        )
        cuisines = (
            {CuisineType(c.value) for c in request.cuisines}
            if request.cuisines
            else None
        )

        recipes = await self.recipe_repository.advanced_search(
            name_query=request.name_query,
            ingredients=request.ingredients,
            diets=diets,
            difficulties=difficulties,
            meal_types=meal_types,
            cuisines=cuisines,
            max_time=request.max_time_minutes,
            min_rating=request.min_rating,
            exclude_allergens=request.exclude_allergens,
            skip=request.skip,
            limit=request.limit,
        )

        items = [
            GetAllRecipesUseCase(self.recipe_repository)._map_to_summary(r)
            for r in recipes
        ]

        return PaginatedRecipesResponse(
            items=items, total=len(items), skip=request.skip, limit=request.limit
        )


class FindRecipesByIngredientsUseCase:
    """Find recipes by available ingredients"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, request: FindByIngredientsRequest
    ) -> PaginatedRecipesResponse:
        """Execute find by ingredients"""

        recipes = await self.recipe_repository.find_by_ingredients(
            ingredient_names=request.ingredient_names,
            match_all=request.match_all,
            skip=request.skip,
            limit=request.limit,
        )

        items = [
            GetAllRecipesUseCase(self.recipe_repository)._map_to_summary(r)
            for r in recipes
        ]

        return PaginatedRecipesResponse(
            items=items, total=len(items), skip=request.skip, limit=request.limit
        )


# ============================================================================
# UPDATE RECIPES
# ============================================================================


class UpdateRecipeUseCase:
    """Update an existing recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: UUID, request: UpdateRecipeRequest, author_id: UUID
    ) -> RecipeResponse:
        """Execute recipe update"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        # Check authorization
        if recipe.author_id.value != author_id:
            raise UnauthorizedException("Not authorized to update this recipe")

        # Update fields (you'd add setters to Recipe entity)
        # For now, simplified - in production add proper update methods

        updated_recipe = await self.recipe_repository.save(recipe)

        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(
            updated_recipe
        )


class AddIngredientToRecipeUseCase:
    """Add ingredient to existing recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self,
        recipe_id: UUID,
        ingredient_request: CreateIngredientRequest,
        author_id: UUID,
    ) -> RecipeResponse:
        """Execute add ingredient"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        if recipe.author_id.value != author_id:
            raise UnauthorizedException("Not authorized to modify this recipe")

        ingredient = Ingredient(
            id=IngredientId(),
            name=ingredient_request.name,
            quantity=Quantity(
                value=ingredient_request.quantity.value,
                unit=ingredient_request.quantity.unit,
            ),
            properties=IngredientProperties(
                is_vegetarian=ingredient_request.properties.is_vegetarian,
                is_vegan=ingredient_request.properties.is_vegan,
                is_gluten_free=ingredient_request.properties.is_gluten_free,
                is_dairy_free=ingredient_request.properties.is_dairy_free,
                allergens=ingredient_request.properties.allergens,
            ),
            is_optional=ingredient_request.is_optional,
            substitutes=ingredient_request.substitutes,
        )

        recipe.add_ingredient(ingredient)
        updated_recipe = await self.recipe_repository.save(recipe)

        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(
            updated_recipe
        )


class AddStepToRecipeUseCase:
    """Add step to existing recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: UUID, step_request: CreateStepRequest, author_id: UUID
    ) -> RecipeResponse:
        """Execute add step"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        if recipe.author_id.value != author_id:
            raise UnauthorizedException("Not authorized to modify this recipe")

        recipe.add_step(
            description=step_request.description,
            duration_minutes=step_request.duration_minutes,
            technique=step_request.technique,
            temperature=step_request.temperature,
        )

        updated_recipe = await self.recipe_repository.save(recipe)

        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(
            updated_recipe
        )


# ============================================================================
# RATING
# ============================================================================


class AddRatingToRecipeUseCase:
    """Add rating to a recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: UUID, rating: int) -> RecipeResponse:
        """Execute add rating"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        try:
            recipe.add_rating(rating)
        except ValueError as e:
            raise InvalidRecipeDataException(str(e))

        updated_recipe = await self.recipe_repository.save(recipe)

        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(
            updated_recipe
        )


# ============================================================================
# SCALING
# ============================================================================


class ScaleRecipeUseCase:
    """Scale recipe to different serving size"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: UUID, request: ScaleRecipeRequest
    ) -> RecipeResponse:
        """Execute recipe scaling"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        try:
            scaled_recipe = recipe.scale_recipe(request.target_servings)
        except ValueError as e:
            raise InvalidRecipeDataException(str(e))

        return CreateRecipeUseCase(self.recipe_repository)._map_to_response(
            scaled_recipe
        )


# ============================================================================
# DELETE
# ============================================================================


class DeleteRecipeUseCase:
    """Delete a recipe"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: UUID, author_id: UUID) -> bool:
        """Execute recipe deletion"""

        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        if recipe.author_id.value != author_id:
            raise UnauthorizedException("Not authorized to delete this recipe")

        return await self.recipe_repository.delete(RecipeId(recipe_id))


# ============================================================================
# RECOMMENDATIONS
# ============================================================================


class GetTopRatedRecipesUseCase:
    """Get top rated recipes"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self,
        min_rating: float = 4.0,
        min_rating_count: int = 5,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedRecipesResponse:
        """Execute get top rated"""

        recipes = await self.recipe_repository.find_top_rated(
            min_rating=min_rating,
            min_rating_count=min_rating_count,
            skip=skip,
            limit=limit,
        )

        items = [
            GetAllRecipesUseCase(self.recipe_repository)._map_to_summary(r)
            for r in recipes
        ]

        return PaginatedRecipesResponse(
            items=items, total=len(items), skip=skip, limit=limit
        )


class GetQuickRecipesUseCase:
    """Get recipes that can be made quickly"""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, max_minutes: int = 30, skip: int = 0, limit: int = 20
    ) -> PaginatedRecipesResponse:
        """Execute get quick recipes"""

        recipes = await self.recipe_repository.find_by_max_time(
            max_minutes=max_minutes, skip=skip, limit=limit
        )

        items = [
            GetAllRecipesUseCase(self.recipe_repository)._map_to_summary(r)
            for r in recipes
        ]

        return PaginatedRecipesResponse(
            items=items, total=len(items), skip=skip, limit=limit
        )
