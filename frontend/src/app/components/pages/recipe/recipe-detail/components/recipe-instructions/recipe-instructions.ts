import { Component, input } from '@angular/core';
import { Recipe } from '../../../../../../models/recipe_models';

@Component({
  selector: 'app-recipe-instructions',
  imports: [],
  template: `<div class="recipe-card instructions-card">
    <h2 class="section-title">Instructions</h2>
    <div class="instructions-list">
      @for (step of recipe().steps; track step.number; let i = $index) {
      <div class="instruction-step">
        <div class="step-number">
          {{ i + 1 }}
        </div>
        <div class="step-content">
          <p class="step-text">{{ step.description }}</p>
          @if (step.durationMinutes) {
          <p class="step-duration">⏱️ {{ step.durationMinutes }} minutes</p>
          }
        </div>
      </div>
      }
    </div>
  </div>`,
  styleUrl: './recipe-instructions.scss',
})
export class RecipeInstructions {
  recipe = input.required<Recipe>();
}
