import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.recipe.infrastructure.persistence.repository import (
    SQLAlchemyRecipeRepository,
)
from app.modules.recipe.infrastructure.persistence.mapper import RecipeMapper
from app.modules.recipe.domain.models.entities.recipe import Recipe
from app.modules.recipe.domain.models.entities.ingredient import (
    Ingredient,
    IngredientProperties,
)
from app.modules.recipe.domain.models.value_objects.value_objects_standard import (
    RecipeId,
    IngredientId,
    Quantity,
    Step,
    Tag,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.value_objects.enums import (
    DifficultyLevel,
    CuisineType,
    MealType,
)
from app.utils.core.pagination import PaginationParams
from app.utils.core.specification import Specification
from app.modules.recipe.application.exceptions import RecipeNotFoundException
from tests.infrastructure.test_sqlalchemy_repository import db_session


@pytest.fixture
def sample_recipe():
    """Create sample recipe for testing"""
    return Recipe.create(
        name="Test Recipe",
        author_id=UserId(1),
        difficulty=DifficultyLevel.MEDIUM,
        meal_types={MealType.DINNER, MealType.LUNCH},
        description="A test recipe description",
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
        substitutes=["Alternative Ingredient"],
    )


class TestRecipeMapper:
    """Tests for RecipeMapper"""

    def test_entity_to_dict(self, sample_recipe):
        """Test converting recipe entity to dictionary"""
        # Add some data to the recipe
        sample_recipe.update_serving_info(ServingInfo(servings=4))
        sample_recipe.update_cooking_time(CookingTime(prep_minutes=15, cook_minutes=30))
        sample_recipe.update_nutritional_info(
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
        assert result["servings"] == 4
        assert result["prep_time_minutes"] == 15
        assert result["cook_time_minutes"] == 30
        assert result["calories"] == 500
        assert result["protein_g"] == Decimal("25.0")


class TestSQLAlchemyRecipeRepository:
    """Tests for SQLAlchemyRecipeRepository"""

    # ========================================================================
    # BASIC CRUD OPERATIONS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, db_session, sample_recipe):
        """Test saving and retrieving recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Verify saved recipe has ID
        assert saved_recipe.id is not None
        assert saved_recipe.id.value > 0

        # Retrieve recipe
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        assert retrieved_recipe.name == sample_recipe.name
        assert retrieved_recipe.description == sample_recipe.description
        assert retrieved_recipe.difficulty == sample_recipe.difficulty
        assert retrieved_recipe.id.value == saved_recipe.id.value

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent(self, db_session):
        """Test finding recipe that doesn't exist"""
        repository = SQLAlchemyRecipeRepository(db_session)

        recipe = await repository.find_by_id(RecipeId(99999))
        assert recipe is None

    @pytest.mark.asyncio
    async def test_find_by_id_and_author(self, db_session, sample_recipe):
        """Test finding recipe by ID and author"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Find with correct author
        found = await repository.find_by_id_and_author(saved_recipe.id, UserId(1))
        assert found is not None
        assert found.id == saved_recipe.id

        # Find with incorrect author
        not_found = await repository.find_by_id_and_author(saved_recipe.id, UserId(999))
        assert not_found is None

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
    async def test_delete_recipe(self, db_session, sample_recipe):
        """Test soft deleting recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        saved_recipe = await repository.save(sample_recipe)

        # Verify recipe exists
        recipe_exists = await repository.find_by_id(saved_recipe.id)
        assert recipe_exists is not None

        # Delete recipe
        deleted = await repository.delete(saved_recipe.id)
        assert deleted is True

        # Verify recipe is soft deleted (not found)
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_recipe(self, db_session):
        """Test deleting recipe that doesn't exist"""
        repository = SQLAlchemyRecipeRepository(db_session)

        deleted = await repository.delete(RecipeId(99999))
        assert deleted is False

    # ========================================================================
    # RECIPE WITH RELATIONSHIPS
    # ========================================================================

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
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        ingredients = retrieved_recipe.ingredients
        assert len(ingredients) == 1
        assert ingredients[0].name == "Test Ingredient"
        assert ingredients[0].quantity.value == Decimal("100.0")
        assert ingredients[0].quantity.unit == "grams"
        assert ingredients[0].properties.is_vegan is True

    @pytest.mark.asyncio
    async def test_save_recipe_with_steps(self, db_session, sample_recipe):
        """Test saving recipe with steps"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add steps to recipe
        sample_recipe.add_step(
            Step(number=1, description="First step description", duration_minutes=5)
        )
        sample_recipe.add_step(
            Step(number=2, description="Second step description", technique="stirring")
        )

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        steps = retrieved_recipe.steps
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
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        tags = retrieved_recipe.tags
        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert "healthy" in tag_names
        assert "quick" in tag_names

    @pytest.mark.asyncio
    async def test_save_recipe_with_duplicate_tags(self, db_session):
        """Test that tags are reused when they already exist"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create first recipe with a tag
        recipe1 = Recipe.create(
            name="Recipe 1",
            author_id=UserId(1),
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
            description="First recipe",
        )
        recipe1.add_tag(Tag(name="healthy", description="Healthy food"))
        await repository.save(recipe1)

        # Create second recipe with same tag
        recipe2 = Recipe.create(
            name="Recipe 2",
            author_id=UserId(1),
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.LUNCH},
            description="Second recipe",
        )
        recipe2.add_tag(Tag(name="healthy", description="Healthy food"))
        saved_recipe2 = await repository.save(recipe2)

        # Verify both recipes have the tag
        retrieved_recipe2 = await repository.find_by_id(saved_recipe2.id)

        assert retrieved_recipe2 is not None
        tags = retrieved_recipe2.tags
        assert len(tags) == 1
        assert any(tag.name == "healthy" for tag in tags)

    @pytest.mark.asyncio
    async def test_save_recipe_with_meal_types(self, db_session):
        """Test saving recipe with meal types"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create recipe with meal types
        recipe = Recipe.create(
            name="Test Recipe",
            author_id=UserId(1),
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.DINNER, MealType.LUNCH},
            description="Test description",
        )

        # Save recipe
        saved_recipe = await repository.save(recipe)

        # Retrieve recipe
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        meal_types = retrieved_recipe.meal_types
        assert len(meal_types) == 2
        assert MealType.DINNER in meal_types
        assert MealType.LUNCH in meal_types

    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_update_recipe_basic_info(self, db_session, sample_recipe):
        """Test updating recipe basic information"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save initial recipe
        saved_recipe = await repository.save(sample_recipe)
        original_version = saved_recipe.version

        # Update recipe using the new method
        saved_recipe.update_basic_info(
            name="Updated Recipe Name",
            description="Updated description",
            difficulty=DifficultyLevel.HARD,
        )

        # Update recipe
        await repository.save(saved_recipe)

        # Retrieve and verify
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        assert retrieved_recipe.name == "Updated Recipe Name"
        assert retrieved_recipe.description == "Updated description"
        assert retrieved_recipe.difficulty == DifficultyLevel.HARD
        assert retrieved_recipe.version == original_version + 1

    @pytest.mark.asyncio
    async def test_update_recipe_ingredients(
        self, db_session, sample_recipe, sample_ingredient
    ):
        """Test updating recipe ingredients"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe with one ingredient
        sample_recipe.add_ingredient(sample_ingredient)
        saved_recipe = await repository.save(sample_recipe)

        # Add another ingredient
        properties2 = IngredientProperties(
            is_vegan=False,
            is_vegetarian=True,
            allergens={"dairy"},
        )
        ingredient2 = Ingredient.reconstruct(
            id=IngredientId(2),
            name="New Ingredient",
            quantity=Quantity(value=Decimal("200.0"), unit="ml"),
            properties=properties2,
            is_optional=True,
            substitutes=[],
        )

        # Update ingredients using the new method
        saved_recipe.update_ingredients([sample_ingredient, ingredient2])

        await repository.save(saved_recipe)

        # Verify ingredients were updated
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        ingredients = retrieved_recipe.ingredients
        assert len(ingredients) == 2
        ingredient_names = {ing.name for ing in ingredients}
        assert "Test Ingredient" in ingredient_names
        assert "New Ingredient" in ingredient_names

    @pytest.mark.asyncio
    async def test_update_recipe_remove_all_ingredients(
        self, db_session, sample_recipe, sample_ingredient
    ):
        """Test removing all ingredients from a recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe with ingredient
        sample_recipe.add_ingredient(sample_ingredient)
        saved_recipe = await repository.save(sample_recipe)

        # Update with no ingredients using the new method
        saved_recipe.clear_ingredients()

        await repository.save(saved_recipe)

        # Verify ingredients were removed
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is not None
        assert len(retrieved_recipe.ingredients) == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_recipe(self, db_session):
        """Test updating recipe that doesn't exist"""
        repository = SQLAlchemyRecipeRepository(db_session)
        from datetime import datetime

        # Create a recipe with ID that doesn't exist
        recipe = Recipe.reconstruct(
            id=RecipeId(99999),
            name="Nonexistent Recipe",
            author_id=UserId(1),
            description="This recipe doesn't exist",
            difficulty=DifficultyLevel.EASY,
            cuisine=CuisineType.ITALIAN,
            ingredients=[],
            steps=[],
            tags=set(),
            meal_types=set(),
            serving_info=None,
            cooking_time=None,
            nutritional_info=None,
            rating_sum=0,
            rating_count=0,
            view_count=0,
            favorite_count=0,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
        )

        with pytest.raises(RecipeNotFoundException):
            await repository.save(recipe)

    # ========================================================================
    # SEARCH OPERATIONS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_with_pagination(self, db_session):
        """Test searching recipes with pagination"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create multiple recipes
        for i in range(5):
            recipe = Recipe.create(
                name=f"Recipe {i}",
                author_id=UserId(1),
                difficulty=DifficultyLevel.MEDIUM,
                meal_types={MealType.DINNER},
                description=f"Description {i}",
            )
            await repository.save(recipe)

        # Import the AllSpecification
        from app.modules.recipe.infrastructure.persistence.specification import (
            AllSpecification,
        )

        spec = AllSpecification()

        # Test first page
        page_request = PaginationParams(
            page=1, size=2, sort_by="created_at", sort_dir="asc"
        )
        page = await repository.search(spec, page_request)

        assert page.total == 5
        assert len(page.items) == 2
        assert page.page == 1
        assert page.size == 2

        # Test second page
        page_request = PaginationParams(
            page=2, size=2, sort_by="created_at", sort_dir="asc"
        )
        page = await repository.search(spec, page_request)

        assert page.total == 5
        assert len(page.items) == 2
        assert page.page == 2

        # Test last page
        page_request = PaginationParams(
            page=3, size=2, sort_by="created_at", sort_dir="asc"
        )
        page = await repository.search(spec, page_request)

        assert page.total == 5
        assert len(page.items) == 1  # Last page has only 1 item
        assert page.page == 3

    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session):
        """Test searching recipes by name"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create recipes with different names
        recipe1 = Recipe.create(
            name="Chocolate Cake",
            author_id=UserId(1),
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.DINNER},
            description="Delicious chocolate cake",
        )
        await repository.save(recipe1)

        recipe2 = Recipe.create(
            name="Vanilla Cake",
            author_id=UserId(1),
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.DINNER},
            description="Classic vanilla cake",
        )
        await repository.save(recipe2)

        recipe3 = Recipe.create(
            name="Chocolate Cookies",
            author_id=UserId(1),
            description="Crispy chocolate cookies",
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
        )
        await repository.save(recipe3)

        # Search for "chocolate" (should match 2 recipes)
        from app.modules.recipe.infrastructure.persistence.specification import (
            RecipeByNameSpecification,
        )

        spec = RecipeByNameSpecification(name_pattern="Chocolate")
        page_request = PaginationParams(page=1, size=10)
        page = await repository.search(spec, page_request)

        assert page.total == 2
        assert len(page.items) == 2
        names = {recipe.name for recipe in page.items}
        assert "Chocolate Cake" in names
        assert "Chocolate Cookies" in names

        # Search for "Vanilla" (should match 1 recipe)
        spec = RecipeByNameSpecification(name_pattern="Vanilla")
        page = await repository.search(spec, page_request)

        assert page.total == 1
        assert page.items[0].name == "Vanilla Cake"

    @pytest.mark.asyncio
    async def test_search_by_author(self, db_session):
        """Test searching recipes by author"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create recipes for different authors
        recipe1 = Recipe.create(
            name="Author 1 Recipe",
            author_id=UserId(1),
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
            description="Recipe by author 1",
        )
        await repository.save(recipe1)

        recipe2 = Recipe.create(
            name="Author 2 Recipe",
            author_id=UserId(2),
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.DINNER},
            description="Recipe by author 2",
        )
        await repository.save(recipe2)

        recipe3 = Recipe.create(
            name="Another Author 1 Recipe",
            author_id=UserId(1),
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
            description="Another recipe by author 1",
        )
        await repository.save(recipe3)

        # Search for author 1's recipes
        from app.modules.recipe.infrastructure.persistence.specification import (
            RecipeByAuthorSpecification,
        )

        spec = RecipeByAuthorSpecification(author_id=UserId(1))
        page_request = PaginationParams(page=1, size=10)
        page = await repository.search(spec, page_request)

        assert page.total == 2
        assert len(page.items) == 2
        for recipe in page.items:
            assert recipe.author_id == UserId(1)

        # Search for author 2's recipes
        spec = RecipeByAuthorSpecification(author_id=UserId(2))
        page = await repository.search(spec, page_request)

        assert page.total == 1
        assert page.items[0].author_id == UserId(2)

    @pytest.mark.asyncio
    async def test_search_with_multiple_criteria(self, db_session):
        """Test searching recipes with multiple criteria using builder"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create diverse recipes
        recipe1 = Recipe.create(
            name="Easy Pasta",
            author_id=UserId(1),
            description="Quick pasta dish",
            difficulty=DifficultyLevel.EASY,
            cuisine=CuisineType.ITALIAN,
            meal_types={MealType.DINNER},
        )
        recipe1.add_tag(Tag(name="quick", description="Quick recipes"))
        await repository.save(recipe1)

        recipe2 = Recipe.create(
            name="Complex Pasta",
            author_id=UserId(1),
            description="Advanced pasta dish",
            difficulty=DifficultyLevel.HARD,
            cuisine=CuisineType.ITALIAN,
            meal_types={MealType.DINNER},
        )
        await repository.save(recipe2)

        recipe3 = Recipe.create(
            name="Easy Tacos",
            author_id=UserId(2),
            description="Simple tacos",
            difficulty=DifficultyLevel.EASY,
            cuisine=CuisineType.MEXICAN,
            meal_types={MealType.DINNER},
        )
        recipe3.add_tag(Tag(name="quick", description="Quick recipes"))
        await repository.save(recipe3)

        # Search: Author 1 + Easy difficulty
        from app.modules.recipe.infrastructure.persistence.specification_builder import (
            RecipeSearchCriteria,
            RecipeSpecificationBuilder,
        )

        criteria = RecipeSearchCriteria(
            author_id=UserId(1),
            difficulty=DifficultyLevel.EASY,
        )
        spec = RecipeSpecificationBuilder.build_from_criteria(criteria)
        page_request = PaginationParams(page=1, size=10)
        page = await repository.search(spec, page_request)

        assert page.total == 1
        assert page.items[0].name == "Easy Pasta"

        # Search: Italian cuisine + Easy difficulty
        criteria = RecipeSearchCriteria(
            cuisine=CuisineType.ITALIAN,
            difficulty=DifficultyLevel.EASY,
        )
        spec = RecipeSpecificationBuilder.build_from_criteria(criteria)
        page = await repository.search(spec, page_request)

        assert page.total == 1
        assert page.items[0].name == "Easy Pasta"

        # Search: Tag "quick"
        criteria = RecipeSearchCriteria(tags={"quick"})
        spec = RecipeSpecificationBuilder.build_from_criteria(criteria)
        page = await repository.search(spec, page_request)

        assert page.total == 2

    @pytest.mark.asyncio
    async def test_search_sorting(self, db_session):
        """Test searching recipes with different sorting options"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create recipes with different attributes
        import asyncio

        recipe1 = Recipe.create(
            name="A Recipe",
            author_id=UserId(1),
            description="First recipe",
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
        )
        await repository.save(recipe1)
        await asyncio.sleep(0.1)  # Small delay to ensure different timestamps

        recipe2 = Recipe.create(
            name="C Recipe",
            author_id=UserId(1),
            description="Third recipe",
            difficulty=DifficultyLevel.HARD,
            meal_types={MealType.DINNER},
        )
        await repository.save(recipe2)
        await asyncio.sleep(0.1)

        recipe3 = Recipe.create(
            name="B Recipe",
            author_id=UserId(1),
            description="Second recipe",
            difficulty=DifficultyLevel.MEDIUM,
            meal_types={MealType.DINNER},
        )
        await repository.save(recipe3)

        from app.modules.recipe.infrastructure.persistence.specification import (
            AllSpecification,
        )

        spec = AllSpecification()

        # Sort by name ascending
        page_request = PaginationParams(page=1, size=10, sort_by="name", sort_dir="asc")
        page = await repository.search(spec, page_request)

        assert page.items[0].name == "A Recipe"
        assert page.items[1].name == "B Recipe"
        assert page.items[2].name == "C Recipe"

        # Sort by name descending
        page_request = PaginationParams(
            page=1, size=10, sort_by="name", sort_dir="desc"
        )
        page = await repository.search(spec, page_request)

        assert page.items[0].name == "C Recipe"
        assert page.items[1].name == "B Recipe"
        assert page.items[2].name == "A Recipe"

        # Sort by created_at ascending (default)
        page_request = PaginationParams(
            page=1, size=10, sort_by="created_at", sort_dir="asc"
        )
        page = await repository.search(spec, page_request)

        assert page.items[0].name == "A Recipe"  # First created
        assert page.items[2].name == "B Recipe"  # Last created

    # ========================================================================
    # COMPLEX SCENARIOS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_recipe_with_nutritional_info(self, db_session, sample_recipe):
        """Test recipe with nutritional information"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add nutritional info
        sample_recipe.update_nutritional_info(
            NutritionalInfo(
                calories=350,
                protein_g=Decimal("20.5"),
                carbs_g=Decimal("45.2"),
                fat_g=Decimal("12.3"),
                fiber_g=Decimal("5.0"),
                sodium_mg=Decimal("300.0"),
            )
        )

        saved_recipe = await repository.save(sample_recipe)
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        assert retrieved_recipe.nutritional_info is not None
        nutritional_info = retrieved_recipe.nutritional_info
        assert nutritional_info.calories == 350
        assert nutritional_info.protein_g == Decimal("20.5")
        assert nutritional_info.carbs_g == Decimal("45.2")
        assert nutritional_info.fat_g == Decimal("12.3")

    @pytest.mark.asyncio
    async def test_recipe_complex_full_workflow(self, db_session):
        """Test complex recipe operations with all components"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Create a complex recipe
        recipe = Recipe.create(
            name="Complex Test Recipe",
            author_id=UserId(1),
            description="A complex recipe with all features",
            difficulty=DifficultyLevel.HARD,
            cuisine=CuisineType.MEXICAN,
            meal_types={MealType.DINNER, MealType.LUNCH},
        )

        # Add serving info
        recipe.update_serving_info(ServingInfo(servings=6, serving_size="1 plate"))

        # Add cooking time
        recipe.update_cooking_time(
            CookingTime(prep_minutes=20, cook_minutes=45, rest_minutes=10)
        )

        # Add nutritional info
        recipe.update_nutritional_info(
            NutritionalInfo(
                calories=450,
                protein_g=Decimal("30.0"),
                carbs_g=Decimal("50.0"),
                fat_g=Decimal("15.0"),
            )
        )

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
            substitutes=["Vegan cheese", "Nutritional yeast"],
        )

        recipe.add_ingredient(ingredient1)
        recipe.add_ingredient(ingredient2)

        # Add steps
        recipe.add_step(
            Step(
                number=1,
                description="Chop the tomatoes",
                duration_minutes=10,
                technique="chopping",
            )
        )
        recipe.add_step(
            Step(
                number=2,
                description="Grate the cheese",
                duration_minutes=5,
                technique="grating",
            )
        )
        recipe.add_step(
            Step(
                number=3,
                description="Cook everything together",
                duration_minutes=30,
                technique="simmering",
            )
        )

        # Add tags
        recipe.add_tag(Tag(name="mexican", description="Mexican cuisine"))
        recipe.add_tag(Tag(name="comfort-food", description="Comfort food"))

        # Save and retrieve
        saved_recipe = await repository.save(recipe)
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        # Verify all components
        assert retrieved_recipe is not None
        assert retrieved_recipe.name == "Complex Test Recipe"
        assert retrieved_recipe.difficulty == DifficultyLevel.HARD
        assert retrieved_recipe.cuisine == CuisineType.MEXICAN

        serving_info = retrieved_recipe.serving_info
        assert serving_info is not None
        assert serving_info.servings == 6

        cooking_time = retrieved_recipe.cooking_time
        assert cooking_time is not None
        assert cooking_time.prep_minutes == 20
        assert cooking_time.cook_minutes == 45

        ingredients = retrieved_recipe.ingredients
        assert len(ingredients) == 2

        steps = retrieved_recipe.steps
        assert len(steps) == 3
        assert steps[0].number == 1
        assert steps[1].number == 2
        assert steps[2].number == 3

        tags = retrieved_recipe.tags
        assert len(tags) == 2

        meal_types = retrieved_recipe.meal_types
        assert len(meal_types) == 2

    @pytest.mark.asyncio
    async def test_concurrent_updates_version_control(self, db_session, sample_recipe):
        """Test that version control works correctly"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save initial recipe
        saved_recipe = await repository.save(sample_recipe)
        assert saved_recipe.version == 1

        # Update recipe using the new method
        saved_recipe.update_basic_info(name="Updated Name")
        await repository.save(saved_recipe)

        # Verify version incremented
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.version == 2

    @pytest.mark.asyncio
    async def test_recipe_with_empty_collections(self, db_session):
        """Test recipe with no ingredients, steps, tags, or meal types"""
        repository = SQLAlchemyRecipeRepository(db_session)

        recipe = Recipe.create(
            name="Minimal Recipe",
            author_id=UserId(1),
            difficulty=DifficultyLevel.EASY,
            meal_types={MealType.DINNER},
            description="A minimal recipe",
        )

        saved_recipe = await repository.save(recipe)
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)

        assert retrieved_recipe is not None
        assert len(retrieved_recipe.ingredients) == 0
        assert len(retrieved_recipe.steps) == 0
        assert len(retrieved_recipe.tags) == 0
        assert len(retrieved_recipe.meal_types) == 1  # Now meal_types is required

    # ========================================================================
    # NEW FUNCTIONALITY TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_recipe_soft_delete_and_restore(self, db_session, sample_recipe):
        """Test soft delete and restore functionality"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)
        assert not saved_recipe.is_deleted

        # Soft delete
        saved_recipe.soft_delete()
        await repository.save(saved_recipe)

        # Verify deleted
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is None  # Should not find soft-deleted recipes

        # Restore (would need to test with a method that can retrieve deleted recipes)
        # This would require additional repository methods

    @pytest.mark.asyncio
    async def test_recipe_update_tracking_info(self, db_session, sample_recipe):
        """Test updating tracking information"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)
        original_view_count = saved_recipe.view_count
        original_version = saved_recipe.version

        # Increment view count
        saved_recipe.increment_view_count()
        await repository.save(saved_recipe)

        # Retrieve and verify
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.view_count == original_view_count + 1
        # View count increment doesn't increase version
        assert retrieved_recipe.version == original_version

    @pytest.mark.asyncio
    async def test_recipe_add_rating(self, db_session, sample_recipe):
        """Test adding rating to recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Save recipe
        saved_recipe = await repository.save(sample_recipe)
        assert saved_recipe.average_rating is None

        # Add rating
        saved_recipe.add_rating(4)
        await repository.save(saved_recipe)

        # Retrieve and verify
        retrieved_recipe = await repository.find_by_id(saved_recipe.id)
        assert retrieved_recipe is not None
        assert retrieved_recipe.average_rating == 4.0
        assert retrieved_recipe.rating_count == 1

    @pytest.mark.asyncio
    async def test_recipe_calculate_total_time(self, db_session, sample_recipe):
        """Test calculating total time"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add cooking time
        sample_recipe.update_cooking_time(
            CookingTime(prep_minutes=15, cook_minutes=30, rest_minutes=5)
        )

        saved_recipe = await repository.save(sample_recipe)

        total_time = saved_recipe.calculate_total_time()
        assert total_time == 50  # 15 + 30 + 5

    @pytest.mark.asyncio
    async def test_recipe_get_allergens(
        self, db_session, sample_recipe, sample_ingredient
    ):
        """Test getting allergens from recipe"""
        repository = SQLAlchemyRecipeRepository(db_session)

        # Add ingredient with allergens
        sample_recipe.add_ingredient(sample_ingredient)
        saved_recipe = await repository.save(sample_recipe)

        allergens = saved_recipe.get_allergens()
        assert "gluten" in allergens
