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
    if (pagination?.next_page) {
      console.log(`➡️ RecipeGrid: Navegando a página ${pagination.next_page}`);
      this.pageChanged.emit(pagination.next_page);
    }
  }

  onPreviousPage(): void {
    const pagination = this.pagination();
    if (pagination?.previous_page) {
      console.log(`⬅️ RecipeGrid: Navegando a página ${pagination.previous_page}`);
      this.pageChanged.emit(pagination.previous_page);
    }
  }

  onCreateRecipe(): void {
    console.log('RecipeGrid: Crear nueva receta');
    this.createRecipe.emit();
  }

  shouldShowPagination(): boolean {
    const pagination = this.pagination();
    return !!pagination && pagination.total_pages > 1;
  }

  shouldShowEmptyState(): boolean {
    return !this.loading() && this.recipes().length === 0;
  }
}
