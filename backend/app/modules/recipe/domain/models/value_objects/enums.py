from enum import Enum


class DietType(Enum):
    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarian"
    GLUTEN_FREE = "Gluten Free"
    DAIRY_FREE = "Dairy Free"
    KETO = "Keto"
    PALEO = "Paleo"
    REGULAR = "Regular"
    UNKNOWN = "Unknown"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class DifficultyLevel(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    UNKNOWN = "Unknown"

    def is_valid(self) -> bool:
        return self != DifficultyLevel.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class MealType(Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"
    DESSERT = "Dessert"
    APPETIZER = "Appetizer"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value


class CuisineType(Enum):
    ITALIAN = "Italian"
    MEXICAN = "Mexican"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"
    INDIAN = "Indian"
    FRENCH = "French"
    GREEK = "Greek"
    MEDITERRANEAN = "Mediterranean"
    AMERICAN = "American"
    THAI = "Thai"
    ASIAN = "Asian"
    SPANISH = "Spanish"
    FUSION = "Fusion"
    OTHER = "Other"
    UNKNOWN = "Unknown"

    def is_valid(self) -> bool:
        return self != DietType.UNKNOWN and self != None and self != ""

    def __str__(self):
        return self.value
