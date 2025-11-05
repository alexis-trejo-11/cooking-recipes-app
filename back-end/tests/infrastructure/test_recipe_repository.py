import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.receipt.infrastructure.persistence.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)
from app.receipt.infrastructure.persistence.mapper import RecipeMapper
from app.receipt.domain.entities.recipe import Recipe
from app.receipt.domain.entities.ingredient import Ingredient, IngredientProperties
from app.receipt.domain.entities.value_objects import (
    RecipeId,
    IngredientId,
    Quantity,
    Tag,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
)
from app.auth.domain.user import UserId
from app.receipt.domain.entities.enums import DifficultyLevel, CuisineType, MealType
from tests.infrastructure.test_sqlalchemy_repository import db_session


@pytest.fixture
def sample_recipe():
    """Create sample recipe for testing"""
    return Recipe.create(
        name="Test Recipe",
        author_id=UserId(1),
        description="A test recipe description",
        difficulty=DifficultyLevel.MEDIUM,
        cuisine=CuisineType.ITALIAN,
    )


@pytest.fixture
def sample_ingredient():
    """Create sample ingredient for testing"""
    properties = IngredientProperties(
        is_vegan=True,
        is_vegetarian=True,
        is_gluten_free=True,
        is_dairy_free=True,
        allergens={"gluten"},
    )

    return Ingredient.reconstruct(
        id=IngredientId(1),
        name="Test Ingredient",
        quantity=Quantity(value=Decimal("100.0"), unit="grams"),
        properties=properties,
        is_optional=False,
        substitutes=["Substitute 1", "Substitute 2"],
    )


class TestRecipeMapper:

    def test_entity_to_dict(self, sample_recipe):
        """Test converting recipe entity to dictionary"""
        # Add some data to the recipe
        sample_recipe.set_serving_info(ServingInfo(servings=4))
        sample_recipe.set_cooking_time(CookingTime(prep_minutes=15, cook_minutes=30))
        sample_recipe.set_nutritional_info(
            NutritionalInfo(
                calories=500,
                protein_g=Decimal("25.0"),
                carbs_g=Decimal("60.0"),
                fat_g=Decimal("20.0"),
            )
        )

        result = RecipeMapper.entity_to_dict(sample_recipe)

        assert result["name"] == "Test Recipe"
        assert result["author_id"] == 1
        assert result["serving_size"] == 4
        assert result["prep_time_minutes"] == 15
        assert result["cook_time_minutes"] == 30
        assert result["calories"] == 500
        assert result["protein_g"] == Decimal("25.0")


class TestSQLAlchemyRecipeRepository:

    @pytest.mark.asyncio
    async def test_save_and_get_recipe(self, db_session, sample_recipe):
        """Test saving and retrieving recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        assert retrieved_recipe.name == sample_recipe.name
        assert retrieved_recipe.description == sample_recipe.description
        assert retrieved_recipe.difficulty == sample_recipe.difficulty
        assert retrieved_recipe.id.value == saved_recipe.id.value

    @pytest.mark.asyncio
    async def test_save_recipe_with_ingredients(
        self, db_session, sample_recipe, sample_ingredient
    ):
        """Test saving recipe with ingredients"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add ingredient to recipe
        sample_recipe.add_ingredient(sample_ingredient)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        ingredients = retrieved_recipe.get_ingredients()
        assert len(ingredients) == 1
        assert ingredients[0].name == "Test Ingredient"
        assert ingredients[0].quantity.value == Decimal("100.0")

    @pytest.mark.asyncio
    async def test_save_recipe_with_steps(self, db_session, sample_recipe):
        """Test saving recipe with steps"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add steps to recipe
        sample_recipe.add_step("First step description", duration_minutes=5)
        sample_recipe.add_step("Second step description", technique="stirring")

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        steps = retrieved_recipe.get_steps()
        assert len(steps) == 2
        assert steps[0].description == "First step description"
        assert steps[0].duration_minutes == 5
        assert steps[1].description == "Second step description"
        assert steps[1].technique == "stirring"

    @pytest.mark.asyncio
    async def test_save_recipe_with_tags(self, db_session, sample_recipe):
        """Test saving recipe with tags"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add tags to recipe
        sample_recipe.add_tag(Tag(name="healthy", description="Healthy food"))
        sample_recipe.add_tag(Tag(name="quick", description="Quick to prepare"))

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        tags = retrieved_recipe.get_tags()
        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert "healthy" in tag_names
        assert "quick" in tag_names

    @pytest.mark.asyncio
    async def test_save_recipe_with_meal_types(self, db_session, sample_recipe):
        """Test saving recipe with meal types"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add meal types to recipe
        sample_recipe.add_meal_type(MealType.DINNER)
        sample_recipe.add_meal_type(MealType.LUNCH)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        meal_types = retrieved_recipe.get_meal_types()
        assert len(meal_types) == 2
        assert MealType.DINNER in meal_types
        assert MealType.LUNCH in meal_types

    @pytest.mark.asyncio
    async def test_update_recipe(self, db_session, sample_recipe):
        """Test updating recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save initial recipe
        saved_recipe = await repository.save(sample_recipe)

        updated_recipe_data = Recipe.reconstruct(
            id=saved_recipe.id,
            name="Updated Recipe Name",
            author_id=saved_recipe.author_id,
            description="Updated description",
            difficulty=saved_recipe.difficulty,
            cuisine=saved_recipe.cuisine,
            ingredients=saved_recipe.get_ingredients(),
            steps=saved_recipe.get_steps(),
            tags=saved_recipe.get_tags(),
            meal_types=saved_recipe.get_meal_types(),
            serving_info=saved_recipe.get_serving_info(),
            cooking_time=saved_recipe.get_cooking_time(),
            nutritional_info=saved_recipe.get_nutritional_info(),
            rating_sum=saved_recipe._rating_sum,
            rating_count=saved_recipe._rating_count,
            view_count=saved_recipe._view_count,
            favorite_count=saved_recipe._favorite_count,
            version=saved_recipe.version,
            created_at=saved_recipe.get_created_at(),
            updated_at=saved_recipe.get_updated_at(),
            deleted_at=saved_recipe.deleted_at,
        )

        # Update recipe
        updated_recipe = await repository.save(updated_recipe_data)

        # Retrieve and verify
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe.name == "Updated Recipe Name"
        assert retrieved_recipe.description == "Updated description"
        assert retrieved_recipe.version == 2  # Version should increment

    @pytest.mark.asyncio
    async def test_delete_recipe(self, db_session, sample_recipe):
        """Test soft deleting recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        saved_recipe = await repository.save(sample_recipe)

        # Verify recipe exists
        recipe_exists = await repository.get_by_id(saved_recipe.id)
        assert recipe_exists is not None

        # Delete recipe
        deleted = await repository.delete(saved_recipe.id)
        assert deleted is True

        # Verify recipe is soft deleted
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)
        assert retrieved_recipe is None

    @pytest.mark.asyncio
    async def test_list_all_recipes(self, db_session, sample_recipe):
        """Test listing all recipes"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Should be empty initially
        recipes = await repository.list_all()
        assert len(recipes) == 0

        # Save multiple recipes
        recipe1 = await repository.save(sample_recipe)

        recipe2 = Recipe.create(
            name="Second Recipe",
            author_id=UserId(1),
            description="Another test recipe",
            difficulty=DifficultyLevel.EASY,
        )
        await repository.save(recipe2)

        # List recipes
        recipes = await repository.list_all()

        assert len(recipes) == 2
        names = [recipe.name for recipe in recipes]
        assert "Test Recipe" in names
        assert "Second Recipe" in names

    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session, sample_recipe):
        """Test searching recipes by name"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save test recipe
        await repository.save(sample_recipe)

        # Search by name
        recipes = await repository.search_by_name("Test")
        assert len(recipes) == 1
        assert recipes[0].name == "Test Recipe"

        # Search with no results
        recipes = await repository.search_by_name("Nonexistent")
        assert len(recipes) == 0

    @pytest.mark.asyncio
    async def test_get_by_author(self, db_session):
        """Test getting recipes by author"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create recipes for different authors
        recipe1 = Recipe.create(
            name="Author 1 Recipe",
            author_id=UserId(1),
            description="Recipe by author 1",
        )
        await repository.save(recipe1)

        recipe2 = Recipe.create(
            name="Author 2 Recipe",
            author_id=UserId(2),
            description="Recipe by author 2",
        )
        await repository.save(recipe2)

        # Get recipes by author 1
        author1_recipes = await repository.get_by_author(UserId(1))
        assert len(author1_recipes) == 1
        assert author1_recipes[0].name == "Author 1 Recipe"

        # Get recipes by author 2
        author2_recipes = await repository.get_by_author(UserId(2))
        assert len(author2_recipes) == 1
        assert author2_recipes[0].name == "Author 2 Recipe"

    @pytest.mark.asyncio
    async def test_exists_by_name_and_author(self, db_session, sample_recipe):
        """Test checking if recipe exists by name and author"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Should not exist before saving
        exists = await repository.exists_by_name_and_author("Test Recipe", UserId(1))
        assert exists is False

        # Save recipe
        await repository.save(sample_recipe)

        # Should exist after saving
        exists = await repository.exists_by_name_and_author("Test Recipe", UserId(1))
        assert exists is True

        # Check with different author
        exists = await repository.exists_by_name_and_author("Test Recipe", UserId(2))
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_nonexistent_recipe(self, db_session):
        """Test getting recipe that doesn't exist"""
        repository = SQLAlchemyRecipeRepository(db_session)

        recipe = await repository.get_by_id(RecipeId(999))
        assert recipe is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_recipe(self, db_session):
        """Test deleting recipe that doesn't exist"""
        repository = SQLAlchemyRecipeRepository(db_session)

        deleted = await repository.delete(RecipeId(999))
        assert deleted is False

    @pytest.mark.asyncio
    async def test_recipe_with_nutritional_info(self, db_session, sample_recipe):
        """Test recipe with nutritional information"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add nutritional info
        sample_recipe.set_nutritional_info(
            NutritionalInfo(
                calories=350,
                protein_g=Decimal("20.5"),
                carbs_g=Decimal("45.2"),
                fat_g=Decimal("12.3"),
            )
        )

        saved_recipe = await repository.save(sample_recipe)
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        assert retrieved_recipe.get_nutritional_info() is not None
        nutritional_info = retrieved_recipe.get_nutritional_info()
        assert nutritional_info.calories == 350
        assert nutritional_info.protein_g == Decimal("20.5")
        assert nutritional_info.carbs_g == Decimal("45.2")

    @pytest.mark.asyncio
    async def test_recipe_complex_operations(self, db_session):
        """Test complex recipe operations with all components"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create a complex recipe
        recipe = Recipe.create(
            name="Complex Test Recipe",
            author_id=UserId(1),
            description="A complex recipe with all features",
            difficulty=DifficultyLevel.HARD,
            cuisine=CuisineType.MEXICAN,
        )

        # Add serving info
        recipe.set_serving_info(ServingInfo(servings=6))

        # Add cooking time
        recipe.set_cooking_time(CookingTime(prep_minutes=20, cook_minutes=45))

        # Add ingredients
        properties1 = IngredientProperties(
            is_vegan=True, is_vegetarian=True, allergens=set()
        )
        ingredient1 = Ingredient.reconstruct(
            id=IngredientId(1),
            name="Tomatoes",
            quantity=Quantity(value=Decimal("500.0"), unit="grams"),
            properties=properties1,
            is_optional=False,
            substitutes=[],
        )

        properties2 = IngredientProperties(
            is_vegan=False, is_vegetarian=True, allergens={"dairy"}
        )
        ingredient2 = Ingredient.reconstruct(
            id=IngredientId(2),
            name="Cheese",
            quantity=Quantity(value=Decimal("200.0"), unit="grams"),
            properties=properties2,
            is_optional=True,
            substitutes=[],
        )

        recipe.add_ingredient(ingredient1)
        recipe.add_ingredient(ingredient2)

        # Add steps
        recipe.add_step("Chop tomatoes", duration_minutes=10)
        recipe.add_step("Grate cheese", duration_minutes=5)
        recipe.add_step("Mix ingredients", technique="stirring")

        # Add tags and meal types
        recipe.add_tag(Tag(name="mexican", description="Mexican cuisine"))
        recipe.add_meal_type(MealType.DINNER)
        recipe.add_meal_type(MealType.LUNCH)

        # Save and retrieve
        saved_recipe = await repository.save(recipe)
        retrieved_recipe = await repository.get_by_id(saved_recipe.id)

        # Verify all components
        assert retrieved_recipe.name == "Complex Test Recipe"
        assert retrieved_recipe.difficulty == DifficultyLevel.HARD
        assert retrieved_recipe.cuisine == CuisineType.MEXICAN

        assert retrieved_recipe.get_serving_info().servings == 6
        assert retrieved_recipe.get_cooking_time().total_minutes == 65

        ingredients = retrieved_recipe.get_ingredients()
        assert len(ingredients) == 2

        steps = retrieved_recipe.get_steps()
        assert len(steps) == 3

        tags = retrieved_recipe.get_tags()
        assert len(tags) == 1

        meal_types = retrieved_recipe.get_meal_types()
        assert len(meal_types) == 2
