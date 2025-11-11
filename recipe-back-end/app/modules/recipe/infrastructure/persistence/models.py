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
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.config.sql_session import Base

if TYPE_CHECKING:
    from app.modules.auth.infrastucture.persitence.models import UserModel

recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column(
        "recipe_id",
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
    # Índice compuesto para búsquedas bidireccionales
    Index("idx_recipe_tags_recipe_id", "recipe_id"),
    Index("idx_recipe_tags_tag_id", "tag_id"),
)

recipe_reviews = Table(
    "recipe_reviews",
    Base.metadata,
    Column(
        "recipe_id",
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "reviewed_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column("rating", Integer, nullable=False),
    Column("comment", Text, nullable=True),
    Index("idx_recipe_reviews_recipe_id", "recipe_id"),
    Index("idx_recipe_reviews_user_id", "user_id"),
)

recipe_favorites = Table(
    "recipe_favorites",
    Base.metadata,
    Column(
        "recipe_id",
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "favorited_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Index("idx_recipe_favorites_recipe_id", "recipe_id"),
    Index("idx_recipe_favorites_user_id", "user_id"),
)


class RecipeModel(Base):
    """
    SQLAlchemy model for Recipe entity.

    Índices optimizados para queries comunes:
    - Búsqueda por autor
    - Filtrado por dificultad/cocina
    - Ordenamiento por rating/views
    - Búsquedas full-text en nombre
    """

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True  # Para búsquedas por nombre
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Para "mis recetas"
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True  # Para filtrar por dificultad
    )
    cuisine: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True  # Para filtrar por tipo de cocina
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=""  # Empty string por defecto
    )

    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    serving_size: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True  # "1 cup", "2 slices" - opcional
    )

    prep_time_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    cook_time_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    rest_time_minutes: Mapped[int] = mapped_column(nullable=False, default=0)

    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    carbs_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    fat_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    fiber_g: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    sodium_mg: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)

    version: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,  # Para "más recientes"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True  # Para soft delete queries
    )

    author: Mapped["UserModel"] = relationship(
        back_populates="recipes", lazy="selectin"  # Evita N+1 queries
    )

    ingredients: Mapped[List["IngredientModel"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="IngredientModel.id",
        lazy="selectin",
    )

    steps: Mapped[List["StepModel"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="StepModel.step_number",
        lazy="selectin",
    )

    tags: Mapped[List["TagModel"]] = relationship(
        secondary=recipe_tags, back_populates="recipes", lazy="selectin"
    )

    meal_types: Mapped[List["RecipeMealTypeModel"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", lazy="selectin"
    )

    view_count: Mapped[int] = mapped_column(
        nullable=False, default=0, index=True  # Para "más vistas"
    )

    __table_args__ = (
        CheckConstraint("servings > 0", name="check_servings_positive"),
        CheckConstraint("prep_time_minutes >= 0", name="check_prep_time_non_negative"),
        CheckConstraint("cook_time_minutes >= 0", name="check_cook_time_non_negative"),
        CheckConstraint("rest_time_minutes >= 0", name="check_rest_time_non_negative"),
        CheckConstraint("view_count >= 0", name="check_view_count_non_negative"),
        CheckConstraint(
            "favorite_count >= 0", name="check_favorite_count_non_negative"
        ),
        CheckConstraint("version > 0", name="check_version_positive"),
        # Índices compuestos para queries comunes
        Index("idx_recipes_author_created", "author_id", "created_at"),
        Index("idx_recipes_difficulty_cuisine", "difficulty", "cuisine"),
        Index("idx_recipes_deleted_at_created", "deleted_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<RecipeModel(id={self.id}, name='{self.name}', author_id={self.author_id})>"

    @property
    def total_time_minutes(self) -> int:
        """Tiempo total de la receta"""
        return self.prep_time_minutes + self.cook_time_minutes + self.rest_time_minutes

    @property
    def is_deleted(self) -> bool:
        """Indica si la receta está eliminada (soft delete)"""
        return self.deleted_at is not None

    def increment_version(self):
        """Incrementa la versión de la receta"""
        self.version += 1


class IngredientModel(Base):
    """SQLAlchemy model for Ingredient entity"""

    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True  # Para búsquedas por ingrediente
    )
    quantity_value: Mapped[Decimal] = mapped_column(DECIMAL(10, 3), nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_vegan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_gluten_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_dairy_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allergens: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    substitutes: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    recipe: Mapped["RecipeModel"] = relationship(back_populates="ingredients")

    __table_args__ = (
        CheckConstraint("quantity_value > 0", name="check_quantity_positive"),
        # Índice compuesto para búsquedas por ingrediente en recetas
        Index("idx_ingredients_recipe_name", "recipe_id", "name"),
        # Índices para filtros dietéticos
        Index("idx_ingredients_dietary", "is_vegan", "is_vegetarian", "is_gluten_free"),
    )

    def __repr__(self) -> str:
        return f"<IngredientModel(id={self.id}, name='{self.name}', quantity={self.quantity_value} {self.quantity_unit})>"


class StepModel(Base):
    """SQLAlchemy model for Recipe Step entity"""

    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temperature: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Ingredientes usados en este paso
    ingredients_used: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    recipe: Mapped["RecipeModel"] = relationship(back_populates="steps")

    __table_args__ = (
        # Constraint: step_number debe ser único por receta
        UniqueConstraint("recipe_id", "step_number", name="uq_recipe_step_number"),
        CheckConstraint("step_number > 0", name="check_step_number_positive"),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes >= 0",
            name="check_duration_non_negative",
        ),
        # Índice compuesto para ordenamiento eficiente
        Index("idx_steps_recipe_number", "recipe_id", "step_number"),
    )

    def __repr__(self) -> str:
        return f"<StepModel(id={self.id}, recipe_id={self.recipe_id}, step={self.step_number})>"


class TagModel(Base):
    """SQLAlchemy model for Tag entity"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    usage_count: Mapped[int] = mapped_column(
        nullable=False, default=0, index=True  # Para "tags más populares"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    recipes: Mapped[List["RecipeModel"]] = relationship(
        secondary=recipe_tags, back_populates="tags"
    )

    __table_args__ = (
        CheckConstraint("usage_count >= 0", name="check_usage_count_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<TagModel(id={self.id}, name='{self.name}', usage={self.usage_count})>"


class RecipeMealTypeModel(Base):
    """SQLAlchemy model for Recipe Meal Type association"""

    __tablename__ = "recipe_meal_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    meal_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # breakfast, lunch, dinner, snack, dessert

    recipe: Mapped["RecipeModel"] = relationship(back_populates="meal_types")

    __table_args__ = (
        # Un recipe no puede tener el mismo meal_type duplicado
        UniqueConstraint("recipe_id", "meal_type", name="uq_recipe_meal_type"),
        # Índice compuesto para búsquedas por meal_type
        Index("idx_meal_types_type_recipe", "meal_type", "recipe_id"),
    )

    def __repr__(self) -> str:
        return f"<RecipeMealTypeModel(recipe_id={self.recipe_id}, meal_type='{self.meal_type}')>"
