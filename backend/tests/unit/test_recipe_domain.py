"""Recipe domain unit tests aligned with the three-DTO create API."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.exceptions import (
    RecipeDomainException,
    RecipeValidationException,
    RecipeDeletedException,
)
from app.modules.recipe.domain.models.entities.ingredient import (
    Ingredient,
    IngredientProperties,
)
from app.modules.recipe.domain.models.entities.recipe import Recipe
from app.modules.recipe.domain.models.value_objects.enums import (
    DifficultyLevel,
    CuisineType,
    MealType,
    DietType,
)
from app.modules.recipe.domain.models.value_objects.param_dtos import (
    RecipeCreateBasicInfo,
    RecipeCreateContent,
    RecipeCreateDetails,
)
from app.modules.recipe.domain.models.value_objects.value_objects_standard import (
    RecipeId,
    Quantity,
    Step,
    Tag,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
)


def _ingredient(name: str = "Tomato", optional: bool = False) -> Ingredient:
    return Ingredient.create(
        name=name,
        quantity=Quantity(value=Decimal("200.0"), unit="grams"),
        properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
        is_optional=optional,
    )


def _make_recipe(
    name: str = "Test Recipe",
    author_id: UserId | None = None,
    description: str = "A tasty test recipe description",
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
    cuisine: CuisineType = CuisineType.ITALIAN,
    meal_types: set[MealType] | None = None,
    ingredients: list[Ingredient] | None = None,
    steps: list[Step] | None = None,
    tags: set[Tag] | None = None,
) -> Recipe:
    return Recipe.create(
        RecipeCreateBasicInfo(
            name=name,
            author_id=author_id or UserId(1),
            description=description,
            difficulty=difficulty,
            cuisine=cuisine,
        ),
        RecipeCreateContent(
            ingredients=ingredients or [_ingredient()],
            steps=steps
            or [Step(number=1, description="Chop and cook", duration_minutes=10)],
            tags=tags or {Tag(name="test")},
        ),
        RecipeCreateDetails(
            meal_types=meal_types or {MealType.DINNER},
            serving_info=ServingInfo(servings=4, serving_size="1 bowl"),
            cooking_time=CookingTime(prep_minutes=10, cook_minutes=20),
            nutritional_info=NutritionalInfo(calories=400, protein_g=Decimal("20")),
        ),
    )


@pytest.fixture
def sample_recipe() -> Recipe:
    return _make_recipe()


class TestRecipeCreation:
    def test_create_recipe_success(self):
        recipe = _make_recipe()

        assert recipe.name == "Test Recipe"
        assert recipe.author_id == UserId(1)
        assert recipe.difficulty == DifficultyLevel.MEDIUM
        assert recipe.cuisine == CuisineType.ITALIAN
        assert MealType.DINNER in recipe.meal_types
        assert len(recipe.ingredients) == 1
        assert len(recipe.steps) == 1
        assert recipe.serving_info.servings == 4
        assert recipe.is_deleted is False

    def test_create_recipe_empty_name_fails(self):
        with pytest.raises(RecipeValidationException):
            RecipeCreateBasicInfo(
                name="   ",
                author_id=UserId(1),
                description="desc",
                difficulty=DifficultyLevel.EASY,
                cuisine=CuisineType.ITALIAN,
            )

    def test_create_requires_ingredients_steps_and_tags(self):
        with pytest.raises(RecipeValidationException):
            RecipeCreateContent(ingredients=[], steps=[], tags=set())


class TestRecipeReconstruction:
    def test_reconstruct_recipe_success(self):
        data = {
            "id": RecipeId(1),
            "name": "Persisted Recipe",
            "author_id": UserId(1),
            "description": "A persisted recipe",
            "difficulty": DifficultyLevel.HARD,
            "cuisine": CuisineType.MEXICAN,
            "ingredients": [_ingredient("Beans")],
            "steps": [Step(number=1, description="Cook beans")],
            "tags": {Tag(name="mexican")},
            "meal_types": {MealType.LUNCH},
            "serving_info": ServingInfo(servings=2),
            "cooking_time": CookingTime(prep_minutes=5, cook_minutes=15),
            "nutritional_info": None,
            "rating_sum": 10,
            "review_count": 2,
            "view_count": 50,
            "favorite_count": 3,
            "version": 5,
            "created_at": datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2024, 1, 2, 15, 30, 0, tzinfo=timezone.utc),
            "deleted_at": None,
        }

        recipe = Recipe.reconstruct(data)

        assert recipe.id == RecipeId(1)
        assert recipe.name == "Persisted Recipe"
        assert recipe.review_count == 2
        assert recipe.view_count == 50
        assert recipe.version == 5


class TestRecipeBasicInfo:
    def test_update_basic_info(self, sample_recipe):
        sample_recipe.update_basic_info(
            name="Updated Name",
            description="Updated description text",
            difficulty=DifficultyLevel.HARD,
        )

        assert sample_recipe.name == "Updated Name"
        assert sample_recipe.description == "Updated description text"
        assert sample_recipe.difficulty == DifficultyLevel.HARD

    def test_update_empty_name_fails(self, sample_recipe):
        with pytest.raises(RecipeValidationException):
            sample_recipe.update_basic_info(name="  ")


class TestRecipeCollections:
    def test_add_ingredient_success(self, sample_recipe):
        before = len(sample_recipe.ingredients)
        sample_recipe.add_ingredient(_ingredient("Onion"))
        assert len(sample_recipe.ingredients) == before + 1

    def test_add_duplicate_ingredient_name_fails(self, sample_recipe):
        with pytest.raises(RecipeDomainException):
            sample_recipe.add_ingredient(_ingredient("Tomato"))

    def test_add_step_and_duplicate_number_fails(self, sample_recipe):
        sample_recipe.add_step(Step(number=2, description="Serve"))
        with pytest.raises(RecipeDomainException):
            sample_recipe.add_step(Step(number=2, description="Duplicate"))

    def test_add_tag_and_meal_type(self, sample_recipe):
        sample_recipe.add_tag(Tag(name="comfort"))
        sample_recipe.add_meal_type(MealType.LUNCH)

        assert any(t.name == "comfort" for t in sample_recipe.tags)
        assert MealType.LUNCH in sample_recipe.meal_types

    def test_clear_ingredients_steps_tags(self, sample_recipe):
        sample_recipe.clear_ingredients()
        sample_recipe.clear_steps()
        sample_recipe.clear_tags()

        assert sample_recipe.ingredients == []
        assert sample_recipe.steps == []
        assert sample_recipe.tags == set()


class TestRecipeMetadataAndDiet:
    def test_update_serving_and_cooking_time(self, sample_recipe):
        sample_recipe.update_serving_info(ServingInfo(servings=6))
        sample_recipe.update_cooking_time(
            CookingTime(prep_minutes=15, cook_minutes=30, rest_minutes=5)
        )

        assert sample_recipe.serving_info.servings == 6
        assert sample_recipe.calculate_total_time() == 50

    def test_diet_compatibility(self):
        vegan = _ingredient("Tofu")
        recipe = _make_recipe(ingredients=[vegan])

        assert recipe.is_suitable_for_diet(DietType.VEGAN)
        assert DietType.VEGAN in recipe.get_compatible_diets()

    def test_get_allergens(self):
        allergen = Ingredient.create(
            name="Peanut",
            quantity=Quantity(value=Decimal("10"), unit="grams"),
            properties=IngredientProperties(allergens={"peanuts"}),
        )
        recipe = _make_recipe(ingredients=[allergen])
        assert "peanuts" in recipe.get_allergens()


class TestRecipeFavoritesAndDeletion:
    def test_decrease_favorite_count_at_zero_fails(self, sample_recipe):
        with pytest.raises(RecipeDomainException):
            sample_recipe.decrease_favorite_count()

    def test_soft_delete_and_restore(self, sample_recipe):
        sample_recipe.soft_delete()
        assert sample_recipe.is_deleted is True

        with pytest.raises(RecipeDeletedException):
            sample_recipe.update_basic_info(name="Nope")

        sample_recipe.restore()
        assert sample_recipe.is_deleted is False

    def test_restore_non_deleted_fails(self, sample_recipe):
        with pytest.raises(RecipeValidationException):
            sample_recipe.restore()


class TestRecipeRepresentation:
    def test_repr_and_str(self, sample_recipe):
        assert "Test Recipe" in repr(sample_recipe)
        assert "Test Recipe" in str(sample_recipe)
