import { Component, input, output, signal } from '@angular/core';
import {
  CreateIngredientRequest,
  CreateRecipeRequest,
  CreateStepRequest,
  CuisineType,
  DifficultyLevel,
  MealType,
  TagRequest,
  UpdateRecipeRequest,
} from '../../../models/recipe_models';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-recipe-form',
  imports: [FormsModule, CommonModule],
  templateUrl: './recipe-form.html',
  styleUrl: './recipe-form.scss',
})
export class RecipeForm {
  // Inputs
  mode = input<'create' | 'edit'>('create');
  initialData = input<CreateRecipeRequest | null>(null);
  loading = input(false);

  // Outputs
  formSubmit = output<CreateRecipeRequest | UpdateRecipeRequest>();
  formCancel = output<void>();

  // Internal state
  recipeData: CreateRecipeRequest = this.getDefaultRecipeData();
  ingredients = signal<CreateIngredientRequest[]>([]);
  steps = signal<CreateStepRequest[]>([]);
  tags = signal<TagRequest[]>([]);
  mealTypes = signal<MealType[]>([]);

  // Available options
  difficultyLevels: DifficultyLevel[] = [
    DifficultyLevel.EASY,
    DifficultyLevel.MEDIUM,
    DifficultyLevel.HARD,
  ];
  cuisineTypes: CuisineType[] = [
    CuisineType.AMERICAN,
    CuisineType.ITALIAN,
    CuisineType.MEXICAN,
    CuisineType.CHINESE,
    CuisineType.INDIAN,
    CuisineType.FRENCH,
    CuisineType.JAPANESE,
    CuisineType.MEDITERRANEAN,
    CuisineType.THAI,
    CuisineType.SPANISH,
    CuisineType.GREEK,
    CuisineType.FUSION,
    CuisineType.ASIAN,
    CuisineType.OTHER,
    CuisineType.UNKNOWN,
  ];
  availableMealTypes: MealType[] = [
    MealType.BREAKFAST,
    MealType.LUNCH,
    MealType.DINNER,
    MealType.DESSERT,
    MealType.SNACK,
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {
    const initialData = this.initialData();
    if (initialData && this.mode() === 'edit') {
      this.loadInitialData(initialData);
    } else {
      // Add empty ingredient and step for create mode
      this.addIngredient();
      this.addStep();
    }
  }

  private getDefaultRecipeData(): CreateRecipeRequest {
    return {
      name: '',
      description: null,
      difficulty: DifficultyLevel.EASY,
      cuisine: CuisineType.AMERICAN,
      ingredients: [],
      steps: [],
      tags: [],
      mealTypes: [],
      imageUrl: null,
      servings: 4,
      cookingTime: {
        prepMinutes: 0,
        cookMinutes: 0,
      },
      nutritionalInfo: null,
    };
  }

  private loadInitialData(data: CreateRecipeRequest): void {
    this.recipeData = { ...data };
    this.ingredients.set([...data.ingredients]);
    this.steps.set([...data.steps]);
    this.tags.set([...data.tags]);
    this.mealTypes.set([...data.mealTypes]);
  }

  // Ingredients Management
  addIngredient(): void {
    this.ingredients.update((ingredients) => [
      ...ingredients,
      {
        name: '',
        quantity: { value: '0', unit: '' },
        properties: {
          isVegan: false,
          isVegetarian: false,
          isGlutenFree: false,
          isDairyFree: false,
          allergens: [],
        },
        isOptional: false,
        substitutes: [],
      },
    ]);
  }

  removeIngredient(index: number): void {
    this.ingredients.update((ingredients) => ingredients.filter((_, i) => i !== index));
  }

  updateIngredientProperty(
    index: number,
    property: keyof CreateIngredientRequest,
    value: any
  ): void {
    this.ingredients.update((ingredients) =>
      ingredients.map((ing, i) => (i === index ? { ...ing, [property]: value } : ing))
    );
  }

  // Steps Management
  addStep(): void {
    this.steps.update((steps) => [
      ...steps,
      {
        description: '',
        durationMinutes: null,
        technique: null,
        temperature: null,
      },
    ]);
  }

  removeStep(index: number): void {
    this.steps.update((steps) => steps.filter((_, i) => i !== index));
  }

  // Tags Management
  addTag(): void {
    this.tags.update((tags) => [...tags, { name: '', description: null }]);
  }

  removeTag(index: number): void {
    this.tags.update((tags) => tags.filter((_, i) => i !== index));
  }

  // Meal Types Management
  toggleMealType(mealType: MealType): void {
    this.mealTypes.update((types) =>
      types.includes(mealType) ? types.filter((t) => t !== mealType) : [...types, mealType]
    );
  }

  // Form Submission
  submitRecipe(): void {
    if (this.loading()) return;

    // Prepare final data
    const finalData: CreateRecipeRequest = {
      ...this.recipeData,
      ingredients: this.ingredients().filter((ing) => ing.name.trim() !== ''),
      steps: this.steps().filter((step) => step.description.trim() !== ''),
      tags: this.tags().filter((tag) => tag.name.trim() !== ''),
      mealTypes: this.mealTypes(),
      cookingTime: {
        prepMinutes: this.recipeData.cookingTime.prepMinutes || 0,
        cookMinutes: this.recipeData.cookingTime.cookMinutes || 0,
      },
    };

    console.log(`📤 ${this.mode() === 'create' ? 'Creating' : 'Updating'} recipe:`, finalData);
    this.formSubmit.emit(finalData);
  }

  cancel(): void {
    this.formCancel.emit();
  }

  // Helper methods
  get submitButtonText(): string {
    return this.loading()
      ? `${this.mode() === 'create' ? 'Creating' : 'Updating'}...`
      : `${this.mode() === 'create' ? 'Create' : 'Update'} Recipe`;
  }

  get title(): string {
    return this.mode() === 'create' ? 'Create New Recipe' : 'Edit Recipe';
  }

  get isEditMode(): boolean {
    return this.mode() === 'edit';
  }
}
