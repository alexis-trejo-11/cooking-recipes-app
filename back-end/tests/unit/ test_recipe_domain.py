import pytest
from decimal import Decimal

from app.domain.entities.ingredient import Ingredient, IngredientProperties
from app.domain.entities.value_objects import IngredientId, Quantity
from app.domain.entities.enums import DietType
from app.application.exceptions import RecipeValidationException

# conftest.py
import pytest
from datetime import datetime, timezone
from decimal import Decimal

from app.domain.entities.recipe import Recipe
from app.domain.entities.ingredient import Ingredient, IngredientProperties
from app.domain.entities.value_objects import (
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
from app.domain.entities.enums import DifficultyLevel, CuisineType, MealType, DietType


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
def sample_recipe_with_ingredients(sample_recipe):
    """Sample recipe with ingredients."""
    ingredients = [
        Ingredient.reconstruct(
            id=IngredientId(1),
            name="Tomato",
            quantity=Quantity(value=Decimal("200.0"), unit="grams"),
            properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
            is_optional=False,
            substitutes=[],
        ),
        Ingredient.reconstruct(
            id=IngredientId(2),
            name="Onion",
            quantity=Quantity(value=Decimal("100.0"), unit="grams"),
            properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
            is_optional=False,
            substitutes=[],
        ),
    ]

    for ingredient in ingredients:
        sample_recipe.add_ingredient(ingredient)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_mixed_ingredients(sample_recipe):
    """Sample recipe with mixed optional and required ingredients."""
    ingredients = [
        Ingredient.reconstruct(
            id=IngredientId(1),
            name="Required Ingredient",
            quantity=Quantity(value=Decimal("200.0"), unit="grams"),
            properties=IngredientProperties(),
            is_optional=False,
            substitutes=[],
        ),
        Ingredient.reconstruct(
            id=IngredientId(2),
            name="Optional Ingredient",
            quantity=Quantity(value=Decimal("100.0"), unit="grams"),
            properties=IngredientProperties(),
            is_optional=True,
            substitutes=[],
        ),
        Ingredient.reconstruct(
            id=IngredientId(3),
            name="Another Required",
            quantity=Quantity(value=Decimal("150.0"), unit="grams"),
            properties=IngredientProperties(),
            is_optional=False,
            substitutes=[],
        ),
    ]

    for ingredient in ingredients:
        sample_recipe.add_ingredient(ingredient)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_allergens(sample_recipe):
    """Sample recipe with allergens."""
    ingredients = [
        Ingredient.reconstruct(
            id=IngredientId(1),
            name="Cheese",
            quantity=Quantity(value=Decimal("100.0"), unit="grams"),
            properties=IngredientProperties(allergens={"dairy"}),
            is_optional=False,
            substitutes=[],
        ),
        Ingredient.reconstruct(
            id=IngredientId(2),
            name="Nuts",
            quantity=Quantity(value=Decimal("50.0"), unit="grams"),
            properties=IngredientProperties(allergens={"nuts"}),
            is_optional=False,
            substitutes=[],
        ),
    ]

    for ingredient in ingredients:
        sample_recipe.add_ingredient(ingredient)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_steps(sample_recipe):
    """Sample recipe with steps."""
    steps = [
        ("First step", 10, None, None),
        ("Second step", 5, "mixing", None),
        ("Third step", 10, None, "180°C"),
    ]

    for description, duration, technique, temperature in steps:
        sample_recipe.add_step(description, duration, technique, temperature)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_tags(sample_recipe):
    """Sample recipe with tags."""
    tags = [
        Tag(name="healthy", description="Healthy food"),
        Tag(name="quick", description="Quick to prepare"),
        Tag(name="vegetarian", description="Vegetarian meal"),
    ]

    for tag in tags:
        sample_recipe.add_tag(tag)

    return sample_recipe


@pytest.fixture
def sample_recipe_with_meal_types(sample_recipe):
    """Sample recipe with meal types."""
    sample_recipe.add_meal_type(MealType.BREAKFAST)
    sample_recipe.add_meal_type(MealType.LUNCH)
    return sample_recipe


@pytest.fixture
def sample_persisted_ingredient_data():
    """Sample data for ingredient reconstruction."""
    return {
        "id": IngredientId(1),
        "name": "Persisted Ingredient",
        "quantity": Quantity(value=Decimal("150.0"), unit="ml"),
        "properties": IngredientProperties(is_vegan=False, is_vegetarian=True),
        "is_optional": True,
        "substitutes": ["Alternative"],
    }


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


class TestIngredientCreation:
    """Test cases for Ingredient creation functionality."""

    def test_create_ingredient_success(self, sample_ingredient):
        """Test successful ingredient creation with valid data."""
        ingredient = Ingredient.create(**sample_ingredient)

        assert ingredient.name == "Tomato"
        assert ingredient.quantity == Quantity(value=Decimal("200.0"), unit="grams")
        assert ingredient.properties.is_vegan is True
        assert ingredient.properties.is_vegetarian is True
        assert ingredient.is_optional is False
        assert ingredient.substitutes == []

    def test_create_ingredient_with_substitutes(self, sample_ingredient_data):
        """Test ingredient creation with substitutes."""
        data = sample_ingredient_data.copy()
        data["substitutes"] = ["Cherry tomatoes", "Canned tomatoes"]

        ingredient = Ingredient.create(**data)

        assert len(ingredient.substitutes) == 2
        assert "Cherry tomatoes" in ingredient.substitutes

    def test_create_ingredient_optional(self, sample_ingredient_data):
        """Test creating optional ingredient."""
        data = sample_ingredient_data.copy()
        data["is_optional"] = True

        ingredient = Ingredient.create(**data)

        assert ingredient.is_optional is True

    def test_create_ingredient_invalid_name(self, sample_ingredient_data):
        """Test ingredient creation fails with invalid name."""
        test_cases = [
            "",  # Empty name
            "   ",  # Only whitespace
            "A" * 101,  # Too long
        ]

        for invalid_name in test_cases:
            data = sample_ingredient_data.copy()
            data["name"] = invalid_name

            with pytest.raises(RecipeValidationException) as exc_info:
                Ingredient.create(**data)

            error_message = str(exc_info.value).lower()
            assert "name" in error_message

    def test_create_ingredient_negative_quantity(self, sample_ingredient_data):
        """Test ingredient creation fails with negative quantity."""
        data = sample_ingredient_data.copy()
        data["quantity"] = Quantity(value=Decimal("-1.0"), unit="grams")

        with pytest.raises(RecipeValidationException):
            Ingredient.create(**data)


class TestIngredientReconstruction:
    """Test cases for Ingredient reconstruction functionality."""

    def test_reconstruct_ingredient_success(self, sample_persisted_ingredient_data):
        """Test successful ingredient reconstruction from persisted data."""
        ingredient = Ingredient.reconstruct(**sample_persisted_ingredient_data)

        assert ingredient.id == IngredientId(1)
        assert ingredient.name == "Persisted Ingredient"
        assert ingredient.quantity == Quantity(value=Decimal("150.0"), unit="ml")
        assert ingredient.properties.is_vegan is False
        assert ingredient.is_optional is True
        assert ingredient.substitutes == ["Alternative"]

    def test_reconstruct_ingredient_invalid_id(self, sample_persisted_ingredient_data):
        """Test reconstruction fails with invalid ID."""
        data = sample_persisted_ingredient_data.copy()
        data["id"] = IngredientId(-1)  # Invalid ID

        with pytest.raises(RecipeValidationException) as exc_info:
            Ingredient.reconstruct(**data)

        error_message = str(exc_info.value).lower()
        assert "id" in error_message


class TestIngredientDietaryCompatibility:
    """Test cases for Ingredient dietary compatibility."""

    def test_is_suitable_for_diet(self, sample_ingredient):
        """Test checking if ingredient is suitable for specific diet."""
        # Test with vegan ingredient
        vegan_properties = IngredientProperties(is_vegan=True, is_vegetarian=True)
        vegan_ingredient = Ingredient.create(
            name="Vegan Ingredient",
            quantity=Quantity(value=Decimal("100.0"), unit="grams"),
            properties=vegan_properties,
        )

        assert vegan_ingredient.is_suitable_for(DietType.VEGAN) is True
        assert vegan_ingredient.is_suitable_for(DietType.VEGETARIAN) is True

    def test_is_not_suitable_for_diet(self, sample_ingredient):
        """Test ingredient not suitable for specific diet."""
        non_vegan_properties = IngredientProperties(is_vegan=False, is_vegetarian=True)
        non_vegan_ingredient = Ingredient.create(
            name="Non-Vegan Ingredient",
            quantity=Quantity(value=Decimal("100.0"), unit="grams"),
            properties=non_vegan_properties,
        )

        assert non_vegan_ingredient.is_suitable_for(DietType.VEGAN) is False
        assert non_vegan_ingredient.is_suitable_for(DietType.VEGETARIAN) is True


class TestIngredientScaling:
    """Test cases for Ingredient quantity scaling."""

    def test_scale_quantity_success(self, sample_ingredient):
        """Test successfully scaling ingredient quantity."""
        scaled_ingredient = sample_ingredient.scale_quantity(Decimal("2.0"))

        assert scaled_ingredient.quantity.value == Decimal("400.0")  # 200 * 2
        assert scaled_ingredient.quantity.unit == "grams"
        assert scaled_ingredient.name == sample_ingredient.name
        assert scaled_ingredient.properties == sample_ingredient.properties

    def test_scale_quantity_negative_factor(self, sample_ingredient):
        """Test scaling with negative factor fails."""
        with pytest.raises(RecipeValidationException) as exc_info:
            sample_ingredient.scale_quantity(Decimal("-1.0"))

        error_message = str(exc_info.value).lower()
        assert "factor" in error_message or "negative" in error_message

    def test_scale_quantity_zero_factor(self, sample_ingredient):
        """Test scaling with zero factor."""
        scaled_ingredient = sample_ingredient.scale_quantity(Decimal("0.0"))

        assert scaled_ingredient.quantity.value == Decimal("0.0")


class TestIngredientUpdates:
    """Test cases for Ingredient update methods."""

    def test_update_name_success(self, sample_ingredient):
        """Test successfully updating ingredient name."""
        updated_ingredient = sample_ingredient.update_name("Updated Tomato")

        assert updated_ingredient.name == "Updated Tomato"
        assert updated_ingredient.quantity == sample_ingredient.quantity
        assert updated_ingredient.id == sample_ingredient.id

    def test_update_name_invalid(self, sample_ingredient):
        """Test updating with invalid name fails."""
        with pytest.raises(RecipeValidationException):
            sample_ingredient.update_name("")

    def test_update_quantity_success(self, sample_ingredient):
        """Test successfully updating ingredient quantity."""
        new_quantity = Quantity(value=Decimal("300.0"), unit="kilograms")
        updated_ingredient = sample_ingredient.update_quantity(new_quantity)

        assert updated_ingredient.quantity == new_quantity
        assert updated_ingredient.name == sample_ingredient.name

    def test_update_properties_success(self, sample_ingredient):
        """Test successfully updating ingredient properties."""
        new_properties = IngredientProperties(
            is_vegan=False, is_vegetarian=True, allergens={"dairy"}
        )
        updated_ingredient = sample_ingredient.update_properties(new_properties)

        assert updated_ingredient.properties == new_properties
        assert updated_ingredient.name == sample_ingredient.name

    def test_mark_as_optional(self, sample_ingredient):
        """Test marking ingredient as optional."""
        updated_ingredient = sample_ingredient.mark_as_optional()

        assert updated_ingredient.is_optional is True
        assert updated_ingredient.name == sample_ingredient.name

    def test_mark_as_required(self, sample_ingredient):
        """Test marking ingredient as required."""
        optional_ingredient = sample_ingredient.mark_as_optional()
        required_ingredient = optional_ingredient.mark_as_required()

        assert required_ingredient.is_optional is False

    def test_add_substitute_success(self, sample_ingredient):
        """Test successfully adding a substitute."""
        updated_ingredient = sample_ingredient.add_substitute("Cherry tomatoes")

        assert len(updated_ingredient.substitutes) == 1
        assert "Cherry tomatoes" in updated_ingredient.substitutes

    def test_add_substitute_invalid(self, sample_ingredient):
        """Test adding invalid substitute fails."""
        with pytest.raises(RecipeValidationException):
            sample_ingredient.add_substitute("")

    def test_remove_substitute_success(self, sample_ingredient):
        """Test successfully removing a substitute."""
        # First add a substitute
        with_substitute = sample_ingredient.add_substitute("Cherry tomatoes")
        # Then remove it
        without_substitute = with_substitute.remove_substitute("Cherry tomatoes")

        assert len(without_substitute.substitutes) == 0

    def test_remove_nonexistent_substitute(self, sample_ingredient):
        """Test removing nonexistent substitute."""
        updated_ingredient = sample_ingredient.remove_substitute("Nonexistent")

        assert len(updated_ingredient.substitutes) == 0


class TestIngredientRepresentation:
    """Test cases for Ingredient string representation."""

    def test_repr(self, sample_ingredient):
        """Test string representation of ingredient."""
        repr_str = repr(sample_ingredient)

        assert sample_ingredient.name in repr_str
        assert str(sample_ingredient.id.value) in repr_str
        assert "is_optional" in repr_str

    def test_str(self, sample_ingredient):
        """Test user-friendly string representation."""
        str_repr = str(sample_ingredient)

        assert sample_ingredient.quantity.value in str_repr
        assert sample_ingredient.quantity.unit in str_repr
        assert sample_ingredient.name in str_repr

    def test_str_optional_ingredient(self, sample_ingredient):
        """Test string representation of optional ingredient."""
        optional_ingredient = sample_ingredient.mark_as_optional()
        str_repr = str(optional_ingredient)

        assert "(optional)" in str_repr

    def test_equality(self, sample_ingredient_data):
        """Test ingredient equality based on ID."""
        ingredient1 = Ingredient.create(**sample_ingredient_data)
        ingredient2 = Ingredient.create(**sample_ingredient_data)

        # Different instances with same data but no ID should not be equal
        assert ingredient1 != ingredient2

        # Same ID should make them equal
        same_id = IngredientId(1)
        # We'd need to reconstruct with same ID to test this properly
        reconstructed1 = Ingredient.reconstruct(
            id=same_id,
            name=ingredient1.name,
            quantity=ingredient1.quantity,
            properties=ingredient1.properties,
            is_optional=ingredient1.is_optional,
            substitutes=ingredient1.substitutes,
        )
        reconstructed2 = Ingredient.reconstruct(
            id=same_id,
            name=ingredient2.name,
            quantity=ingredient2.quantity,
            properties=ingredient2.properties,
            is_optional=ingredient2.is_optional,
            substitutes=ingredient2.substitutes,
        )

        assert reconstructed1 == reconstructed2
