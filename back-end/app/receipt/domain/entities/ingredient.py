from typing import Optional, List
from decimal import Decimal
from dataclasses import dataclass, field
from .value_objects import IngredientId, Quantity
from .enums import DietType
from ..exceptions import RecipeValidationException


@dataclass(frozen=True)
class IngredientProperties:
    is_vegan: bool = True
    is_vegetarian: bool = True
    is_gluten_free: bool = True
    is_dairy_free: bool = True
    allergens: set[str] = field(default_factory=set)

    def is_compatible_with(self, diet: DietType) -> bool:
        compatibility_map = {
            DietType.VEGAN: self.is_vegan,
            DietType.VEGETARIAN: self.is_vegetarian,
            DietType.GLUTEN_FREE: self.is_gluten_free,
            DietType.DAIRY_FREE: self.is_dairy_free,
            DietType.REGULAR: True,
            DietType.KETO: self._is_keto_compatible(),
        }
        return compatibility_map.get(diet, True)

    def _is_keto_compatible(self) -> bool:
        # Placeholder for keto logic
        return True


class Ingredient:
    def __init__(self):
        self._id: IngredientId = IngredientId()
        self._name: str = ""
        self._quantity: Quantity = Quantity()
        self._properties: IngredientProperties = IngredientProperties()
        self._is_optional: bool = False
        self._substitutes: List[str] = []

    @classmethod
    def create(
        cls,
        name: str,
        quantity: Quantity,
        properties: IngredientProperties,
        is_optional: bool = False,
        substitutes: Optional[List[str]] = None,
    ) -> "Ingredient":
        """
        Static constructor for creating a new Ingredient
        Use this when creating a brand new ingredient from user input
        """
        if not name or not name.strip():
            raise RecipeValidationException(
                "Ingredient name cannot be empty", "EMPTY_INGREDIENT_NAME"
            )

        if len(name.strip()) > 100:
            raise RecipeValidationException(
                "Ingredient name cannot exceed 100 characters",
                "INGREDIENT_NAME_TOO_LONG",
            )

        ingredient = cls.__new__(cls)

        ingredient._id = IngredientId()
        ingredient._name = name.strip()
        ingredient._quantity = quantity
        ingredient._properties = properties
        ingredient._is_optional = is_optional
        ingredient._substitutes = substitutes or []

        return ingredient

    @classmethod
    def reconstruct(
        cls,
        id: IngredientId,
        name: str,
        quantity: Quantity,
        properties: IngredientProperties,
        is_optional: bool,
        substitutes: List[str],
    ) -> "Ingredient":
        """
        Static constructor for reconstructing Ingredient from persistence (DB/Cache)
        Use this when loading an existing ingredient from database or cache
        """
        if id.value < 0:
            raise RecipeValidationException(
                f"Invalid ingredient ID {id}", "INVALID_INGREDIENT_ID"
            )

        if not name or not name.strip():
            raise RecipeValidationException(
                "Ingredient name cannot be empty", "EMPTY_INGREDIENT_NAME"
            )

        ingredient = cls.__new__(cls)

        ingredient._id = id
        ingredient._name = name
        ingredient._quantity = quantity
        ingredient._properties = properties
        ingredient._is_optional = is_optional
        ingredient._substitutes = substitutes or []

        return ingredient

    @property
    def id(self) -> IngredientId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def properties(self) -> IngredientProperties:
        return self._properties

    @property
    def is_optional(self) -> bool:
        return self._is_optional

    @property
    def substitutes(self) -> List[str]:
        return self._substitutes.copy()

    def is_suitable_for(self, diet: DietType) -> bool:
        """Check if ingredient is suitable for a specific diet"""
        return self.properties.is_compatible_with(diet)

    def scale_quantity(self, factor: Decimal) -> "Ingredient":
        """Scale the ingredient quantity by a factor"""
        if factor < 0:
            raise RecipeValidationException(
                "Scaling factor cannot be negative", "INVALID_SCALING_FACTOR"
            )

        scaled_quantity = self.quantity.scale(factor)

        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=scaled_quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=self.substitutes,
        )

    def update_name(self, name: str) -> "Ingredient":
        """Create a new ingredient with updated name"""
        if not name or not name.strip():
            raise RecipeValidationException(
                "Ingredient name cannot be empty", "EMPTY_INGREDIENT_NAME"
            )

        return Ingredient.reconstruct(
            id=self.id,
            name=name.strip(),
            quantity=self.quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=self.substitutes,
        )

    def update_quantity(self, quantity: Quantity) -> "Ingredient":
        """Create a new ingredient with updated quantity"""
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=self.substitutes,
        )

    def update_properties(self, properties: IngredientProperties) -> "Ingredient":
        """Create a new ingredient with updated properties"""
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            properties=properties,
            is_optional=self.is_optional,
            substitutes=self.substitutes,
        )

    def mark_as_optional(self) -> "Ingredient":
        """Create a new ingredient marked as optional"""
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            properties=self.properties,
            is_optional=True,
            substitutes=self.substitutes,
        )

    def mark_as_required(self) -> "Ingredient":
        """Create a new ingredient marked as required"""
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            properties=self.properties,
            is_optional=False,
            substitutes=self.substitutes,
        )

    def add_substitute(self, substitute: str) -> "Ingredient":
        """Create a new ingredient with added substitute"""
        if not substitute or not substitute.strip():
            raise RecipeValidationException(
                "Substitute cannot be empty", "EMPTY_SUBSTITUTE"
            )

        new_substitutes = self.substitutes + [substitute.strip()]
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=new_substitutes,
        )

    def remove_substitute(self, substitute: str) -> "Ingredient":
        """Create a new ingredient with removed substitute"""
        new_substitutes = [s for s in self.substitutes if s != substitute]
        return Ingredient.reconstruct(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=new_substitutes,
        )

    def __repr__(self):
        return f"Ingredient(id={self.id}, name='{self.name}', quantity={self.quantity}, is_optional={self.is_optional})"

    def __str__(self):
        optional_text = " (optional)" if self.is_optional else ""
        return f"{self.quantity} of {self.name}{optional_text}"

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
