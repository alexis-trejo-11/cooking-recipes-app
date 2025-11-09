import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Recipes } from './pages/recipe/recipes/recipes';
import { RecipeCard } from './shared/recipe-card/recipe-card';
import { RecipeDetail } from './pages/recipe/recipe-detail/recipe-detail';

export const routes: Routes = [
  {
    path: '',
    component: Home,
  },
  {
    path: 'recipes',
    component: Recipes,
  },
  {
    path: 'recipe-card',
    component: RecipeCard,
  },
  {
    path: 'recipes/:id',
    component: RecipeDetail,
  },
];
