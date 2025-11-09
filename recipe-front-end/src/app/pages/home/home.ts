import { Component, signal } from '@angular/core';
import { RecipeCard } from '../../shared/recipe-card/recipe-card';

interface FeatureCard {
  icon: string;
  title: string;
  description: string;
  iconClass: string;
}

@Component({
  selector: 'app-home',
  imports: [RecipeCard],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  loadingTopRated = signal(true);
  loadingQuick = signal(false);
  topRatedRecipes = signal<any[]>([]);
  quickRecipes = signal<any[]>([]);

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
}
