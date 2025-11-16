import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Recipes } from './pages/recipe/recipes/recipes';
import { RecipeDetail } from './pages/recipe/recipe-detail/recipe-detail';
import { Login } from './pages/auth/login/login';
import { Singup } from './pages/auth/singup/singup';
import { About } from './shared/about/about';
import { DashboardLayout } from './pages/users/dashboard/layout/dashboard-layout';
import { Profile } from './pages/users/profile/profile';

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
  },
  {
    path: 'signup',
    component: Singup,
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
    path: 'user-dashboard',
    component: DashboardLayout,
  },
  {
    path: 'profile',
    component: Profile,
  },
];
