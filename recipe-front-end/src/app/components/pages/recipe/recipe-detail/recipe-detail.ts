import { Component, OnInit, inject, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RecipeService } from '../../../../services/recipe.service';
import { Ingredient, Recipe } from '../../../../models/recipe_models';
import { AuthService } from '../../../../services/auth.service';
import { RecipeHero } from './components/recipe-hero/recipe-hero';
import { RecipeStats } from './components/recipe-stats/recipe-stats';
import { RecipeIngredients } from './components/recipe-ingredients/recipe-ingredients';
import { RecipeInstructions } from './components/recipe-instructions/recipe-instructions';
import { RecipeSidebar } from './components/recipe-sidebar/recipe-sidebar';

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
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RecipeHero,
    RecipeStats,
    RecipeIngredients,
    RecipeSidebar,
    RecipeInstructions,
  ],
  templateUrl: './recipe-detail.html',
  styleUrls: ['./recipe-detail.scss'],
})
export class RecipeDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private recipeService = inject(RecipeService);
  private authService = inject(AuthService);

  recipe = signal<Recipe | null>(null);
  loading = signal(true);
  scaledServings = signal(1);
  isFavorite = signal(false);

  ngOnInit(): void {
    this.loadRecipe();
  }

  get isUserLoggedIn(): boolean {
    return this.authService.isAuthenticated();
  }

  get isUserRecipeAuthor(): boolean {
    const currentUser = this.authService.currentUser();
    const recipe = this.recipe();
    return !!currentUser && !!recipe && currentUser.id === recipe.authorId;
  }

  private loadRecipe(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    if (!recipeId) {
      this.loading.set(false);
      return;
    }

    this.recipeService.getRecipeById(recipeId).subscribe({
      next: (recipe) => {
        this.recipe.set(recipe);
        this.scaledServings.set(recipe.servings || 1);
        this.checkIfFavorite(recipeId);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  private checkIfFavorite(recipeId: string): void {
    if (this.isUserLoggedIn) {
      this.recipeService.isFavorite(recipeId).subscribe({
        next: (isFav) => this.isFavorite.set(isFav),
        error: () => this.isFavorite.set(false),
      });
    }
  }

  // Event handlers
  onServingsChanged(newServings: number): void {
    this.scaledServings.set(newServings);
  }

  onToggleFavorite(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    if (!recipeId) return;

    if (this.isFavorite()) {
      this.recipeService.toggleFavorite(recipeId).subscribe({
        next: () => this.isFavorite.set(false),
      });
    } else {
      this.recipeService.toggleFavorite(recipeId).subscribe({
        next: () => this.isFavorite.set(true),
      });
    }
  }

  onOpenReview(): void {
    // Implementar modal de review
    console.log('Abrir modal de review');
  }

  onEditRecipe(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    if (recipeId) {
      this.router.navigate(['/recipes', recipeId, 'edit']);
    }
  }

  onDeleteRecipe(): void {
    const recipeId = this.route.snapshot.paramMap.get('id');
    if (!recipeId) return;

    if (confirm('Are you sure you want to delete this recipe?')) {
      this.recipeService.deleteRecipe(recipeId).subscribe({
        next: () => {
          this.router.navigate(['/my-recipes']);
        },
      });
    }
  }
}
