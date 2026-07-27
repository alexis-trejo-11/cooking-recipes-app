import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RecipeService } from '../../../../services/recipe.service';
import { CreateRecipeRequest, UpdateRecipeRequest } from '../../../../models/recipe_models';

@Component({
  selector: 'app-edit-recipe',
  imports: [],
  templateUrl: './edit-recipe.html',
  styleUrl: './edit-recipe.scss',
})
export class EditRecipe {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recipeService = inject(RecipeService);

  recipeData = signal<CreateRecipeRequest | null>(null);
  loading = signal(true);
  submitting = signal(false);

  ngOnInit(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    if (recipeId) {
      this.loadRecipe(Number(recipeId));
    } else {
      this.router.navigate(['/recipes']);
    }
  }

  private loadRecipe(recipeId: number): void {
    this.recipeService.getRecipeById(recipeId.toString()).subscribe({
      next: (recipe) => {
        // Convert recipe to CreateRecipeRequest format
        const formData: CreateRecipeRequest = {
          name: recipe.name,
          description: recipe.description,
          difficulty: recipe.difficulty,
          cuisine: recipe.cuisine,
          ingredients: recipe.ingredients.map((ing) => ({
            name: ing.name,
            quantity: {
              value: ing.quantity.value.toString(),
              unit: ing.quantity.unit,
            },
            properties: {
              isVegan: ing.properties?.isVegan || false,
              isVegetarian: ing.properties?.isVegetarian || false,
              isGlutenFree: ing.properties?.isGlutenFree || false,
              isDairyFree: ing.properties?.isDairyFree || false,
              allergens: ing.properties?.allergens || [],
            },
            isOptional: ing.isOptional,
            substitutes: ing.substitutes,
          })),
          steps: recipe.steps.map((step) => ({
            description: step.description,
            durationMinutes: step.durationMinutes,
            technique: step.technique,
            temperature: step.temperature,
          })),
          tags: recipe.tags.map((tag) => ({
            name: tag.name,
            description: tag.description,
          })),
          mealTypes: recipe.mealTypes,
          imageUrl: recipe.imageUrl,
          servings: recipe.servings!,
          cookingTime: {
            prepMinutes: recipe.prepTimeMinutes || 0,
            cookMinutes: recipe.cookTimeMinutes || 0,
          },
          nutritionalInfo: recipe.nutritionalInfo
            ? {
                calories: recipe.nutritionalInfo.calories,
                proteinG: recipe.nutritionalInfo.proteinG?.toString(),
                carbsG: recipe.nutritionalInfo.carbsG?.toString(),
                fatG: recipe.nutritionalInfo.fatG?.toString(),
              }
            : null,
        };

        this.recipeData.set(formData);
        this.loading.set(false);
      },
      error: (error) => {
        console.error(' Error loading recipe:', error);
        this.loading.set(false);
        this.router.navigate(['/recipes']);
      },
    });
  }

  onFormSubmit(recipeData: CreateRecipeRequest | UpdateRecipeRequest): void {
    this.submitting.set(true);
    const recipeId = this.route.snapshot.paramMap.get('id')!;

    this.recipeService.updateRecipe(recipeId, recipeData as CreateRecipeRequest).subscribe({
      next: (updatedRecipe) => {
        console.log(' Recipe updated successfully:', updatedRecipe);
        this.submitting.set(false);
        this.router.navigate(['/recipes', updatedRecipe.id]);
      },
      error: (error) => {
        console.error('❌ Error updating recipe:', error);
        this.submitting.set(false);
        alert('Error updating recipe. Please try again.');
      },
    });
  }

  onFormCancel(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    this.router.navigate(['/recipes', recipeId]);
  }
}
