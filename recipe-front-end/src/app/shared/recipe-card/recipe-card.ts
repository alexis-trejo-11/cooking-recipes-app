import { Component, input, signal } from '@angular/core';
import { DifficultyLevel, RecipeSummary, CuisineType, MealType } from '../../models/recipe_models';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-recipe-card',
  imports: [CommonModule, RouterModule],
  templateUrl: './recipe-card.html',
  styleUrl: './recipe-card.scss',
})
export class RecipeCard {
  recipe = input.required<RecipeSummary>();

  getDifficultyClass(difficulty: DifficultyLevel): string {
    const classes = {
      [DifficultyLevel.EASY]: 'difficulty-easy',
      [DifficultyLevel.MEDIUM]: 'difficulty-medium',
      [DifficultyLevel.HARD]: 'difficulty-hard',
    };
    return classes[difficulty] || 'difficulty-easy';
  }

  getDifficultyText(difficulty: DifficultyLevel): string {
    const texts = {
      [DifficultyLevel.EASY]: 'Easy',
      [DifficultyLevel.MEDIUM]: 'Medium',
      [DifficultyLevel.HARD]: 'Hard',
    };
    return texts[difficulty] || 'Easy';
  }

  getCuisineText(cuisine: CuisineType): string {
    const texts = {
      [CuisineType.ITALIAN]: 'Italian',
      [CuisineType.MEXICAN]: 'Mexican',
      [CuisineType.ASIAN]: 'Asian',
      [CuisineType.AMERICAN]: 'American',
      [CuisineType.MEDITERRANEAN]: 'Mediterranean',
      [CuisineType.CHINESE]: 'Chinese',
      [CuisineType.INDIAN]: 'Indian',
      [CuisineType.FRENCH]: 'French',
      [CuisineType.JAPANESE]: 'Japanese',
      [CuisineType.THAI]: 'Thai',
      [CuisineType.SPANISH]: 'Spanish',
      [CuisineType.GREEK]: 'Greek',
      [CuisineType.FUSION]: 'Fusion',
      [CuisineType.UNKNOWN]: 'Unknown',
      [CuisineType.OTHER]: 'Other',
    };
    return texts[cuisine] || 'Other';
  }

  getMealTypeText(mealType: MealType): string {
    const texts = {
      [MealType.BREAKFAST]: 'Breakfast',
      [MealType.LUNCH]: 'Lunch',
      [MealType.DINNER]: 'Dinner',
      [MealType.SNACK]: 'Snack',
      [MealType.DESSERT]: 'Dessert',
    };
    return texts[mealType] || 'Meal';
  }

  formatNumber(count: number): string {
    if (count >= 1000) {
      return (count / 1000).toFixed(1) + 'k';
    }
    return count.toString();
  }
}
