// src/app/pages/recipe-detail/recipe-detail.component.ts
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RecipeService } from '../../../services/recipe.service';
import { Ingredient, Recipe } from '../../../models/recipe_models';

interface RecipeStat {
  icon: string;
  label: string;
  value: string | number;
  bgColor: string;
  iconColor: string;
}

@Component({
  selector: 'app-recipe-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './recipe-detail.html',
  styleUrls: ['./recipe-detail.scss'],
})
export class RecipeDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recipeService = inject(RecipeService);

  recipe = signal<Recipe | null>(null);
  loading = signal(true);
  scaledServings = signal(1);
  userRating = signal(0);

  recipeStats = computed<RecipeStat[]>(() => {
    const recipe = this.recipe();
    if (!recipe) return [];

    return [
      {
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
        label: 'Prep Time',
        value: `${recipe.prep_time_minutes} min`,
        bgColor: 'orange',
        iconColor: 'orange',
      },
      {
        icon: 'M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z',
        label: 'Cook Time',
        value: `${recipe.cook_time_minutes} min`,
        bgColor: 'red',
        iconColor: 'red',
      },
      {
        icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
        label: 'Servings',
        value: this.scaledServings(),
        bgColor: 'blue',
        iconColor: 'blue',
      },
    ];
  });

  stars = [1, 2, 3, 4, 5];

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadRecipe(id);
    }
  }

  loadRecipe(id: string): void {
    this.recipeService.getRecipeById(id).subscribe({
      next: (recipe) => {
        this.recipe.set(recipe);
        this.scaledServings.set(recipe.servings || 1);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.router.navigate(['/recipes']);
      },
    });
  }

  increaseServings(): void {
    const current = this.scaledServings();
    this.scaledServings.set(current + 1);
  }

  decreaseServings(): void {
    const current = this.scaledServings();
    if (current > 1) {
      this.scaledServings.set(current - 1);
    }
  }

  scaleIngredient(ingredient: Ingredient): string {
    const recipe = this.recipe();
    if (!recipe) return ingredient.quantity.toString();

    const scaleFactor = this.scaledServings() / recipe.servings!;
    const scaled = ingredient.quantity.value * scaleFactor;
    return scaled % 1 === 0 ? scaled.toString() : scaled.toFixed(2);
  }

  rateRecipe(rating: number): void {}

  getDifficultyClass(difficulty: string): string {
    const classes = {
      Easy: 'difficulty-easy',
      Medium: 'difficulty-medium',
      Hard: 'difficulty-hard',
    };
    return classes[difficulty as keyof typeof classes] || 'difficulty-easy';
  }
}
