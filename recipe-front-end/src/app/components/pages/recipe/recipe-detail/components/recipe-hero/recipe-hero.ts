import { Component, input } from '@angular/core';
import { Recipe } from '../../../../../../models/recipe_models';

@Component({
  selector: 'app-recipe-hero',
  imports: [],
  template: `<section class="recipe-hero">
  <img
    [src]="recipe().imageUrl || '/images/dummy-plate.jpg'"
    [alt]="recipe().name"
    class="hero-image"
  />
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="recipe-badges">
      <span class="recipe-badge {{ getDifficultyClass(recipe().difficulty) }}">
        {{ recipe().difficulty }}
      </span>
      @if (recipe().cuisine) {
        <span class="recipe-badge cuisine-badge">
          {{ recipe().cuisine }}
        </span>
      }
    </div>

    <h1 class="recipe-title">{{ recipe().name }}</h1>
    <p class="recipe-description">{{ recipe().description }}</p>
  </div>
</section>`,
  styleUrl: './recipe-hero.scss',
})
export class RecipeHero {
  recipe = input.required<Recipe>();

  getDifficultyClass(difficulty: string): string {
    return `difficulty-${difficulty.toLowerCase()}`;
  }
}
