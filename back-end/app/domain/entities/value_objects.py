from dataclasses import dataclass, field
from typing import Optional, List, Set
from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class RecipeId:
    value: int = field(default=0)


@dataclass(frozen=True)
class IngredientId:
    value: int = field(default=0)


@dataclass(frozen=True)
class UserId:
    """Value Object for User ID"""

    value: int = field(default=0)

    def __post_init__(self):
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError("User ID must be a non-negative integer")

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create UserId from string"""
        try:
            return cls(int(value))
        except (ValueError, TypeError):
            raise ValueError(f"Cannot create UserId from string: {value}")


@dataclass(frozen=True)
class Quantity:
    value: Decimal = field(default=Decimal("0.0"))
    unit: str = field(default="")  # "grams", "cups", "tablespoons", "units"

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Quantity value cannot be negative")

    def scale(self, factor: Decimal) -> "Quantity":
        """Scale quantity by a factor (for serving adjustments)"""
        return Quantity(value=self.value * factor, unit=self.unit)


@dataclass(frozen=True)
class NutritionalInfo:
    """Per serving nutritional information"""

    calories: Optional[int] = None
    protein_g: Optional[Decimal] = None
    carbs_g: Optional[Decimal] = None
    fat_g: Optional[Decimal] = None
    fiber_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None

    def scale(self, factor: Decimal) -> "NutritionalInfo":
        """Scale nutritional info by servings"""
        return NutritionalInfo(
            calories=int(self.calories * factor) if self.calories else None,
            protein_g=self.protein_g * factor if self.protein_g else None,
            carbs_g=self.carbs_g * factor if self.carbs_g else None,
            fat_g=self.fat_g * factor if self.fat_g else None,
            fiber_g=self.fiber_g * factor if self.fiber_g else None,
            sodium_mg=self.sodium_mg * factor if self.sodium_mg else None,
        )


@dataclass(frozen=True)
class ServingInfo:
    servings: int
    serving_size: Optional[str] = None  # "1 cup", "2 slices"

    def __post_init__(self):
        if self.servings <= 0:
            raise ValueError("Servings must be positive")


@dataclass(frozen=True)
class CookingTime:
    prep_minutes: int
    cook_minutes: int

    def __post_init__(self):
        if self.prep_minutes < 0 or self.cook_minutes < 0:
            raise ValueError("Time cannot be negative")

    @property
    def total_minutes(self) -> int:
        return self.prep_minutes + self.cook_minutes


@dataclass(frozen=True)
class Step:
    number: int
    description: str
    duration_minutes: Optional[int] = None
    technique: Optional[str] = None  # "sauté", "boil", "bake"
    temperature: Optional[str] = None  # "180°C", "medium heat"

    def __post_init__(self):
        if not self.description.strip():
            raise ValueError("Step description cannot be empty")


@dataclass(frozen=True)
class Tag:
    name: str  # "spicy", "vegetarian", "dessert", "quick"

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Tag cannot be empty")
        # Normalize to lowercase
        object.__setattr__(self, "name", self.name.lower().strip())
