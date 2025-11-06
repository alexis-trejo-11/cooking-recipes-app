from pydantic import BaseModel, Field, validator
from typing import Optional, List, Set, Dict, Any
from decimal import Decimal
from app.utils.page_request import PydnaticPageRequest
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CuisineType(str, Enum):
    ITALIAN = "italian"
    MEXICAN = "mexican"
    ASIAN = "asian"
    AMERICAN = "american"
    MEDITERRANEAN = "mediterranean"
    OTHER = "other"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class DietType(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    REGULAR = "regular"


class QuantityRequest(BaseModel):
    value: Decimal = Field(..., gt=0, description="Quantity value")
    unit: str = Field(..., min_length=1, max_length=50, description="Quantity unit")


class IngredientPropertiesRequest(BaseModel):
    is_vegan: bool = Field(default=True)
    is_vegetarian: bool = Field(default=True)
    is_gluten_free: bool = Field(default=True)
    is_dairy_free: bool = Field(default=True)
    allergens: Set[str] = Field(default_factory=set)


class CreateIngredientRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Ingredient name")
    quantity: QuantityRequest
    properties: IngredientPropertiesRequest
    is_optional: bool = Field(default=False)
    substitutes: List[str] = Field(default_factory=list)


class CreateStepRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Step description")
    duration_minutes: Optional[int] = Field(
        None, ge=0, description="Duration in minutes"
    )
    technique: Optional[str] = Field(
        None, max_length=100, description="Cooking technique"
    )
    temperature: Optional[str] = Field(
        None, max_length=50, description="Cooking temperature"
    )


class TagRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")


class CreateRecipeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    author_id: int = Field(..., gt=0, description="Author user ID")
    description: Optional[str] = Field(None, description="Recipe description")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    cuisine: Optional[CuisineType] = Field(None, description="Cuisine type")
    ingredients: List[CreateIngredientRequest] = Field(default_factory=list)
    steps: List[CreateStepRequest] = Field(default_factory=list)
    tags: List[TagRequest] = Field(default_factory=list)
    meal_types: List[MealType] = Field(default_factory=list)
    servings: Optional[int] = Field(None, gt=0, description="Number of servings")
    prep_time_minutes: Optional[int] = Field(
        None, ge=0, description="Prep time in minutes"
    )
    cook_time_minutes: Optional[int] = Field(
        None, ge=0, description="Cook time in minutes"
    )
    calories: Optional[int] = Field(None, ge=0, description="Calories per serving")
    protein_g: Optional[Decimal] = Field(None, ge=0, description="Protein in grams")
    carbs_g: Optional[Decimal] = Field(None, ge=0, description="Carbs in grams")
    fat_g: Optional[Decimal] = Field(None, ge=0, description="Fat in grams")

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Recipe name cannot be empty")
        return v.strip()

    @validator("description")
    def description_validation(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class UpdateRecipeRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    difficulty: Optional[DifficultyLevel] = Field(None)
    cuisine: Optional[CuisineType] = Field(None)
    ingredients: Optional[List[CreateIngredientRequest]] = Field(None)
    steps: Optional[List[CreateStepRequest]] = Field(None)
    tags: Optional[List[TagRequest]] = Field(None)
    meal_types: Optional[List[MealType]] = Field(None)
    servings: Optional[int] = Field(None, gt=0)
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    protein_g: Optional[Decimal] = Field(None, ge=0)
    carbs_g: Optional[Decimal] = Field(None, ge=0)
    fat_g: Optional[Decimal] = Field(None, ge=0)

    @validator("name")
    def name_validation(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Recipe name cannot be empty")
            return v.strip()
        return v

    @validator("description")
    def description_validation(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class ScaleRecipeRequest(BaseModel):
    factor: Decimal = Field(..., gt=0, description="Scaling factor")
    adjust_cooking_time: bool = Field(
        default=True, description="Whether to adjust cooking time"
    )


class AddRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")


class RecipeSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    author_id: Optional[int] = Field(None, gt=0, description="Filter by author")
    difficulty: Optional[DifficultyLevel] = Field(
        None, description="Filter by difficulty"
    )
    cuisine: Optional[CuisineType] = Field(None, description="Filter by cuisine")
    meal_type: Optional[MealType] = Field(None, description="Filter by meal type")
    diet: Optional[DietType] = Field(None, description="Filter by diet type")
    max_prep_time: Optional[int] = Field(None, ge=0, description="Maximum prep time")
    max_cook_time: Optional[int] = Field(None, ge=0, description="Maximum cook time")
    min_rating: Optional[Decimal] = Field(
        None, ge=0, le=5, description="Minimum rating"
    )
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    exclude_allergens: List[str] = Field(
        default_factory=list, description="Exclude allergens"
    )
    pagination: PydnaticPageRequest = Field(..., description="Pagination parameters")

    def is_empty(self) -> bool:
        return not any(
            [
                self.query,
                self.author_id,
                self.difficulty,
                self.cuisine,
                self.meal_type,
                self.diet,
                self.max_prep_time is not None,
                self.max_cook_time is not None,
                self.min_rating is not None,
                self.tags,
                self.exclude_allergens,
            ]
        )


class FindByIngredientsRequest(BaseModel):
    ingredients: List[str] = Field(
        ..., min_length=1, description="List of ingredient names"
    )
    include_optional: bool = Field(
        default=False, description="Include optional ingredients in search"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")


# Response DTOs
class QuantityResponse(BaseModel):
    value: Decimal
    unit: str


class IngredientPropertiesResponse(BaseModel):
    is_vegan: bool
    is_vegetarian: bool
    is_gluten_free: bool
    is_dairy_free: bool
    allergens: Set[str]


class IngredientResponse(BaseModel):
    id: int
    name: str
    quantity: QuantityResponse
    properties: IngredientPropertiesResponse
    is_optional: bool
    substitutes: List[str]


class StepResponse(BaseModel):
    number: int
    description: str
    duration_minutes: Optional[int]
    technique: Optional[str]
    temperature: Optional[str]


class TagResponse(BaseModel):
    name: str
    description: Optional[str]


class NutritionalInfoResponse(BaseModel):
    calories: Optional[int]
    protein_g: Optional[Decimal]
    carbs_g: Optional[Decimal]
    fat_g: Optional[Decimal]


class RecipeSummaryResponse(BaseModel):
    id: int
    name: str
    author_id: int
    author_name: Optional[str]
    description: Optional[str]
    difficulty: DifficultyLevel
    cuisine: Optional[CuisineType]
    image_url: Optional[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    servings: Optional[int]
    average_rating: Optional[Decimal]
    rating_count: int
    view_count: int
    favorite_count: int
    tags: List[TagResponse]
    meal_types: List[MealType]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_recipe(cls, recipe: Any) -> "RecipeSummaryResponse":
        return cls(
            id=recipe.id.value,
            name=recipe.name,
            author_id=recipe.author_id.value,
            author_name=None,
            description=recipe.description,
            difficulty=recipe.difficulty,
            cuisine=recipe.cuisine,
            image_url=recipe.image_url,
            prep_time_minutes=(
                recipe.get_cooking_time().prep_minutes
                if recipe.get_cooking_time()
                else None
            ),
            cook_time_minutes=(
                recipe.get_cooking_time().cook_minutes
                if recipe.get_cooking_time()
                else None
            ),
            total_time_minutes=recipe.calculate_total_time(),
            servings=(
                recipe.get_serving_info().servings
                if recipe.get_serving_info()
                else None
            ),
            average_rating=recipe.get_average_rating(),
            rating_count=recipe._rating_count,
            view_count=recipe.get_view_count(),
            favorite_count=recipe.get_favorite_count(),
            tags=[
                TagResponse(name=tag.name, description=tag.description)
                for tag in recipe.get_tags()
            ],
            meal_types=list(recipe.get_meal_types()),
            created_at=recipe.get_created_at(),
            updated_at=recipe.get_updated_at(),
        )


class RecipeResponse(BaseModel):
    id: int
    name: str
    author_id: int
    author_name: Optional[str]
    description: Optional[str]
    difficulty: DifficultyLevel
    cuisine: Optional[CuisineType]
    ingredients: List[IngredientResponse]
    steps: List[StepResponse]
    tags: List[TagResponse]
    meal_types: List[MealType]
    servings: Optional[int]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    nutritional_info: Optional[NutritionalInfoResponse]
    average_rating: Optional[Decimal]
    rating_count: int
    view_count: int
    favorite_count: int
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    @classmethod
    def from_recipe(cls, recipe) -> "RecipeResponse":
        ingredients_response = []
        for ingredient in recipe.get_ingredients():
            ingredients_response.append(
                IngredientResponse(
                    id=ingredient.id.value,
                    name=ingredient.name,
                    quantity=QuantityResponse(
                        value=ingredient.quantity.value, unit=ingredient.quantity.unit
                    ),
                    properties=IngredientPropertiesResponse(
                        is_vegan=ingredient.properties.is_vegan,
                        is_vegetarian=ingredient.properties.is_vegetarian,
                        is_gluten_free=ingredient.properties.is_gluten_free,
                        is_dairy_free=ingredient.properties.is_dairy_free,
                        allergens=ingredient.properties.allergens,
                    ),
                    is_optional=ingredient.is_optional,
                    substitutes=ingredient.substitutes,
                )
            )

        steps_response = []
        for step in recipe.get_steps():
            steps_response.append(
                StepResponse(
                    number=step.number,
                    description=step.description,
                    duration_minutes=step.duration_minutes,
                    technique=step.technique,
                    temperature=step.temperature,
                )
            )

        tags_response = []
        for tag in recipe.get_tags():
            tags_response.append(
                TagResponse(name=tag.name, description=tag.description)
            )

        nutritional_info = None
        if recipe.get_nutritional_info():
            nutritional_info = NutritionalInfoResponse(
                calories=recipe.get_nutritional_info().calories,
                protein_g=recipe.get_nutritional_info().protein_g,
                carbs_g=recipe.get_nutritional_info().carbs_g,
                fat_g=recipe.get_nutritional_info().fat_g,
            )

        return RecipeResponse(
            id=recipe.id.value,
            name=recipe.name,
            author_id=recipe.author_id.value,
            author_name=None,  # Would need user service to get author name
            description=recipe.description,
            difficulty=recipe.difficulty,
            cuisine=recipe.cuisine,
            ingredients=ingredients_response,
            steps=steps_response,
            tags=tags_response,
            meal_types=list(recipe.get_meal_types()),
            servings=(
                recipe.get_serving_info().servings
                if recipe.get_serving_info()
                else None
            ),
            prep_time_minutes=(
                recipe.get_cooking_time().prep_minutes
                if recipe.get_cooking_time()
                else None
            ),
            cook_time_minutes=(
                recipe.get_cooking_time().cook_minutes
                if recipe.get_cooking_time()
                else None
            ),
            total_time_minutes=recipe.calculate_total_time(),
            nutritional_info=nutritional_info,
            average_rating=recipe.get_average_rating(),
            rating_count=recipe._rating_count,
            view_count=recipe.get_view_count(),
            favorite_count=recipe.get_favorite_count(),
            version=recipe.version,
            created_at=recipe.get_created_at(),
            updated_at=recipe.get_updated_at(),
            deleted_at=recipe.deleted_at,
        )

    class Config:
        from_attributes = True


class RecipeCreatedResponse(BaseModel):
    id: int
    name: str
    message: str = "Recipe created successfully"


class RecipeUpdatedResponse(BaseModel):
    id: int
    name: str
    version: int
    message: str = "Recipe updated successfully"


class RecipeDeletedResponse(BaseModel):
    id: int
    message: str = "Recipe deleted successfully"


class RatingAddedResponse(BaseModel):
    recipe_id: int
    new_average_rating: Optional[Decimal]
    total_ratings: int
    message: str = "Rating added successfully"


class RecipeScaledResponse(BaseModel):
    original_recipe_id: int
    scaled_recipe_id: int
    factor: Decimal
    message: str = "Recipe scaled successfully"
