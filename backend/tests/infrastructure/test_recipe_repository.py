"""SqlAlchemyRecipeRepository tests aligned with current create/save APIs."""

from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.sql_session import Base
from app.modules.auth.domain.user import User, UserGender, UserId, UserRole
from app.modules.auth.infrastucture.persitence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.modules.recipe.domain.models.entities.ingredient import (
    Ingredient,
    IngredientProperties,
)
from app.modules.recipe.domain.models.entities.recipe import Recipe
from app.modules.recipe.domain.models.value_objects.enums import (
    CuisineType,
    DifficultyLevel,
    MealType,
)
from app.modules.recipe.domain.models.value_objects.param_dtos import (
    RecipeCreateBasicInfo,
    RecipeCreateContent,
    RecipeCreateDetails,
)
from app.modules.recipe.domain.models.value_objects.value_objects_standard import (
    CookingTime,
    Quantity,
    RecipeId,
    ServingInfo,
    Step,
    Tag,
)
from app.modules.recipe.infrastructure.persistence.repository import (
    SqlAlchemyRecipeRepository,
)


def _make_recipe(author_id: UserId, name: str = "Pasta Primavera") -> Recipe:
    return Recipe.create(
        RecipeCreateBasicInfo(
            name=name,
            author_id=author_id,
            description="Fresh seasonal pasta dish",
            difficulty=DifficultyLevel.MEDIUM,
            cuisine=CuisineType.ITALIAN,
        ),
        RecipeCreateContent(
            ingredients=[
                Ingredient.create(
                    name="Pasta",
                    quantity=Quantity(value=Decimal("200"), unit="grams"),
                    properties=IngredientProperties(is_vegan=True, is_vegetarian=True),
                )
            ],
            steps=[Step(number=1, description="Boil pasta and toss with vegetables")],
            tags={Tag(name="italian"), Tag(name="pasta")},
        ),
        RecipeCreateDetails(
            meal_types={MealType.DINNER},
            serving_info=ServingInfo(servings=2),
            cooking_time=CookingTime(prep_minutes=10, cook_minutes=15),
        ),
    )


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Import models so they register on Base.metadata
    import app.modules.auth.infrastucture.persitence.models  # noqa: F401
    import app.modules.recipe.infrastructure.persistence.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def author(db_session):
    user_repo = SQLAlchemyUserRepository(db_session)
    user = User.create(
        first_name="Alex",
        last_name="Chef",
        email="alex.chef@example.com",
        raw_password="SecurePass123!",
        gender=UserGender.OTHER,
        roles=[UserRole.COMMON_USER],
    )
    return await user_repo.save(user)


class TestSqlAlchemyRecipeRepository:
    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        recipe = _make_recipe(author.id)

        saved = await repo.save(recipe)
        found = await repo.find_by_id(saved.id, with_relations=True)

        assert found is not None
        assert found.id.value == saved.id.value
        assert found.name == "Pasta Primavera"
        assert found.author_id == author.id
        assert len(found.ingredients) == 1
        assert len(found.steps) == 1
        assert found.serving_info.servings == 2

    @pytest.mark.asyncio
    async def test_find_by_id_and_author(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        saved = await repo.save(_make_recipe(author.id))

        assert await repo.find_by_id_and_author(saved.id, author.id) is not None
        assert await repo.find_by_id_and_author(saved.id, UserId(999)) is None

    @pytest.mark.asyncio
    async def test_exists_helpers(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        saved = await repo.save(_make_recipe(author.id, name="Unique Dish"))

        assert await repo.exists_by_id(saved.id) is True
        assert await repo.exists_by_id(RecipeId(999)) is False
        assert await repo.exists_by_name_and_author("Unique Dish", author.id) is True
        assert await repo.exists_by_name_and_author("Missing", author.id) is False

    @pytest.mark.asyncio
    async def test_update_recipe(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        saved = await repo.save(_make_recipe(author.id))

        saved.update_basic_info(name="Pasta Updated", description="Updated description")
        updated = await repo.save(saved)
        found = await repo.find_by_id(updated.id)

        assert found.name == "Pasta Updated"
        assert found.description == "Updated description"

    @pytest.mark.asyncio
    async def test_soft_delete(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        saved = await repo.save(_make_recipe(author.id))

        assert await repo.delete(saved.id) is True
        assert await repo.find_by_id(saved.id) is None
        assert await repo.find_by_id(saved.id, include_deleted=True) is not None

    @pytest.mark.asyncio
    async def test_increase_view_count(self, db_session, author):
        repo = SqlAlchemyRecipeRepository(db_session)
        saved = await repo.save(_make_recipe(author.id))

        await repo.increase_view_count(saved.id)
        found = await repo.find_by_id(saved.id)

        assert found.view_count >= 1
