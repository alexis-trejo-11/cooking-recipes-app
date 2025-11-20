import { Component, input } from '@angular/core';
import { Recipe } from '../../../../../../models/recipe_models';

@Component({
  selector: 'app-recipe-ingredients',
  imports: [],
  template: `<div class="recipe-card ingredients-card">
    <h2 class="section-title">Ingredients</h2>
    <ul class="ingredients-list">
      @for (ingredient of recipe().ingredients; track ingredient.id) {
      <li class="ingredient-item">
        <div class="ingredient-bullet"></div>
        <span class="ingredient-text">
          <span class="ingredient-quantity">{{ scaleIngredient(ingredient) }}</span>
          {{ ingredient.name }}
        </span>
      </li>
      }
    </ul>
  </div>`,
  styleUrl: './recipe-ingredients.scss',
})
export class RecipeIngredients {
  recipe = input.required<Recipe>();
  scaledServings = input(1);

  scaleIngredient(ingredient: any): string {
    const originalServings = this.recipe().servings || 1;
    const scaleFactor = this.scaledServings() / originalServings;

    if (ingredient.quantity && ingredient.quantity.value) {
      const scaledValue = parseFloat(ingredient.quantity.value) * scaleFactor;
      return `${scaledValue} ${ingredient.quantity.unit}`;
    }

    return ingredient.name;
  }
}
