export enum DietType {
  VEGAN = 'vegan',
  VEGETARIAN = 'vegetarian',
  GLUTEN_FREE = 'gluten_free',
  DAIRY_FREE = 'dairy_free',
  KETO = 'keto',
  REGULAR = 'regular',
}

export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum CuisineType {
  ITALIAN = 'italian',
  MEXICAN = 'mexican',
  CHINESE = 'chinese',
  JAPANESE = 'japanese',
  INDIAN = 'indian',
  FRENCH = 'french',
  MEDITERRANEAN = 'mediterranean',
  AMERICAN = 'american',
  THAI = 'thai',
  ASIAN = 'asian',
  GREEK = 'greek',
  SPANISH = 'spanish',
  FUSION = 'fusion',
  OTHER = 'other',
  UNKNOWN = 'unknown',
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
  author_id: number;
  image_url?: string | null;
  author_name?: string | null;
  description?: string | null;
  cuisine: CuisineType;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  total_time_minutes?: number | null;
  servings: number;
  average_rating: number;
  rating_count: number;
  view_count: number;
  favorite_count: number;
  tags: TagResponse[];
  meal_types: MealType[];
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

export interface PaginationResponse {
  total_items: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next_page?: number | null;
  previous_page?: number | null;
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
  is_vegan: boolean;
  is_vegetarian: boolean;
  is_gluten_free: boolean;
  is_dairy_free: boolean;
  allergens: string[]; // Set[str] -> array
}

export interface Ingredient {
  id: number;
  name: string;
  quantity: Quantity;
  properties: IngredientProperties;
  is_optional: boolean;
  substitutes: string[];
}

export interface Step {
  number: number;
  description: string;
  duration_minutes?: number | null;
  technique?: string | null;
  temperature?: string | null;
}

export interface Tag {
  name: string;
  description?: string | null;
}

export interface NutritionalInfo {
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
}

export interface Recipe {
  id: string;
  name: string;
  author_id: number;
  author_name?: string | null;
  description?: string | null;
  difficulty: DifficultyLevel;
  cuisine?: CuisineType | null;
  diet: DietType;
  ingredients: Ingredient[];
  steps: Step[];
  tags: Tag[];
  meal_types: MealType[];
  servings?: number | null;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  total_time_minutes?: number | null;
  nutritional_info?: NutritionalInfo | null;
  average_rating?: number | null;
  rating_count: number;
  view_count: number;
  favorite_count: number;
  version: number;
  created_at: string;
  updated_at: string;
  instructions?: string[] | null;
  image_url?: string | null;
}

// Small s
export interface RecipeCreated {
  id: number;
  name: string;
  message?: string; // default "Recipe created successfully"
}

export interface RatingAdded {
  recipe_id: number;
  new_average_rating?: number | null;
  total_ratings: number;
  message?: string; // default "Rating added successfully"
}

export interface RecipeScaled {
  original_recipe_id: number;
  scaled_recipe_id: number;
  factor: number;
  message?: string; // default "Recipe scaled successfully"
}

// Pagination  used by RecipePage
export interface Pagination {
  total_items: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next_page?: number | null;
  previous_page?: number | null;
}
