export enum DietType {
  VEGAN = 'vegan',
  VEGETARIAN = 'vegetarian',
  GLUTEN_FREE = 'gluten_free',
  DAIRY_FREE = 'dairy_free',
  KETO = 'keto',
  REGULAR = 'regular',
}

export enum DifficultyLevel {
  EASY = 'Easy',
  MEDIUM = 'Medium',
  HARD = 'Hard',
}

export enum CuisineType {
  ITALIAN = 'Italian',
  MEXICAN = 'Mexican',
  CHINESE = 'Chinese',
  JAPANESE = 'Japanese',
  INDIAN = 'Indian',
  FRENCH = 'French',
  MEDITERRANEAN = 'Mediterranean',
  AMERICAN = 'American',
  THAI = 'Thai',
  ASIAN = 'Asian',
  GREEK = 'Greek',
  SPANISH = 'Spanish',
  FUSION = 'Fusion',
  OTHER = 'Other',
  UNKNOWN = 'Unknown',
}

export enum MealType {
  BREAKFAST = 'breakfast',
  LUNCH = 'lunch',
  DINNER = 'dinner',
  SNACK = 'snack',
  DESSERT = 'dessert',
}

export interface TagResponse {
  name: string;
  description?: string | null;
}

export interface RecipeSummary {
  id: number;
  name: string;
  difficulty: DifficultyLevel;
  authorId: number;
  imageUrl?: string | null;
  authorName?: string | null;
  description?: string | null;
  cuisine: CuisineType;
  prepTimeMinutes?: number | null;
  cookTimeMinutes?: number | null;
  totalTimeMinutes?: number | null;
  servings: number;
  averageRating: number;
  ratingCount: number;
  viewCount: number;
  favoriteCount: number;
  tags: TagResponse[];
  mealTypes: MealType[];
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
}

export interface PaginationResponse {
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
  nextPage?: number | null;
  previousPage?: number | null;
}

export interface RecipeSummaryPage {
  recipes: RecipeSummary[];
  pagination: PaginationResponse;
}

export interface Quantity {
  value: number;
  unit: string;
}

export interface IngredientProperties {
  isVegan: boolean;
  isVegetarian: boolean;
  isGlutenFree: boolean;
  isDairyFree: boolean;
  allergens: string[]; // Set[str] -> array
}

export interface Ingredient {
  id: number;
  name: string;
  quantity: Quantity;
  properties: IngredientProperties;
  isOptional: boolean;
  substitutes: string[];
}

export interface Step {
  number: number;
  description: string;
  durationMinutes?: number | null;
  technique?: string | null;
  temperature?: string | null;
}

export interface Tag {
  name: string;
  description?: string | null;
}

export interface NutritionalInfo {
  calories?: number | null;
  proteinG?: number | null;
  carbsG?: number | null;
  fatG?: number | null;
}

export interface Recipe {
  id: string;
  name: string;
  authorId: string;
  authorName: string | null;
  description: string | null;
  difficulty: DifficultyLevel;
  cuisine: CuisineType;
  diet: DietType;
  ingredients: Ingredient[];
  steps: Step[];
  tags: Tag[];
  mealTypes: MealType[];
  servings?: number | null;
  prepTimeMinutes?: number | null;
  cookTimeMinutes?: number | null;
  totalTimeMinutes?: number | null;
  nutritionalInfo?: NutritionalInfo | null;
  averageRating?: number | null;
  ratingCount: number;
  viewCount: number;
  favoriteCount: number;
  version: number;
  createdAt: string;
  updatedAt: string;
  instructions?: string[] | null;
  imageUrl?: string | null;
}

// Small s
export interface RecipeCreated {
  id: number;
  name: string;
  message?: string; // default "Recipe created successfully"
}

export interface RatingAdded {
  recipeId: number;
  newAverageRating?: number | null;
  totalRatings: number;
  message?: string; // default "Rating added successfully"
}

export interface RecipeScaled {
  originalRecipeId: number;
  scaledRecipeId: number;
  factor: number;
  message?: string; // default "Recipe scaled successfully"
}

// Pagination  used by RecipePage
export interface Pagination {
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
  nextPage?: number | null;
  previousPage?: number | null;
}

type DecimalString = string;

export interface QuantityRequest {
  /** Quantity value */
  value: DecimalString;
  /** Quantity unit */
  unit: string;
}

export interface IngredientPropertiesRequest {
  isVegan: boolean;
  isVegetarian: boolean;
  isGlutenFree: boolean;
  isDairyFree: boolean;
  allergens: string[];
}

export interface CreateIngredientRequest {
  /** Ingredient name */
  name: string;
  quantity: QuantityRequest;
  properties: IngredientPropertiesRequest;
  isOptional: boolean;
  substitutes: string[];
}

export interface CreateStepRequest {
  /** Step description */
  description: string;
  /** Duration in minutes */
  durationMinutes?: number | null;
  /** Cooking technique */
  technique?: string | null;
  /** Cooking temperature */
  temperature?: string | null;
}

export interface TagRequest {
  /** Tag name */
  name: string;
  /** Tag description */
  description?: string | null;
}

export interface NutritionalInfoRequest {
  /** Calories per serving */
  calories?: number | null;
  /** Protein in grams */
  proteinG?: DecimalString | null;
  /** Carbs in grams */
  carbsG?: DecimalString | null;
  /** Fat in grams */
  fatG?: DecimalString | null;
  /** Fiber in grams */
  fiberG?: DecimalString | null;
  /** Sodium in mg */
  sodiumMg?: DecimalString | null;
}

export interface CookingTimeRequest {
  /** Preparation time */
  prepMinutes: number;
  /** Cooking time */
  cookMinutes: number;
}

export interface CreateRecipeRequest {
  // Required fields
  /** Recipe name */
  name: string;
  /** Difficulty level */
  difficulty: DifficultyLevel;
  /** Cuisine type */
  cuisine: CuisineType;
  ingredients: CreateIngredientRequest[];
  steps: CreateStepRequest[];
  tags: TagRequest[];
  mealTypes: MealType[];

  // Optional fields
  /** Recipe description */
  description: string | null;
  /** URL of the recipe image */
  imageUrl?: string | null;
  /** Number of servings */
  servings: number;
  /** Cooking time information */
  cookingTime: CookingTimeRequest;
  /** Nutritional information */
  nutritionalInfo?: NutritionalInfoRequest | null;
}

export interface UpdateRecipeRequest {
  name?: string | null;
  description?: string | null;
  difficulty?: DifficultyLevel | null;
  cuisine?: CuisineType | null;
  ingredients?: CreateIngredientRequest[] | null;
  steps?: CreateStepRequest[] | null;
  tags?: TagRequest[] | null;
  mealTypes?: MealType[] | null;
  servings?: number | null;
  prepTimeMinutes?: number | null;
  cookTimeMinutes?: number | null;
  calories?: number | null;
  proteinG?: DecimalString | null;
  carbsG?: DecimalString | null;
  fatG?: DecimalString | null;
}
