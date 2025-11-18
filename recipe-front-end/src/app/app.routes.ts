import { Routes } from '@angular/router';
import { Home } from './components/pages/home/home';
import { Recipes } from './components/pages/recipe/recipes/recipes';
import { RecipeDetail } from './components/pages/recipe/recipe-detail/recipe-detail';
import { Login } from './components/pages/auth/login/login';
import { Singup } from './components/pages/auth/singup/singup';
import { About } from './components/shared/about/about';
import { authGuard } from './guards/auth.guard';
import { publicGuard } from './guards/public.guard';
import { CreateRecipe } from './components/pages/recipe/create-recipe/create-recipe';
import { DashboardLayout } from './components/pages/user/dashboard/layout/dashboard-layout';
import { Overview } from './components/pages/user/dashboard/overview/overview';
import { Profile } from './components/pages/user/profile/profile';
import { EditRecipe } from './components/pages/user/edit-recipe/edit-recipe';
import { MyRecipes } from './components/pages/user/my-recipes/my-recipes';
import { MyFavorites } from './components/pages/user/my-favorites/my-favorites';

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
    path: 'login',
    component: Login,
    canActivate: [publicGuard],
  },
  {
    path: 'signup',
    component: Singup,
    canActivate: [publicGuard],
  },
  {
    path: 'recipes/:id',
    component: RecipeDetail,
  },
  {
    path: 'about',
    component: About,
  },
  {
    path: 'dashboard',
    component: DashboardLayout,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        redirectTo: 'overview',
        pathMatch: 'full',
      },
      {
        path: 'overview',
        component: Overview,
      },
      {
        path: 'create',
        component: CreateRecipe,
      },
      {
        path: 'edit/:id',
        component: EditRecipe,
      },
      {
        path: 'my-recipes',
        component: MyRecipes,
      },
      {
        path: 'favorites',
        component: MyFavorites,
      },
      {
        path: 'profile',
        component: Profile,
      },
    ],
  },
];
