import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RecipeCard } from '../../shared/recipe-card/recipe-card';
import { RecipeService } from '../../../services/recipe.service';
import { RecipeSummary } from '../../../models/recipe_models';

interface FeatureCard {
  icon: string;
  title: string;
  description: string;
  iconClass: string;
}

@Component({
  selector: 'app-home',
  imports: [RouterLink, RecipeCard],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home implements OnInit {
  private recipeService = inject(RecipeService);

  loadingFeatured = signal(true);
  featuredRecipes = signal<RecipeSummary[]>([]);

  featureCards: FeatureCard[] = [
    {
      icon: 'search',
      title: 'Search & Discover',
      description: 'Find recipes by ingredients, cuisine, or dietary preferences',
      iconClass: 'search-icon',
    },
    {
      icon: 'create',
      title: 'Create & Share',
      description: 'Share your favorite recipes with the community',
      iconClass: 'create-icon',
    },
    {
      icon: 'favorite',
      title: 'Save Favorites',
      description: 'Keep track of your favorite recipes and cooking tips',
      iconClass: 'favorite-icon',
    },
  ];

  getIconPath(icon: string): string {
    const icons = {
      search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
      create: 'M12 6v6m0 0v6m0-6h6m-6 0H6',
      favorite:
        'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
    };
    return icons[icon as keyof typeof icons] || icons.search;
  }

  loadFeaturedRecipes(): void {
    this.recipeService.getFeaturedRecipes().subscribe({
      next: (recipes) => {
        this.featuredRecipes.set(recipes);
        this.loadingFeatured.set(false);
      },
      error: (error) => {
        console.error('Error fetching featured recipes:', error);
        this.loadingFeatured.set(false);
      },
    });
  }

  ngOnInit(): void {
    this.loadFeaturedRecipes();
  }
}
