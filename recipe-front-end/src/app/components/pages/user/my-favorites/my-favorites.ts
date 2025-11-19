import { Component, inject, OnInit, signal } from '@angular/core';
import { RecipeGrid } from '../../../shared/recipe-grid/recipe-grid';
import {
  PaginationResponse,
  RecipeSummary,
  RecipeSummaryPage,
} from '../../../../models/recipe_models';
import { RecipeService } from '../../../../services/recipe.service';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-my-favorites',
  imports: [RecipeGrid],
  templateUrl: './my-favorites.html',
  styleUrl: './my-favorites.scss',
})
export class MyFavorites implements OnInit {
  loadingFavorites = signal(false);
  favoriteRecipes = signal<RecipeSummary[]>([]);
  favoritesPagination = signal<PaginationResponse | null>(null);
  private recipeService = inject(RecipeService);
  private authService = inject(AuthService);

  private currentPage = 1;
  private pageSize = 10;

  ngOnInit(): void {
    if (this.authService.currentUser()) {
      this.loadFavoriteRecipes(this.currentPage, this.pageSize);
    }
  }

  loadFavoriteRecipes(pageNumber: number, pageSize: number): void {
    this.loadingFavorites.set(true);
    this.recipeService.getUserFavoriteRecipes(pageNumber, pageSize).subscribe({
      next: (recipePage: RecipeSummaryPage) => {
        console.log('Recetas cargadas exitosamente:', recipePage);
        console.log('Número de recetas:', recipePage.recipes?.length);
        console.log('Información de paginación:', recipePage.pagination);

        this.favoriteRecipes.set(recipePage.recipes);
        this.favoritesPagination.set(recipePage.pagination);
        this.loadingFavorites.set(false);
        console.log(' LoadingFavorites establecido en:', false);
      },
      error: (error) => {
        console.error(' Error cargando recetas:', error);
        this.loadingFavorites.set(false);
        console.log(' LoadingFavorites establecido en:', false);
      },
    });
  }

  onFavoritesPageChanged(newPage: number): void {
    console.log('Cambiando a página de favoritos:', newPage);
    this.currentPage = newPage;
    this.loadFavoriteRecipes(this.currentPage, this.pageSize);
  }
}
