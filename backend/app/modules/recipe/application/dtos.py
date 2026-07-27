from typing import Optional, List, Set, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator

from app.utils.core.pagination import Page
from app.utils.external.page_request import (
    PydanticPaginationParams,
    PydanticPaginationResponse,
)
from app.modules.recipe.domain.models.entities.review import Review
from app.modules.recipe.domain.models.entities.ingredient import (
    IngredientProperties,
    Ingredient,
)
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    RecipeId,
    UserId,
    Quantity,
    Step,
    Tag,
    ServingInfo,
    NutritionalInfo,
    CookingTime,
    DifficultyLevel as DomainDifficultyLevel,
    CuisineType as DomainCuisineType,
    MealType as DomainMealType,
)
from app.modules.recipe.infrastructure.persistence.specification_builder import (
    RecipeSearchCriteria,
)


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class CuisineType(str, Enum):
    ITALIAN = "Italian"
    MEXICAN = "Mexican"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"
    INDIAN = "Indian"
    FRENCH = "French"
    MEDITERRANEAN = "Mediterranean"
    AMERICAN = "American"
    THAI = "Thai"
    ASIAN = "Asian"
    GREEK = "Greek"
    SPANISH = "Spanish"
    FUSION = "Fusion"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"
    DESSERT = "Dessert"


# to
class DietType(str, Enum):
    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarian"
    GLUTEN_FREE = "Gluten_free"
    DAIRY_FREE = "Dairy_free"
    KETO = "Keto"
    REGULAR = "Regular"


class QuantityRequest(BaseModel):
    value: Decimal = Field(..., gt=0, description="Quantity value")
    unit: str = Field(..., min_length=1, max_length=50, description="Quantity unit")

    def to_domain(self) -> Quantity:
        return Quantity(value=self.value, unit=self.unit)


class IngredientPropertiesRequest(BaseModel):
    is_vegan: bool = Field(default=True)
    is_vegetarian: bool = Field(default=True)
    is_gluten_free: bool = Field(default=True)
    is_dairy_free: bool = Field(default=True)
    allergens: Set[str] = Field(default_factory=set)

    def to_domain(self) -> IngredientProperties:
        return IngredientProperties(
            is_vegan=self.is_vegan,
            is_vegetarian=self.is_vegetarian,
            is_gluten_free=self.is_gluten_free,
            is_dairy_free=self.is_dairy_free,
            allergens=set(self.allergens),
        )


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


class NutritionalInfoRequest(BaseModel):
    calories: Optional[int] = Field(None, ge=0, description="Calories per serving")
    protein_g: Optional[Decimal] = Field(None, ge=0, description="Protein in grams")
    carbs_g: Optional[Decimal] = Field(None, ge=0, description="Carbs in grams")
    fat_g: Optional[Decimal] = Field(None, ge=0, description="Fat in grams")
    fiber_g: Optional[Decimal] = Field(None, ge=0, description="Fiber in grams")
    sodium_mg: Optional[Decimal] = Field(None, ge=0, description="Sodium in mg")


class CookingTimeRequest(BaseModel):
    prep_minutes: int = Field(..., ge=0, description="Preparation time")
    cook_minutes: int = Field(..., ge=0, description="Cooking time")


class CreateRecipeRequest(BaseModel):
    # Required fields
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    cuisine: CuisineType = Field(..., description="Cuisine type")
    ingredients: List[CreateIngredientRequest] = Field(
        default_factory=list, min_length=1, max_length=100
    )
    steps: List[CreateStepRequest] = Field(
        default_factory=list, min_length=1, max_length=100
    )
    tags: List[TagRequest] = Field(default_factory=list, min_length=1, max_length=10)
    meal_types: List[MealType] = Field(default_factory=list, min_length=1, max_length=5)

    # Optional fields
    description: Optional[str] = Field(
        ..., min_length=10, max_length=255, description="Recipe description"
    )
    image_url: Optional[str] = Field(None, description="URL of the recipe image")
    servings: int = Field(..., gt=0, description="Number of servings")
    cooking_time: CookingTimeRequest = Field(
        ..., description="Cooking time information"
    )
    nutritional_info: Optional[NutritionalInfoRequest] = Field(
        None, description="Nutritional information"
    )

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

    def create_ingredients(self) -> List[Ingredient]:
        return [
            Ingredient.create(
                name=ing_dto.name,
                quantity=ing_dto.quantity.to_domain(),
                properties=ing_dto.properties.to_domain(),
                is_optional=ing_dto.is_optional,
                substitutes=ing_dto.substitutes,
            )
            for ing_dto in self.ingredients
        ]

    def create_steps(self) -> List[Step]:
        return [
            Step(
                number=index + 1,
                description=step_dto.description,
                duration_minutes=step_dto.duration_minutes,
                technique=step_dto.technique,
                temperature=step_dto.temperature,
            )
            for index, step_dto in enumerate(self.steps)
        ]

    def create_tags(self) -> Set[Tag]:
        return {
            Tag(name=tag_dto.name, description=tag_dto.description)
            for tag_dto in self.tags
        }

    def create_meal_types(self) -> Set[DomainMealType]:
        return {DomainMealType(meal_type) for meal_type in self.meal_types}

    def create_serving_info(self) -> ServingInfo:
        return ServingInfo(servings=self.servings)

    def create_cooking_time(self) -> CookingTime:
        return CookingTime(
            prep_minutes=self.cooking_time.prep_minutes,
            cook_minutes=self.cooking_time.cook_minutes,
        )

    def create_nutritional_info(self) -> Optional[NutritionalInfo]:
        if self.nutritional_info:
            return NutritionalInfo(
                calories=self.nutritional_info.calories,
                protein_g=self.nutritional_info.protein_g,
                carbs_g=self.nutritional_info.carbs_g,
                fat_g=self.nutritional_info.fat_g,
                fiber_g=self.nutritional_info.fiber_g,
                sodium_mg=self.nutritional_info.sodium_mg,
            )
        return None


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

    def create_ingredients(self) -> Optional[List[Ingredient]]:
        if self.ingredients is None:
            return None
        return [
            Ingredient.create(
                name=ing_dto.name,
                quantity=ing_dto.quantity.to_domain(),
                properties=ing_dto.properties.to_domain(),
                is_optional=ing_dto.is_optional,
                substitutes=ing_dto.substitutes,
            )
            for ing_dto in self.ingredients
        ]

    def create_steps(self) -> Optional[List[Step]]:
        if self.steps is None:
            return None
        return [
            Step(
                number=index + 1,
                description=step_dto.description,
                duration_minutes=step_dto.duration_minutes,
                technique=step_dto.technique,
                temperature=step_dto.temperature,
            )
            for index, step_dto in enumerate(self.steps)
        ]

    def create_tags(self) -> Optional[Set[Tag]]:
        if self.tags is None:
            return None
        return {
            Tag(name=tag_dto.name, description=tag_dto.description)
            for tag_dto in self.tags
        }

    def create_meal_types(self) -> Optional[Set[DomainMealType]]:
        if self.meal_types is None:
            return None
        return {DomainMealType(meal_type) for meal_type in self.meal_types}

    def create_serving_info(self) -> Optional[ServingInfo]:
        if self.servings is not None:
            return ServingInfo(servings=self.servings)
        return None

    def create_cooking_time(self) -> Optional[CookingTime]:
        if self.prep_time_minutes is not None or self.cook_time_minutes is not None:
            return CookingTime(
                prep_minutes=self.prep_time_minutes or 0,
                cook_minutes=self.cook_time_minutes or 0,
            )
        return None

    def create_nutritional_info(self) -> Optional[NutritionalInfo]:
        if any(
            [
                self.calories is not None,
                self.protein_g is not None,
                self.carbs_g is not None,
                self.fat_g is not None,
            ]
        ):
            return NutritionalInfo(
                calories=self.calories or 0,
                protein_g=self.protein_g or Decimal("0"),
                carbs_g=self.carbs_g or Decimal("0"),
                fat_g=self.fat_g or Decimal("0"),
            )
        return None


class ScaleRecipeRequest(BaseModel):
    factor: Decimal = Field(..., gt=0, description="Scaling factor")
    adjust_cooking_time: bool = Field(
        default=True, description="Whether to adjust cooking time"
    )


class CreateReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., max_length=500, description="Review comment")

    def to_domain(self, recipe_id: RecipeId, user_id: UserId) -> Review:
        return Review.create(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=self.rating,
            comment=self.comment,
        )


class UpdateReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., max_length=500, description="Review comment")


class ReviewResponse(BaseModel):
    recipe_id: int = Field(..., description="Recipe ID")
    user_id: int = Field(..., description="User ID")
    rating: int = Field(..., description="Rating value")
    comment: str = Field(..., description="Review comment")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_review(cls, review: Review) -> "ReviewResponse":
        return cls(
            recipe_id=review.recipe_id.value,
            user_id=review.user_id.value,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


class ReviewPageResponse(BaseModel):
    reviews: List[ReviewResponse]
    pagination: PydanticPaginationResponse

    @classmethod
    def from_page(cls, review_page: Page[ReviewResponse]) -> "ReviewPageResponse":
        return cls(
            reviews=review_page.items,
            pagination=PydanticPaginationResponse(
                total_items=review_page.total,
                total_pages=review_page.total_pages,
                current_page=review_page.page,
                page_size=review_page.size,
                has_next_page=review_page.has_next_page,
                has_prev_page=review_page.has_prev_page,
            ),
        )


class RecipeSearchRequest(BaseModel):
    """Pydantic DTO for recipe search requests."""

    # Basic filters
    name: Optional[str] = Field(
        None, max_length=200, description="Recipe name (partial match)"
    )
    author_id: Optional[int] = Field(None, ge=1, description="Author ID")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    cuisine: Optional[str] = Field(None, description="Cuisine type")

    # Collections filters
    tags: Optional[List[str]] = Field(
        None, description="Tags (recipes must have ALL tags)"
    )
    meal_types: Optional[List[str]] = Field(None, description="Meal types")
    ingredient_name: Optional[str] = Field(
        None, description="Ingredient name (partial match)"
    )

    # Rating and time filters
    min_rating: Optional[float] = Field(
        None, ge=0, le=5, description="Minimum rating (0-5)"
    )
    max_cooking_time: Optional[int] = Field(
        None, ge=1, description="Maximum cooking time in minutes"
    )

    include_deleted: bool = Field(default=False, description="Include deleted recipes")
    pagination: PydanticPaginationParams = Field(
        ..., description="Pagination parameters"
    )

    @validator("name")
    def validate_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Name cannot be empty if provided")
        return v

    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError("Tags cannot be empty")
        return v

    @validator("meal_types")
    def validate_meal_types(cls, v):
        valid_meal_types = {"breakfast", "lunch", "dinner", "snack", "dessert"}
        if v is not None:
            for meal_type in v:
                if meal_type.lower() not in valid_meal_types:
                    raise ValueError(f"Invalid meal type: {meal_type}")
        return v

    def to_search_criteria(self):
        """Convert to domain search criteria."""
        return RecipeSearchCriteria(
            name=self.name,
            author_id=UserId(self.author_id) if self.author_id else None,
            difficulty=(
                DomainDifficultyLevel(self.difficulty) if self.difficulty else None
            ),
            cuisine=DomainCuisineType(self.cuisine) if self.cuisine else None,
            tags=set(self.tags) if self.tags else None,
            meal_types=(
                {DomainMealType(mt) for mt in self.meal_types}
                if self.meal_types
                else None
            ),
            ingredient_name=self.ingredient_name,
            min_rating=self.min_rating,
            max_cooking_time=self.max_cooking_time,
            include_deleted=self.include_deleted,
        )


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
    difficulty: DifficultyLevel
    author_id: int
    image_url: Optional[str]
    author_name: Optional[str]
    description: Optional[str]
    cuisine: Optional[CuisineType]
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
    def from_recipe(cls, recipe: Recipe) -> "RecipeSummaryResponse":
        return cls(
            id=recipe.id.value,
            name=recipe.name,
            author_name=None,
            description=recipe.description,
            difficulty=DifficultyLevel(recipe.difficulty.value),
            cuisine=CuisineType(recipe.cuisine.value),
            image_url=recipe.image_url,
            author_id=recipe.author_id.value,
            prep_time_minutes=(
                recipe.cooking_time.prep_minutes if recipe.cooking_time else None
            ),
            cook_time_minutes=(
                recipe.cooking_time.cook_minutes if recipe.cooking_time else None
            ),
            total_time_minutes=recipe.calculate_total_time(),
            servings=(recipe.serving_info.servings if recipe.serving_info else None),
            average_rating=(
                Decimal(str(recipe.average_rating))
                if recipe.average_rating is not None
                else None
            ),
            rating_count=recipe.review_count,
            view_count=recipe.view_count,
            favorite_count=recipe.favorite_count,
            tags=[
                TagResponse(name=tag.name, description=tag.description)
                for tag in recipe.tags
            ],
            meal_types=list(MealType(mt.value) for mt in recipe.meal_types),
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    @classmethod
    def from_recipes(cls, recipes: List[Any]) -> List["RecipeSummaryResponse"]:
        return [cls.from_recipe(recipe) for recipe in recipes]


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
    def from_recipe(cls, recipe: Recipe) -> "RecipeResponse":
        ingredients_response = []
        for ingredient in recipe.ingredients:
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
        for step in recipe.steps:
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
        for tag in recipe.tags:
            tags_response.append(
                TagResponse(name=tag.name, description=tag.description)
            )

        nutritional_info = None
        if recipe.nutritional_info:
            nutritional_info = NutritionalInfoResponse(
                calories=recipe.nutritional_info.calories,
                protein_g=recipe.nutritional_info.protein_g,
                carbs_g=recipe.nutritional_info.carbs_g,
                fat_g=recipe.nutritional_info.fat_g,
            )

        return RecipeResponse(
            id=recipe.id.value,
            name=recipe.name,
            author_id=recipe.author_id.value,
            author_name=None,  # Would need user service to get author name
            description=recipe.description,
            difficulty=DifficultyLevel(recipe.difficulty.value),
            cuisine=CuisineType(recipe.cuisine.value),
            ingredients=ingredients_response,
            steps=steps_response,
            tags=tags_response,
            meal_types=list(MealType(mt.value) for mt in recipe.meal_types),
            servings=(recipe.serving_info.servings if recipe.serving_info else None),
            prep_time_minutes=(
                recipe.cooking_time.prep_minutes if recipe.cooking_time else None
            ),
            cook_time_minutes=(
                recipe.cooking_time.cook_minutes if recipe.cooking_time else None
            ),
            total_time_minutes=recipe.calculate_total_time(),
            nutritional_info=nutritional_info,
            average_rating=Decimal(
                str(recipe.average_rating) if recipe.average_rating else "0"
            ),
            rating_count=recipe.review_count,
            view_count=recipe.view_count,
            favorite_count=recipe.favorite_count,
            version=recipe.version,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
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


class ReviewCreatedResponse(BaseModel):
    recipe_id: int
    new_average_rating: Optional[Decimal]
    total_ratings: int
    message: str = "Rating added successfully"


class RecipePageResponse(BaseModel):
    recipes: List[RecipeSummaryResponse]
    pagination: PydanticPaginationResponse

    @classmethod
    def from_page(
        cls, recipe_page: Page[RecipeSummaryResponse]
    ) -> "RecipePageResponse":
        return cls(
            recipes=recipe_page.items,
            pagination=PydanticPaginationResponse(
                total_items=recipe_page.total,
                total_pages=recipe_page.total_pages,
                current_page=recipe_page.page,
                page_size=recipe_page.size,
                has_next_page=recipe_page.has_next_page,
                has_prev_page=recipe_page.has_prev_page,
            ),
        )
