# test_recipe.py
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock

from app.receipt.domain.entities.recipe import Recipe
from app.receipt.domain.entities.ingredient import Ingredient, IngredientProperties
from app.receipt.domain.entities.value_objects import (
    RecipeId,
    UserId,
    IngredientId,
    Quantity,
    Step,
    Tag,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
)
from app.receipt.domain.entities.enums import (
    DifficultyLevel,
    CuisineType,
    MealType,
    DietType,
)
from app.receipt.domain.exceptions import (
    RecipeValidationException,
    RecipeDeletedException,
)


# ===== FIXTURES =====


@pytest.fixture
def sample_recipe_data():
    """Sample data for recipe creation."""
    return {
        "name": "Test Recipe",
        "author_id": UserId(1),
        "description": "A test recipe description",
        "difficulty": DifficultyLevel.MEDIUM,
        "cuisine": CuisineType.ITALIAN,
    }


@pytest.fixture
def minimal_recipe_data():
    """Minimal data for recipe creation."""
    return {
        "name": "Minimal Recipe",
        "author_id": UserId(1),
    }


@pytest.fixture
def sample_persisted_recipe_data():
    """Sample data for recipe reconstruction."""
    return {
        "id": RecipeId(1),
        "name": "Persisted Recipe",
        "author_id": UserId(1),
        "description": "A persisted recipe",
        "difficulty": DifficultyLevel.HARD,
        "cuisine": CuisineType.MEXICAN,
        "ingredients": [],
        "steps": [],
        "tags": set(),
        "meal_types": set(),
        "serving_info": None,
        "cooking_time": None,
        "nutritional_info": None,
        "rating_sum": 0,
        "rating_count": 0,
        "view_count": 0,
        "favorite_count": 0,
        "version": 5,
        "created_at": datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 2, 15, 30, 0, tzinfo=timezone.utc),
        "deleted_at": None,
    }


@pytest.fixture
def sample_recipe(sample_recipe_data):
    """Sample recipe instance."""
    return Recipe.create(**sample_recipe_data)


@pytest.fixture
def sample_ingredient():
    """Sample ingredient instance."""
    return Ingredient.create(
        name="Tomato",
        quantity=Quantity(value=Decimal("200.0"), unit="grams"),
        properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
        is_optional=False,
        substitutes=[],
    )


@pytest.fixture
def sample_recipe_with_ingredients(sample_recipe, sample_ingredient):
    """Sample recipe with ingredients."""
    recipe = sample_recipe
    recipe.add_ingredient(sample_ingredient)

    another_ingredient = Ingredient.create(
        name="Onion",
        quantity=Quantity(value=Decimal("100.0"), unit="grams"),
        properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
        is_optional=False,
        substitutes=[],
    )
    recipe.add_ingredient(another_ingredient)

    return recipe


@pytest.fixture
def sample_recipe_with_mixed_ingredients(sample_recipe):
    """Sample recipe with mixed optional and required ingredients."""
    required_ingredient = Ingredient.create(
        name="Required Ingredient",
        quantity=Quantity(value=Decimal("200.0"), unit="grams"),
        properties=IngredientProperties(),
        is_optional=False,
        substitutes=[],
    )

    optional_ingredient = Ingredient.create(
        name="Optional Ingredient",
        quantity=Quantity(value=Decimal("100.0"), unit="grams"),
        properties=IngredientProperties(),
        is_optional=True,
        substitutes=[],
    )

    sample_recipe.add_ingredient(required_ingredient)
    sample_recipe.add_ingredient(optional_ingredient)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_allergens(sample_recipe):
    """Sample recipe with allergens."""
    dairy_ingredient = Ingredient.create(
        name="Cheese",
        quantity=Quantity(value=Decimal("100.0"), unit="grams"),
        properties=IngredientProperties(allergens={"dairy"}),
        is_optional=False,
        substitutes=[],
    )

    nuts_ingredient = Ingredient.create(
        name="Nuts",
        quantity=Quantity(value=Decimal("50.0"), unit="grams"),
        properties=IngredientProperties(allergens={"nuts"}),
        is_optional=False,
        substitutes=[],
    )

    sample_recipe.add_ingredient(dairy_ingredient)
    sample_recipe.add_ingredient(nuts_ingredient)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_steps(sample_recipe):
    """Sample recipe with steps."""
    step1 = Step(number=1, description="First step", duration_minutes=10)
    step2 = Step(
        number=2, description="Second step", duration_minutes=5, technique="mixing"
    )
    step3 = Step(
        number=3, description="Third step", duration_minutes=10, temperature="180°C"
    )

    sample_recipe.add_step(step1)
    sample_recipe.add_step(step2)
    sample_recipe.add_step(step3)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_tags(sample_recipe):
    """Sample recipe with tags."""
    tag1 = Tag(name="healthy", description="Healthy food")
    tag2 = Tag(name="quick", description="Quick to prepare")
    tag3 = Tag(name="vegetarian", description="Vegetarian meal")

    sample_recipe.add_tag(tag1)
    sample_recipe.add_tag(tag2)
    sample_recipe.add_tag(tag3)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_meal_types(sample_recipe):
    """Sample recipe with meal types."""
    sample_recipe.add_meal_type(MealType.BREAKFAST)
    sample_recipe.add_meal_type(MealType.LUNCH)
    return sample_recipe


@pytest.fixture
def sample_recipe_with_metadata(sample_recipe):
    """Sample recipe with cooking time and serving info."""
    cooking_time = CookingTime(prep_minutes=15, cook_minutes=30)
    serving_info = ServingInfo(servings=4, serving_size="1 cup")
    nutritional_info = NutritionalInfo(
        calories=350,
        protein_g=Decimal("15.0"),
        carbs_g=Decimal("45.0"),
        fat_g=Decimal("12.0"),
    )

    sample_recipe.set_cooking_time(cooking_time)
    sample_recipe.set_serving_info(serving_info)
    sample_recipe.set_nutritional_info(nutritional_info)

    return sample_recipe


# ===== TEST CLASSES =====


class TestRecipeCreation:
    """Test cases for Recipe creation functionality."""

    def test_create_recipe_success(self, sample_recipe_data):
        """Test successful recipe creation with valid data."""
        recipe = Recipe.create(**sample_recipe_data)

        assert recipe.name == "Test Recipe"
        assert recipe.author_id == UserId(1)
        assert recipe.description == "A test recipe description"
        assert recipe.difficulty == DifficultyLevel.MEDIUM
        assert recipe.cuisine == CuisineType.ITALIAN
        assert recipe.version == 1
        assert recipe.is_deleted is False

    def test_create_recipe_minimal_data(self, minimal_recipe_data):
        """Test recipe creation with minimal required data."""
        recipe = Recipe.create(**minimal_recipe_data)

        assert recipe.name == "Minimal Recipe"
        assert recipe.author_id == UserId(1)
        assert recipe.description is None
        assert recipe.difficulty == DifficultyLevel.MEDIUM  # Default
        assert recipe.cuisine is None

    def test_create_recipe_invalid_name(self):
        """Test recipe creation fails with invalid name."""
        test_cases = [
            ("", "EMPTY_NAME"),  # Empty name
            ("   ", "EMPTY_NAME"),  # Only whitespace
            ("A" * 201, "NAME_TOO_LONG"),  # Too long
        ]

        for invalid_name, error_code in test_cases:
            with pytest.raises(RecipeValidationException) as exc_info:
                Recipe.create(name=invalid_name, author_id=UserId(1))

            assert exc_info.value.error_code == error_code


class TestRecipeReconstruction:
    """Test cases for Recipe reconstruction functionality."""

    def test_reconstruct_recipe_success(self, sample_persisted_recipe_data):
        """Test successful recipe reconstruction from persisted data."""
        recipe = Recipe.reconstruct(**sample_persisted_recipe_data)

        assert recipe.id == RecipeId(1)
        assert recipe.name == "Persisted Recipe"
        assert recipe.author_id == UserId(1)
        assert recipe.version == 5
        assert recipe.created_at == datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert recipe.updated_at == datetime(2024, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
        assert recipe.is_deleted is False

    def test_reconstruct_deleted_recipe(self, sample_persisted_recipe_data):
        """Test reconstruction of a deleted recipe."""
        data = sample_persisted_recipe_data.copy()
        data["deleted_at"] = datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc)

        recipe = Recipe.reconstruct(**data)

        assert recipe.is_deleted is True
        assert recipe.deleted_at is not None


class TestRecipeBasicOperations:
    """Test cases for basic Recipe operations."""

    def test_set_name_success(self, sample_recipe):
        """Test successfully updating recipe name."""
        sample_recipe.set_name("Updated Recipe Name")

        assert sample_recipe.name == "Updated Recipe Name"
        assert sample_recipe.version == 2  # Version should increment

    def test_set_name_invalid(self, sample_recipe):
        """Test updating with invalid name fails."""
        with pytest.raises(RecipeValidationException):
            sample_recipe.set_name("")

    def test_update_basic_info(self, sample_recipe):
        """Test updating multiple basic info fields at once."""
        original_version = sample_recipe.version

        sample_recipe.update_basic_info(
            name="New Name",
            description="New description",
            difficulty=DifficultyLevel.HARD,
            cuisine=CuisineType.MEXICAN,
        )

        assert sample_recipe.name == "New Name"
        assert sample_recipe.description == "New description"
        assert sample_recipe.difficulty == DifficultyLevel.HARD
        assert sample_recipe.cuisine == CuisineType.MEXICAN
        assert (
            sample_recipe.version == original_version + 1
        )  # Only one version increment


class TestRecipeIngredientManagement:
    """Test cases for Recipe ingredient management."""

    def test_add_ingredient_success(self, sample_recipe, sample_ingredient):
        """Test successfully adding an ingredient to recipe."""
        original_ingredient_count = len(sample_recipe.ingredients)

        sample_recipe.add_ingredient(sample_ingredient)

        assert len(sample_recipe.ingredients) == original_ingredient_count + 1
        assert sample_recipe.ingredients[-1].name == "Tomato"
        assert sample_recipe.version == 2

    def test_add_duplicate_ingredient(
        self, sample_recipe_with_ingredients, sample_ingredient
    ):
        """Test adding duplicate ingredient fails."""
        recipe = sample_recipe_with_ingredients
        original_ingredient_count = len(recipe.ingredients)

        # Try to add ingredient with same ID
        with pytest.raises(ValueError) as exc_info:
            recipe.add_ingredient(sample_ingredient)

        assert "already exists" in str(exc_info.value).lower()
        assert len(recipe.ingredients) == original_ingredient_count

    def test_remove_ingredient_success(self, sample_recipe_with_ingredients):
        """Test successfully removing an ingredient from recipe."""
        recipe = sample_recipe_with_ingredients
        original_ingredient_count = len(recipe.ingredients)
        ingredient_id_to_remove = recipe.ingredients[0].id

        recipe.remove_ingredient(ingredient_id_to_remove)

        assert len(recipe.ingredients) == original_ingredient_count - 1
        assert all(ing.id != ingredient_id_to_remove for ing in recipe.ingredients)
        assert recipe.version == 3  # Initial + add + remove

    def test_remove_nonexistent_ingredient(self, sample_recipe):
        """Test removing nonexistent ingredient."""
        original_ingredient_count = len(sample_recipe.ingredients)
        nonexistent_id = IngredientId(999)

        sample_recipe.remove_ingredient(nonexistent_id)

        # Should not raise exception, just do nothing
        assert len(sample_recipe.ingredients) == original_ingredient_count


class TestRecipeStepManagement:
    """Test cases for Recipe step management."""

    def test_add_step_success(self, sample_recipe):
        """Test successfully adding a step to recipe."""
        original_step_count = len(sample_recipe.steps)

        step = Step(number=1, description="New step description", duration_minutes=5)
        sample_recipe.add_step(step)

        assert len(sample_recipe.steps) == original_step_count + 1
        assert sample_recipe.steps[-1].description == "New step description"
        assert sample_recipe.version == 2

    def test_reorder_steps_success(self, sample_recipe_with_steps):
        """Test successfully reordering recipe steps."""
        recipe = sample_recipe_with_steps
        original_step_order = [step.number for step in recipe.steps]

        # Reorder steps: [1, 2, 3] -> [3, 1, 2]
        new_order = [3, 1, 2]
        recipe.reorder_steps(new_order)

        new_step_order = [step.number for step in recipe.steps]
        assert new_step_order == [1, 2, 3]  # Should be renumbered sequentially
        assert [step.description for step in recipe.steps] == [
            "Third step",
            "First step",
            "Second step",
        ]

    def test_reorder_steps_invalid(self, sample_recipe_with_steps):
        """Test reordering steps with invalid order fails."""
        recipe = sample_recipe_with_steps

        # Invalid: wrong number of steps
        with pytest.raises(ValueError):
            recipe.reorder_steps([1, 2])  # Missing step 3

        # Invalid: duplicate numbers
        with pytest.raises(ValueError):
            recipe.reorder_steps([1, 1, 2])


class TestRecipeTagManagement:
    """Test cases for Recipe tag management."""

    def test_add_tag_success(self, sample_recipe):
        """Test successfully adding a tag to recipe."""
        original_tag_count = len(sample_recipe.tags)

        tag = Tag(name="new_tag", description="A new tag")
        sample_recipe.add_tag(tag)

        assert len(sample_recipe.tags) == original_tag_count + 1
        assert any(t.name == "new_tag" for t in sample_recipe.tags)
        assert sample_recipe.version == 2

    def test_remove_tag_success(self, sample_recipe_with_tags):
        """Test successfully removing a tag from recipe."""
        recipe = sample_recipe_with_tags
        original_tag_count = len(recipe.tags)
        tag_to_remove = next(iter(recipe.tags))

        recipe.remove_tag(tag_to_remove)

        assert len(recipe.tags) == original_tag_count - 1
        assert tag_to_remove not in recipe.tags

    def test_remove_nonexistent_tag(self, sample_recipe):
        """Test removing nonexistent tag."""
        original_tag_count = len(sample_recipe.tags)
        nonexistent_tag = Tag(name="nonexistent", description="Does not exist")

        sample_recipe.remove_tag(nonexistent_tag)

        # Should not raise exception, just do nothing
        assert len(sample_recipe.tags) == original_tag_count


class TestRecipeMetadataOperations:
    """Test cases for Recipe metadata operations."""

    def test_set_serving_info_success(self, sample_recipe):
        """Test successfully setting serving info."""
        serving_info = ServingInfo(servings=4, serving_size="1 cup")

        sample_recipe.set_serving_info(serving_info)

        assert sample_recipe.serving_info == serving_info
        assert sample_recipe.version == 2

    def test_set_cooking_time_success(self, sample_recipe):
        """Test successfully setting cooking time."""
        cooking_time = CookingTime(prep_minutes=15, cook_minutes=30)

        sample_recipe.set_cooking_time(cooking_time)

        assert sample_recipe.cooking_time == cooking_time
        assert sample_recipe.cooking_time.total_minutes == 45
        assert sample_recipe.version == 2

    def test_set_nutritional_info_success(self, sample_recipe):
        """Test successfully setting nutritional info."""
        nutritional_info = NutritionalInfo(
            calories=350, protein_g=Decimal("15.0"), carbs_g=Decimal("45.0")
        )

        sample_recipe.set_nutritional_info(nutritional_info)

        assert sample_recipe.nutritional_info == nutritional_info
        assert sample_recipe.version == 2


class TestRecipeCalculations:
    """Test cases for Recipe calculations."""

    def test_calculate_total_time_with_cooking_time(self, sample_recipe_with_metadata):
        """Test calculating total time when cooking time is set."""
        recipe = sample_recipe_with_metadata
        total_time = recipe.calculate_total_time()

        assert total_time == 45  # 15 prep + 30 cook

    def test_calculate_total_time_from_steps(self, sample_recipe_with_steps):
        """Test calculating total time from step durations."""
        recipe = sample_recipe_with_steps
        total_time = recipe.calculate_total_time()

        assert total_time == 25  # 10 + 5 + 10

    def test_get_nutritional_info_per_serving(self, sample_recipe_with_metadata):
        """Test calculating nutritional info per serving."""
        recipe = sample_recipe_with_metadata
        per_serving_info = recipe.get_nutritional_info_per_serving()

        assert per_serving_info is not None
        assert per_serving_info.calories == 87.5  # 350 / 4
        assert per_serving_info.protein_g == Decimal("3.75")  # 15 / 4

    def test_get_nutritional_info_no_serving_info(self, sample_recipe):
        """Test nutritional info per serving returns None when no serving info."""
        nutritional_info = NutritionalInfo(calories=350)
        sample_recipe.set_nutritional_info(nutritional_info)
        # Don't set serving info

        per_serving_info = sample_recipe.get_nutritional_info_per_serving()

        assert per_serving_info is None


class TestRecipeDietaryCompatibility:
    """Test cases for Recipe dietary compatibility."""

    def test_is_suitable_for_diet(self, sample_recipe_with_ingredients):
        """Test checking if recipe is suitable for specific diet."""
        recipe = sample_recipe_with_ingredients

        # All ingredients are vegan and vegetarian
        assert recipe.is_suitable_for_diet(DietType.VEGAN) is True
        assert recipe.is_suitable_for_diet(DietType.VEGETARIAN) is True

    def test_is_not_suitable_for_diet(self, sample_recipe_with_allergens):
        """Test recipe not suitable for specific diet."""
        recipe = sample_recipe_with_allergens

        # Recipe contains dairy and nuts, not suitable for vegan
        assert recipe.is_suitable_for_diet(DietType.VEGAN) is False

    def test_get_compatible_diets(self, sample_recipe_with_ingredients):
        """Test getting all compatible diets."""
        recipe = sample_recipe_with_ingredients
        compatible_diets = recipe.get_compatible_diets()

        assert DietType.VEGAN in compatible_diets
        assert DietType.VEGETARIAN in compatible_diets

    def test_get_allergens(self, sample_recipe_with_allergens):
        """Test getting all allergens present in recipe."""
        recipe = sample_recipe_with_allergens
        allergens = recipe.get_allergens()

        assert "dairy" in allergens
        assert "nuts" in allergens
        assert len(allergens) == 2


class TestRecipeTracking:
    """Test cases for Recipe tracking functionality."""

    def test_add_rating_success(self, sample_recipe):
        """Test successfully adding a rating."""
        original_rating_count = sample_recipe.rating_count

        sample_recipe.add_rating(4)

        assert sample_recipe.rating_count == original_rating_count + 1
        assert sample_recipe.average_rating == 4.0
        assert sample_recipe.version == 2

    def test_add_rating_invalid(self, sample_recipe):
        """Test adding invalid rating fails."""
        with pytest.raises(ValueError):
            sample_recipe.add_rating(6)  # Out of range

        with pytest.raises(ValueError):
            sample_recipe.add_rating(0)  # Out of range

    def test_increment_view_count(self, sample_recipe):
        """Test incrementing view count."""
        original_view_count = sample_recipe.view_count
        original_version = sample_recipe.version

        sample_recipe.increment_view_count()

        assert sample_recipe.view_count == original_view_count + 1
        assert (
            sample_recipe.version == original_version
        )  # No version increment for views

    def test_increment_favorite_count(self, sample_recipe):
        """Test incrementing favorite count."""
        original_favorite_count = sample_recipe.favorite_count

        sample_recipe.increment_favorite_count()

        assert sample_recipe.favorite_count == original_favorite_count + 1
        assert sample_recipe.version == 2


class TestRecipeDeletion:
    """Test cases for Recipe deletion functionality."""

    def test_soft_delete_success(self, sample_recipe):
        """Test successful soft deletion of recipe."""
        sample_recipe.soft_delete()

        assert sample_recipe.is_deleted is True
        assert sample_recipe.deleted_at is not None
        assert sample_recipe.version == 2

    def test_restore_success(self, sample_recipe):
        """Test successful restoration of deleted recipe."""
        # First delete
        sample_recipe.soft_delete()
        assert sample_recipe.is_deleted is True

        # Then restore
        sample_recipe.restore()

        assert sample_recipe.is_deleted is False
        assert sample_recipe.deleted_at is None
        assert sample_recipe.version == 3

    def test_operations_on_deleted_recipe_fail(self, sample_recipe):
        """Test operations fail on deleted recipe."""
        sample_recipe.soft_delete()

        # Try to modify deleted recipe
        with pytest.raises(RecipeDeletedException):
            sample_recipe.set_name("New Name")

        with pytest.raises(RecipeDeletedException):
            sample_recipe.add_ingredient(Mock(spec=Ingredient))

        with pytest.raises(RecipeDeletedException):
            sample_recipe.add_rating(5)


class TestRecipeRepresentation:
    """Test cases for Recipe string representation."""

    def test_repr(self, sample_recipe):
        """Test string representation of recipe."""
        repr_str = repr(sample_recipe)

        assert sample_recipe.name in repr_str
        assert str(sample_recipe.id.value) in repr_str
        assert "version" in repr_str

    def test_str(self, sample_recipe):
        """Test user-friendly string representation."""
        str_repr = str(sample_recipe)

        assert sample_recipe.name in str_repr
        assert sample_recipe.author_id.value in str_repr
        assert sample_recipe.difficulty.value in str_repr

    def test_equality(self):
        """Test recipe equality based on ID."""
        recipe1 = Recipe.create(name="Recipe 1", author_id=UserId(1))
        recipe2 = Recipe.create(name="Recipe 2", author_id=UserId(2))

        # Different IDs should not be equal
        assert recipe1 != recipe2

        # Same ID should make them equal (need to reconstruct with same ID)
        same_id = RecipeId(1)
        reconstructed1 = Recipe.reconstruct(
            id=same_id,
            name=recipe1.name,
            author_id=recipe1.author_id,
            description=recipe1.description,
            difficulty=recipe1.difficulty,
            cuisine=recipe1.cuisine,
            ingredients=recipe1.ingredients,
            steps=recipe1.steps,
            tags=recipe1.tags,
            meal_types=recipe1.meal_types,
            serving_info=recipe1.serving_info,
            cooking_time=recipe1.cooking_time,
            nutritional_info=recipe1.nutritional_info,
            rating_sum=0,
            rating_count=0,
            view_count=0,
            favorite_count=0,
            version=1,
            created_at=recipe1.created_at,
            updated_at=recipe1.updated_at,
            deleted_at=recipe1.deleted_at,
        )
        reconstructed2 = Recipe.reconstruct(
            id=same_id,
            name=recipe2.name,
            author_id=recipe2.author_id,
            description=recipe2.description,
            difficulty=recipe2.difficulty,
            cuisine=recipe2.cuisine,
            ingredients=recipe2.ingredients,
            steps=recipe2.steps,
            tags=recipe2.tags,
            meal_types=recipe2.meal_types,
            serving_info=recipe2.serving_info,
            cooking_time=recipe2.cooking_time,
            nutritional_info=recipe2.nutritional_info,
            rating_sum=0,
            rating_count=0,
            view_count=0,
            favorite_count=0,
            version=1,
            created_at=recipe2.created_at,
            updated_at=recipe2.updated_at,
            deleted_at=recipe2.deleted_at,
        )

        assert reconstructed1 == reconstructed2


# ===== INTEGRATION TESTS =====


class TestRecipeIntegration:
    """Integration tests for Recipe functionality."""

    def test_complete_recipe_lifecycle(self):
        """Test complete recipe lifecycle from creation to deletion."""
        # Create recipe
        recipe = Recipe.create(
            name="Integration Test Recipe",
            author_id=UserId(1),
            description="A recipe for integration testing",
            difficulty=DifficultyLevel.EASY,
            cuisine=CuisineType.MEXICAN,
        )

        assert recipe.version == 1
        assert recipe.is_deleted is False

        # Add ingredients
        ingredient1 = Ingredient.create(
            name="Rice",
            quantity=Quantity(value=Decimal("200.0"), unit="grams"),
            properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
            is_optional=False,
            substitutes=[],
        )
        recipe.add_ingredient(ingredient1)

        # Add steps
        step1 = Step(number=1, description="Wash the rice", duration_minutes=2)
        recipe.add_step(step1)

        # Add tags
        tag1 = Tag(name="easy", description="Easy to make")
        recipe.add_tag(tag1)

        # Add meal types
        recipe.add_meal_type(MealType.DINNER)

        # Set metadata
        cooking_time = CookingTime(prep_minutes=5, cook_minutes=15)
        recipe.set_cooking_time(cooking_time)

        # Add ratings
        recipe.add_rating(5)
        recipe.add_rating(4)

        # Increment views and favorites
        recipe.increment_view_count()
        recipe.increment_favorite_count()

        # Verify final state
        assert recipe.version > 1
        assert len(recipe.ingredients) == 1
        assert len(recipe.steps) == 1
        assert len(recipe.tags) == 1
        assert len(recipe.meal_types) == 1
        assert recipe.cooking_time is not None
        assert recipe.average_rating == 4.5
        assert recipe.view_count == 1
        assert recipe.favorite_count == 1

        # Soft delete
        recipe.soft_delete()
        assert recipe.is_deleted is True

        # Restore
        recipe.restore()
        assert recipe.is_deleted is False

    def test_recipe_with_complex_operations(self, sample_recipe_with_metadata):
        """Test complex operations on a recipe with full metadata."""
        recipe = sample_recipe_with_metadata

        # Test nutritional calculations
        per_serving = recipe.get_nutritional_info_per_serving()
        assert per_serving is not None
        assert per_serving.calories == 87.5

        # Test time calculations
        total_time = recipe.calculate_total_time()
        assert total_time == 45

        # Test dietary compatibility
        compatible_diets = recipe.get_compatible_diets()
        assert isinstance(compatible_diets, set)

        # Test allergen detection
        allergens = recipe.get_allergens()
        assert isinstance(allergens, set)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
