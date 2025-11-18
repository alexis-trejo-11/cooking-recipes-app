import { Component, inject, OnInit, signal } from '@angular/core';
import { AuthService } from '../../../../../services/auth.service';
import { RecipeService } from '../../../../../services/recipe.service';
import { Recipe } from '../../../../../models/recipe_models';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-overview',
  imports: [CommonModule, RouterModule],
  templateUrl: './overview.html',
  styleUrl: './overview.scss',
})
export class Overview implements OnInit {
  private recipeService = inject(RecipeService);
  authService = inject(AuthService);

  recentRecipes = signal<Recipe[]>([]);
  loading = signal(true);
  stats = signal({
    totalRecipes: 0,
    totalFavorites: 0,
    averageRating: 0,
    totalViews: 0,
  });

  ngOnInit(): void {
    this.loadRecentRecipes();
    this.loadStats();
  }

  loadRecentRecipes(): void {}

  loadStats(): void {
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.recipeService.getRecipesByAuthor().subscribe({
        next: (page) => {
          const totalRating = page.recipes.reduce((sum, r) => sum + (r.average_rating || 0), 0);
          this.stats.set({
            totalRecipes: page.recipes.length,
            totalFavorites: page.recipes.filter((r) => r).length,
            averageRating: page.recipes.length > 0 ? totalRating / page.recipes.length : 0,
            totalViews: Math.floor(Math.random() * 1000),
          });
        },
      });
    }
  }

  deleteRecipe(event: Event, recipeId: string): void {
    event.preventDefault();
    event.stopPropagation();
  }
}
