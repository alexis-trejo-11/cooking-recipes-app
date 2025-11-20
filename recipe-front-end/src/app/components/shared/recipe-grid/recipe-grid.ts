import { Component, input, output } from '@angular/core';
import { PaginationResponse, RecipeSummary } from '../../../models/recipe_models';
import { RecipeCard } from '../recipe-card/recipe-card';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-recipe-grid',
  imports: [RecipeCard, RouterLink],
  templateUrl: './recipe-grid.html',
  styleUrl: './recipe-grid.scss',
})
export class RecipeGrid {
  // Inputs
  title = input.required<string>();
  recipes = input<RecipeSummary[]>([]);
  pagination = input<PaginationResponse | null>(null);
  loading = input(false);
  showCreateButton = input(false);
  emptyMessage = input('No recipes found');
  createButtonText = input('Create Recipe');
  createButtonLink = input('/create');

  // Outputs (Events)
  pageChanged = output<number>();
  createRecipe = output<void>();

  onNextPage(): void {
    const pagination = this.pagination();
    if (pagination?.nextPage) {
      console.log(`➡️ RecipeGrid: Navegando a página ${pagination.nextPage}`);
      this.pageChanged.emit(pagination.nextPage);
    }
  }

  onPreviousPage(): void {
    const pagination = this.pagination();
    if (pagination?.previousPage) {
      console.log(` RecipeGrid: Navegando a página ${pagination.previousPage}`);
      this.pageChanged.emit(pagination.previousPage);
    }
  }

  onCreateRecipe(): void {
    console.log('RecipeGrid: Crear nueva receta');
    this.createRecipe.emit();
  }

  shouldShowPagination(): boolean {
    const pagination = this.pagination();
    return !!pagination && pagination.totalPages > 1;
  }

  shouldShowEmptyState(): boolean {
    return !this.loading() && this.recipes().length === 0;
  }
}
