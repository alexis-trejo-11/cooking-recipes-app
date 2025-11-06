# app/recipe/infrastructure/persistence/models.py
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DECIMAL,
    JSON,
    Table,
    Column,
    Integer,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config.sql_session import Base

if TYPE_CHECKING:
    from app.auth.infrastucture.persitence.models import UserModel

# Association tables
recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

recipe_meal_types = Table(
    "recipe_meal_types",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("meal_type", String(50), primary_key=True),  # Using MealType enum values
)


class RecipeModel(Base):
    """SQLAlchemy model for Recipe entity"""

    __tablename__ = "recipes"

    # Basic info
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Enums stored as strings
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # easy, medium, hard
    cuisine: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Serving information
    serving_size: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # "1 cup", "2 slices"
    servings: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # number of servings

    # Cooking time (separate from step durations)
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    cook_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    rest_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)

    # Nutritional info (per recipe total)
    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    carbs_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    fat_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    fiber_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    sodium_mg: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)

    # Tracking
    rating_sum: Mapped[int] = mapped_column(default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    view_count: Mapped[int] = mapped_column(default=0)
    favorite_count: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    author: Mapped["UserModel"] = relationship(back_populates="recipes")
    ingredients: Mapped[List["IngredientModel"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="IngredientModel.id",
    )
    steps: Mapped[List["StepModel"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="StepModel.step_number",
    )
    tags: Mapped[List["TagModel"]] = relationship(
        secondary=recipe_tags, back_populates="recipes", order_by="TagModel.name"
    )
    meal_types: Mapped[List["RecipeMealTypeModel"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RecipeModel(id={self.id}, name='{self.name}', author_id={self.author_id})>"


class IngredientModel(Base):
    """SQLAlchemy model for Ingredient entity"""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Quantity as separate fields for easier querying
    quantity_value: Mapped[Decimal] = mapped_column(DECIMAL(10, 3), nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    is_optional: Mapped[bool] = mapped_column(default=False)

    # Dietary properties
    is_vegan: Mapped[bool] = mapped_column(default=True)
    is_vegetarian: Mapped[bool] = mapped_column(default=True)
    is_gluten_free: Mapped[bool] = mapped_column(default=True)
    is_dairy_free: Mapped[bool] = mapped_column(default=True)

    # Allergens as JSON array
    allergens: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Substitutes as JSON array
    substitutes: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="ingredients")

    def __repr__(self) -> str:
        return f"<IngredientModel(id={self.id}, name='{self.name}', recipe_id={self.recipe_id})>"


class StepModel(Base):
    """SQLAlchemy model for Recipe Step entity"""

    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temperature: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Ingredients used in this step (JSON array of ingredient names)
    ingredients_used: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="steps")

    def __repr__(self) -> str:
        return f"<StepModel(id={self.id}, recipe_id={self.recipe_id}, step_number={self.step_number})>"


class TagModel(Base):
    """SQLAlchemy model for Tag entity"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    recipes: Mapped[List["RecipeModel"]] = relationship(
        secondary=recipe_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<TagModel(id={self.id}, name='{self.name}')>"


class RecipeMealTypeModel(Base):
    """SQLAlchemy model for Recipe Meal Type association"""

    __tablename__ = "recipe_meal_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"), nullable=False, index=True
    )
    meal_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # breakfast, lunch, dinner, snack, dessert

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="meal_types")

    def __repr__(self) -> str:
        return f"<RecipeMealTypeModel(recipe_id={self.recipe_id}, meal_type='{self.meal_type}')>"
