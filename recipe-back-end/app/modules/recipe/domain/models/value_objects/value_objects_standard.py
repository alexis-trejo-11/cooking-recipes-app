import logging
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal

logger = logging.getLogger("app.modules.recipe")


@dataclass(frozen=True)
class RecipeId:
    """Value Object para identificador de Recipe."""

    value: int = field(default=0)

    @classmethod
    def generate(cls) -> "RecipeId":
        """Generar nuevo ID (en realidad lo hará la DB)."""
        return cls(value=0)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"RecipeId({self.value})"

    def is_valid(self) -> bool:
        """Validar que el ID sea válido."""
        return self.value >= 0


@dataclass(frozen=True)
class IngredientId:
    """Value Object para identificador de Ingredient."""

    value: int = field(default=0)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Quantity:
    """Value Object para cantidades con unidades."""

    value: Decimal = field(default=Decimal("0.0"))
    unit: str = field(default="unknown")  # "grams", "cups", "tablespoons", "units"

    def __post_init__(self):
        """Validar la cantidad."""
        if self.value < 0:
            raise ValueError("Quantity value cannot be negative")
        if not self.unit or not self.unit.strip():
            raise ValueError("Unit cannot be empty")

    def scale(self, factor: Decimal) -> "Quantity":
        """Escalar cantidad por un factor."""
        if factor < 0:
            raise ValueError("Scaling factor cannot be negative")
        return Quantity(value=self.value * factor, unit=self.unit)

    def convert_to(self, target_unit: str, conversion_rate: Decimal) -> "Quantity":
        """Convertir a otra unidad."""
        return Quantity(value=self.value * conversion_rate, unit=target_unit)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"


@dataclass(frozen=True)
class NutritionalInfo:
    """Value Object para información nutricional."""

    calories: Optional[int] = None
    protein_g: Optional[Decimal] = None
    carbs_g: Optional[Decimal] = None
    fat_g: Optional[Decimal] = None
    fiber_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None

    def scale(self, factor: Decimal) -> "NutritionalInfo":
        """Escalar información nutricional."""
        if factor < 0:
            raise ValueError("Scaling factor cannot be negative")

        return NutritionalInfo(
            calories=round(self.calories * factor) if self.calories else None,
            protein_g=self.protein_g * factor if self.protein_g else None,
            carbs_g=self.carbs_g * factor if self.carbs_g else None,
            fat_g=self.fat_g * factor if self.fat_g else None,
            fiber_g=self.fiber_g * factor if self.fiber_g else None,
            sodium_mg=self.sodium_mg * factor if self.sodium_mg else None,
        )

    def is_complete(self) -> bool:
        """Verificar si toda la información nutricional está presente."""
        return all(
            [
                self.calories is not None,
                self.protein_g is not None,
                self.carbs_g is not None,
                self.fat_g is not None,
            ]
        )

    def calculate_total_calories(self) -> Optional[int]:
        """Calcular calorías totales basado en macronutrientes."""
        if all([self.protein_g, self.carbs_g, self.fat_g]):
            # 4 cal/g para proteína y carbohidratos, 9 cal/g para grasa
            return int(self.protein_g * 4 + self.carbs_g * 4 + self.fat_g * 9)
        return self.calories


@dataclass(frozen=True)
class ServingInfo:
    """Value Object para información de porciones."""

    servings: int
    serving_size: Optional[str] = None

    def __post_init__(self):
        """Validar información de porciones."""
        if self.servings <= 0:
            raise ValueError("Servings must be positive")

    def scale_servings(self, new_servings: int) -> "ServingInfo":
        """Crear nueva información de porciones para diferente cantidad."""
        return ServingInfo(servings=new_servings, serving_size=self.serving_size)

    def __str__(self) -> str:
        if self.serving_size:
            return f"{self.servings} servings ({self.serving_size} each)"
        return f"{self.servings} servings"


@dataclass(frozen=True)
class CookingTime:
    """Value Object para tiempos de cocción."""

    prep_minutes: int
    cook_minutes: int
    rest_minutes: int = 0

    def __post_init__(self):
        """Validar tiempos de cocción."""
        if any(
            time < 0
            for time in [self.prep_minutes, self.cook_minutes, self.rest_minutes]
        ):
            raise ValueError("Time values cannot be negative")

    def calculate_total_minutes(self) -> int:
        """Calcular tiempo total en minutos."""
        return self.prep_minutes + self.cook_minutes + self.rest_minutes

    def format_duration(self) -> str:
        """Formatear duración en formato legible."""
        total = self.calculate_total_minutes()
        if total < 60:
            return f"{total} minutes"

        hours = total // 60
        minutes = total % 60

        if minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{hours}h {minutes}m"

    def is_quick_meal(self) -> bool:
        """Determinar si es una comida rápida (< 30 minutos)."""
        return self.calculate_total_minutes() <= 30


@dataclass(frozen=True)
class Step:
    """Value Object para pasos de la receta."""

    number: int
    description: str
    duration_minutes: Optional[int] = None
    technique: Optional[str] = None
    temperature: Optional[str] = None
    ingredients_used: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validar paso."""
        if not self.description.strip():
            raise ValueError("Step description cannot be empty")
        if self.number <= 0:
            raise ValueError("Step number must be positive")
        if self.duration_minutes and self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")

    def with_ingredients(self, ingredient_names: List[str]) -> "Step":
        """Crear nueva instancia con ingredientes especificados."""
        return Step(
            number=self.number,
            description=self.description,
            duration_minutes=self.duration_minutes,
            technique=self.technique,
            temperature=self.temperature,
            ingredients_used=ingredient_names,
        )

    def __str__(self) -> str:
        base = f"{self.number}. {self.description}"
        if self.duration_minutes:
            base += f" ({self.duration_minutes}min)"
        return base

    def __repr__(self) -> str:
        return f"Step(number={self.number}, description='{self.description[:30]}...')"


@dataclass(frozen=True)
class Tag:
    """Value Object para etiquetas."""

    name: str
    description: Optional[str] = None

    def __post_init__(self):
        """Validar y normalizar etiqueta."""
        if not self.name.strip():
            raise ValueError("Tag name cannot be empty")
        # Normalizar a minúsculas
        object.__setattr__(self, "name", self.name.lower().strip())
        if self.description:
            object.__setattr__(self, "description", self.description.strip())

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return self.name == other.name

    def __str__(self) -> str:
        return self.name
