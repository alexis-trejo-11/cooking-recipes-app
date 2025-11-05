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
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config.sql_session import Base

if TYPE_CHECKING:
    from app.auth.infrastucture.persitence.models import UserModel

userRoles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, primary_key=True),
    Column("role", String, primary_key=True),
)


recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class RecipeModel(Base):
    """SQLAlchemy model for Recipe entity"""

    __tablename__ = "recipes"

    # Basic info
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(50), default="medium", nullable=True
    )
    cuisine: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Metadata
    serving_size: Mapped[Optional[int]] = mapped_column(
        nullable=True
    )  # number of servings
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    cook_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    total_time_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Nutritional info
    calories: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    protein_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    carbs_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    fat_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Tracking
    rating_sum: Mapped[int] = mapped_column(default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    view_count: Mapped[int] = mapped_column(default=0)
    favorite_count: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    author: Mapped["UserModel"] = relationship(back_populates="recipes")
    ingredients: Mapped[List["IngredientModel"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[List["StepModel"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="StepModel.step_number",
    )
    tags: Mapped[List["TagModel"]] = relationship(
        secondary=recipe_tags, back_populates="recipes"
    )
    meal_types: Mapped[List["RecipeMealType"]] = relationship(back_populates="recipe")

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, name='{self.name}', author_id={self.author_id})>"


class IngredientModel(Base):
    """SQLAlchemy model for Ingredient entity"""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    quantity_value: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 3), nullable=True
    )
    quantity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_optional: Mapped[bool] = mapped_column(default=False)

    # Dietary properties
    is_vegan: Mapped[bool] = mapped_column(default=True)
    is_vegetarian: Mapped[bool] = mapped_column(default=True)
    is_gluten_free: Mapped[bool] = mapped_column(default=True)
    is_dairy_free: Mapped[bool] = mapped_column(default=True)
    allergens: Mapped[Optional[str]] = mapped_column(
        JSON, default=list
    )  # Store as JSON list

    # Substitutes (JSON serialized list)
    substitutes: Mapped[Optional[str]] = mapped_column(JSON, default=list)

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="ingredients")

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name='{self.name}', recipe_id={self.recipe_id})>"


class StepModel(Base):
    """SQLAlchemy model for Recipe Step entity"""

    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    step_number: Mapped[int]
    description: Mapped[str] = mapped_column(Text)
    duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temperature: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # e.g., "180°C", "medium heat"

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="steps")

    def __repr__(self) -> str:
        return f"<Step(id={self.id}, recipe_id={self.recipe_id}, step_number={self.step_number})>"


class TagModel(Base):
    """SQLAlchemy model for Tag entity"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    recipes: Mapped[List["RecipeModel"]] = relationship(
        secondary=recipe_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"


class RecipeMealType(Base):
    """SQLAlchemy model for Recipe Meal Type association"""

    __tablename__ = "recipe_meal_types"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    meal_type: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )  # breakfast, lunch, dinner, etc.

    # Relationships
    recipe: Mapped["RecipeModel"] = relationship(back_populates="meal_types")

    def __repr__(self) -> str:
        return f"<RecipeMealType(recipe_id={self.recipe_id}, meal_type='{self.meal_type}')>"
