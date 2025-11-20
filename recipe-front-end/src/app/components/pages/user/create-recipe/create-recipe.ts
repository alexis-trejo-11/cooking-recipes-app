import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { RecipeService } from '../../../../services/recipe.service';
import { RecipeForm } from '../../../shared/recipe-form/recipe-form';
import { CreateRecipeRequest, UpdateRecipeRequest } from '../../../../models/recipe_models';

@Component({
  selector: 'app-create-recipe',
  standalone: true,
  imports: [RecipeForm],
  template: `
    <app-recipe-form
      mode="create"
      [loading]="submitting"
      (formSubmit)="onFormSubmit($event)"
      (formCancel)="onFormCancel()"
    />
  `,
})
export class CreateRecipe {
  private recipeService = inject(RecipeService);
  router = inject(Router);

  submitting = false;

  onFormSubmit(recipeData: CreateRecipeRequest | UpdateRecipeRequest) {
    this.submitting = true;

    this.recipeService.createRecipe(recipeData as CreateRecipeRequest).subscribe({
      next: (createdRecipeId) => {
        console.log('Recipe Created With ID:', createdRecipeId);
        this.submitting = false;
        this.router.navigate(['/recipes', createdRecipeId]);
      },
      error: (error) => {
        console.error('Error creating recipe:', error);
        this.submitting = false;
        alert('There was an error creating the recipe. Please try again.');
      },
    });
  }

  onFormCancel(): void {
    this.router.navigate(['/recipes']);
  }
}
