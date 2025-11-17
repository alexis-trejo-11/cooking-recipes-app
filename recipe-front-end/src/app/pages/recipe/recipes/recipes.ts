import {
  ChangeDetectorRef,
  Component,
  effect,
  inject,
  OnDestroy,
  OnInit,
  signal,
} from '@angular/core';
import { RecipeCard } from '../../../shared/recipe-card/recipe-card';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecipeSummaryPage } from '../../../models/recipe_models';
import { RecipeService } from '../../../services/recipe.service';

interface SearchFilters {
  query: string;
  cuisine: string;
  difficulty: string;
  maxPrepTime: undefined;
}

interface FilterOption {
  value: string;
  label: string;
}

interface FilterConfig {
  type: 'text' | 'select' | 'number';
  placeholder: string;
  options?: FilterOption[];
}

@Component({
  selector: 'app-recipes',
  imports: [CommonModule, FormsModule, RecipeCard],
  templateUrl: './recipes.html',
  styleUrl: './recipes.scss',
})
export class Recipes implements OnInit {
  private recipeService = inject(RecipeService);
  private cdr = inject(ChangeDetectorRef);

  loading = signal(true);

  page = signal<RecipeSummaryPage>({
    recipes: [],
    pagination: { total_items: 0, total_pages: 0, current_page: 0, page_size: 0 },
  });
  filters: SearchFilters = {
    query: '',
    difficulty: '',
    cuisine: '',
    maxPrepTime: undefined,
  };

  filterConfigs: { [key: string]: FilterConfig } = {
    query: {
      type: 'text',
      placeholder: 'Search recipes...',
    },
    difficulty: {
      type: 'select',
      options: [
        { value: 'easy', label: 'Easy' },
        { value: 'medium', label: 'Medium' },
        { value: 'hard', label: 'Hard' },
      ],
      placeholder: 'Select Difficulty',
    },
    cuisine: {
      type: 'select',
      options: [
        { value: '', label: 'All Cuisines' },
        { value: 'Italian', label: 'Italian' },
        { value: 'Mexican', label: 'Mexican' },
        { value: 'Asian', label: 'Asian' },
        { value: 'American', label: 'American' },
        { value: 'Mediterranean', label: 'Mediterranean' },
      ],
      placeholder: 'Select Cuisine',
    },
    maxPrepTime: {
      type: 'number',
      placeholder: 'Max Preparation Time (mins)',
    },
  };

  constructor() {
    console.log('🔴 Recipes Constructor');
    this.cdr.markForCheck(); // ← Fuerza detección de cambios
  }

  ngOnInit() {
    console.log('Init Recipes');
    this.loadRecipes();
  }

  get filterKeys(): (keyof SearchFilters)[] {
    return Object.keys(this.filterConfigs) as (keyof SearchFilters)[];
  }

  clearFilters(): void {
    this.filters = {
      query: '',
      difficulty: '',
      cuisine: '',
      maxPrepTime: undefined,
    };
  }

  applyFilters(): void {
    // TODO
  }

  loadRecipes(): void {
    this.loading.set(true);
    console.log('Loading recipes...');
    this.recipeService.getAllRecipes().subscribe({
      next: (recipes) => {
        this.page.set(recipes);
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('Error loading recipes:', err);
        this.loading.set(false);
      },
    });
  }

  hasActiveFilters(): boolean {
    return (
      this.filters.query !== '' ||
      this.filters.cuisine !== '' ||
      this.filters.difficulty !== '' ||
      this.filters.maxPrepTime !== undefined
    );
  }
}
