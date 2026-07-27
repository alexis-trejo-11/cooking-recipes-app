import { Component, inject, OnInit, signal } from '@angular/core';
import { RecipeService } from '../../../../services/recipe.service';
import {
  PaginationResponse,
  RecipeSummary,
  RecipeSummaryPage,
} from '../../../../models/recipe_models';
import { AuthService } from '../../../../services/auth.service';
import { RecipeGrid } from '../../../shared/recipe-grid/recipe-grid';
import { Router } from '@angular/router';

@Component({
  selector: 'app-my-recipes',
  imports: [RecipeGrid],
  templateUrl: './my-recipes.html',
  styleUrl: './my-recipes.scss',
})
export class MyRecipes implements OnInit {
  private recipeService = inject(RecipeService);
  private authService = inject(AuthService);
  private router = inject(Router);

  loadingRecipes = signal(true);
  userRecipes = signal<RecipeSummary[]>([]);
  pagination = signal<PaginationResponse | null>(null);

  currentPage = 1;
  pageSize = 9;

  ngOnInit(): void {
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.loadUserRecipes(currentUser.id, this.currentPage, this.pageSize);
    }
  }

  loadUserRecipes(userId: string, page: number, pageSize: number): void {
    this.recipeService.getRecipesByAuthor().subscribe({
      next: (recipePage: RecipeSummaryPage) => {
        console.log('Recetas cargadas exitosamente:', recipePage);
        console.log('Número de recetas:', recipePage.recipes?.length);
        console.log('Información de paginación:', recipePage.pagination);

        this.userRecipes.set(recipePage.recipes);
        this.pagination.set(recipePage.pagination);
        this.loadingRecipes.set(false);
        console.log(' LoadingRecipes establecido en:', false);
      },
      error: (error) => {
        console.error(' Error cargando recetas:', error);
        this.loadingRecipes.set(false);
        console.log(' LoadingRecipes establecido en:', false);
      },
    });
  }

  onPageChanged(newPage: number): void {
    console.log('Cambiando a página:', newPage);
    this.currentPage = newPage;
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.loadUserRecipes(currentUser.id, newPage, this.pageSize);
    }
  }

  onCreateRecipe(): void {
    console.log('Profile: Navegando a crear receta');
    this.router.navigate(['/create']);
  }
}
