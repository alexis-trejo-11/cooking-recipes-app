export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum CuisineType {
  ITALIAN = 'italian',
  MEXICAN = 'mexican',
  ASIAN = 'asian',
  AMERICAN = 'american',
  MEDITERRANEAN = 'mediterranean',
  OTHER = 'other',
}

export enum DietType {
  VEGAN = 'vegan',
  VEGETARIAN = 'vegetarian',
  GLUTEN_FREE = 'gluten_free',
  DAIRY_FREE = 'dairy_free',
  KETO = 'keto',
  REGULAR = 'regular',
}

export enum MealType {
  BREAKFAST = 'breakfast',
  LUNCH = 'lunch',
  DINNER = 'dinner',
  SNACK = 'snack',
  DESSERT = 'dessert',
}

export function getDummyDetailedRecipe(): Recipe {
  return {
    id: 1,
    name: 'Spaghetti Carbonara',
    author_id: 1,
    description: 'A classic Italian pasta dish made with eggs, cheese, pancetta, and pepper.',
    difficulty: DifficultyLevel.MEDIUM,
    cuisine: CuisineType.ITALIAN,
    ingredients: [
      {
        id: 1,
        name: 'Spaghetti',
        quantity: { value: 200, unit: 'grams' },
        properties: {
          is_vegan: true,
          is_vegetarian: true,
          is_gluten_free: false,
          is_dairy_free: true,
          allergens: ['gluten'],
        },
        is_optional: false,
        substitutes: ['gluten-free pasta'],
      },
      {
        id: 2,
        name: 'Pancetta',
        quantity: { value: 100, unit: 'grams' },
        properties: {
          is_vegan: false,
          is_vegetarian: false,
          is_gluten_free: true,
          is_dairy_free: true,
          allergens: [],
        },
        is_optional: false,
        substitutes: ['bacon', 'smoked turkey'],
      },
      {
        id: 3,
        name: 'Eggs',
        quantity: { value: 2, unit: 'large' },
        properties: {
          is_vegan: false,
          is_vegetarian: true,
          is_gluten_free: true,
          is_dairy_free: true,
          allergens: ['eggs'],
        },
        is_optional: false,
        substitutes: ['egg replacer'],
      },
      {
        id: 4,
        name: 'Parmesan Cheese',
        quantity: { value: 50, unit: 'grams' },
        properties: {
          is_vegan: false,
          is_vegetarian: true,
          is_gluten_free: true,
          is_dairy_free: false,
          allergens: ['dairy'],
        },
        is_optional: false,
        substitutes: ['nutritional yeast', 'vegan cheese'],
      },
      {
        id: 5,
        name: 'Black Pepper',
        quantity: { value: 1, unit: 'teaspoon' },
        properties: {
          is_vegan: true,
          is_vegetarian: true,
          is_gluten_free: true,
          is_dairy_free: true,
          allergens: [],
        },
        is_optional: true,
        substitutes: [],
      },
    ],
    steps: [
      {
        number: 1,
        description: 'Boil the spaghetti in salted water according to package instructions.',
        duration_minutes: 10,
      },
      {
        number: 2,
        description: 'Fry the pancetta until crispy.',
        duration_minutes: 5,
      },
      {
        number: 3,
        description: 'Beat the eggs and mix in the cheeses.',
      },
      {
        number: 4,
        description: 'Drain the pasta and combine with pancetta and egg mixture off the heat.',
      },
      {
        number: 5,
        description: 'Serve immediately with extra cheese and pepper.',
      },
    ],
    tags: [{ name: 'Italian' }, { name: 'Pasta' }, { name: 'Quick' }],
    meal_types: [MealType.LUNCH, MealType.DINNER],
    servings: 2,
    diet: DietType.REGULAR,
    prep_time_minutes: 10,
    cook_time_minutes: 15,
    total_time_minutes: 25,
    nutritional_info: {
      calories: 600,
      protein_g: 25,
      carbs_g: 75,
      fat_g: 20,
    },
    rating_count: 100,
    view_count: 150,
    favorite_count: 75,
    version: 1,
    average_rating: 4.5,
    instructions: [
      'Boil the spaghetti in salted water according to package instructions.',
      'Fry the pancetta until crispy.',
      'Beat the eggs and mix in the cheeses.',
      'Drain the pasta and combine with pancetta and egg mixture off the heat.',
      'Serve immediately with extra cheese and pepper.',
    ],
    image_url: 'assets/images/spaghetti_carbonara.jpg',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

export interface RecipeSummary {
  id: number;
  imageUrl: string;
  name: string;
  mealType: MealType;
  difficulty: DifficultyLevel;
  cuisine: CuisineType;
  averageRating: number;
  viewCount: number;
  favoriteCount: number;
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
  id: number;
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

export interface RecipeUpdated {
  id: number;
  name: string;
  version: number;
  message?: string; // default "Recipe updated successfully"
}

export interface RecipeDeleted {
  id: number;
  message?: string; // default "Recipe deleted successfully"
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

export interface RecipePage {
  recipes: RecipeSummary[];
  pagination: Pagination;
}
