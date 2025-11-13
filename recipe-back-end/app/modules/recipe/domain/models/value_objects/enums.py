from enum import Enum


class DietType(Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    REGULAR = "regular"
    UNKNOWN = "unknown"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"

    def is_valid(self) -> bool:
        return self != DifficultyLevel.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"
    APPETIZER = "appetizer"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class CuisineType(Enum):
    ITALIAN = "italian"
    MEXICAN = "mexican"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    INDIAN = "indian"
    FRENCH = "french"
    GREEK = "greek"
    MEDITERRANEAN = "mediterranean"
    AMERICAN = "american"
    THAI = "thai"
    ASIAN = "asian"
    SPANISH = "spanish"
    FUSION = "fusion"
    OTHER = "other"
    UNKNOWN = "unknown"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value
