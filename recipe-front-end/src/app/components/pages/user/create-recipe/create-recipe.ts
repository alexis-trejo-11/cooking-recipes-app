import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RecipeService } from '../../../../services/recipe.service';
import { AuthService } from '../../../../services/auth.service';
import { Ingredient, Step } from '../../../../models/recipe_models';

@Component({
  selector: 'app-create-recipe',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-recipe.html',
  styleUrls: ['./create-recipe.scss'],
})
export class CreateRecipe {
  private recipeService = inject(RecipeService);
  private authService = inject(AuthService);
  router = inject(Router);

  recipeData: any = {
    title: '',
    description: '',
    prepTime: 0,
    cookTime: 0,
    servings: 1,
    difficulty: 'Easy',
    cuisine: '',
    imageUrl: '',
    ingredients: [],
    steps: [],
  };
}
