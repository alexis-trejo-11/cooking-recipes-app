from dataclasses import dataclass, field
from typing import Optional, Set, List
from decimal import Decimal
from .value_objects import *
from .enums import DietType


@dataclass(frozen=True)
class IngredientProperties:
    is_vegan: bool = True
    is_vegetarian: bool = True
    is_gluten_free: bool = True
    is_dairy_free: bool = True
    allergens: Set[str] = field(default_factory=set)  # {"dairy", "nuts", "soy"}

    def is_compatible_with(self, diet: DietType) -> bool:
        comptaibility_map = {
            DietType.VEGAN: self.is_vegan,
            DietType.VEGETARIAN: self.is_vegetarian,
            DietType.GLUTEN_FREE: self.is_gluten_free,
            DietType.DAIRY_FREE: self.is_dairy_free,
            DietType.REGULAR: True,
            DietType.KETO: False,  # TODO: ADD LOGIC
        }

        return comptaibility_map.get(diet, True)


class Ingredient:
    def __init__(
        self,
        id: IngredientId,
        name: str,
        quantity: Quantity,
        properties: IngredientProperties,
        is_optional: bool = False,
        substitutes: Optional[List[str]] = None,
    ):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.properties = properties
        self.is_optional = is_optional
        self.substitutes = substitutes or []

    def is_suitable_for(self, diet: DietType) -> bool:
        return self.properties.is_compatible_with(diet)

    def scale_quantity(self, factor: Decimal) -> "Ingredient":
        """Scale the ingredient quantity by a factor"""
        scaled_quantity = self.quantity.scale(factor)
        return Ingredient(
            id=self.id,
            name=self.name,
            quantity=scaled_quantity,
            properties=self.properties,
            is_optional=self.is_optional,
            substitutes=self.substitutes,
        )

    def __repr__(self):
        return f"Ingredient(id={self.id}, name='{self.name}', quantity={self.quantity}, is_optional={self.is_optional})"
