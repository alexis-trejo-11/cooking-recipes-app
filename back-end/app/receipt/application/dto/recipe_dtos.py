from pydantic import BaseModel, Field, validator
from typing import Optional, List, Set, Dict, Any
from decimal import Decimal
from datetime import datetime
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
    query: Optional[str] = Field(None, description="Search query")
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
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")


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

    class Config:
        from_attributes = True


class PaginatedRecipesResponse(BaseModel):
    recipes: List[RecipeSummaryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


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
