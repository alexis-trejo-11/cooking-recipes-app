import { inject, Injectable } from '@angular/core';
import { Recipe, RecipeSummary, RecipeSummaryPage } from '../models/recipe_models';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { environment } from '../../enviorments/enviroment';

@Injectable({
  providedIn: 'root',
})
export class RecipeService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl + '/recipes';

  getAllRecipes(): Observable<RecipeSummaryPage> {
    return this.http.get<RecipeSummaryPage>(this.apiUrl);
  }

  getRecipesById(id: number): Observable<Recipe> {
    return this.http.get<Recipe>(`${this.apiUrl}/${id}`);
  }

  getRecipesByAuthor(): Observable<RecipeSummaryPage> {
    const token = this.getAccessToken();
    if (!token) {
      console.error('No hay token disponible para obtener el usuario');
      return throwError(() => new Error('No authentication token available'));
    }

    console.log('Token disponible:', token.substring(0, 20) + '...');
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    return this.http.get<RecipeSummaryPage>(`${this.apiUrl}/user/`, { headers });
  }

  getUserFavoriteRecipes(pageNumber: number, pageSize: number): Observable<RecipeSummaryPage> {
    const token = this.getAccessToken();
    if (!token) {
      console.error('No hay token disponible para obtener el usuario');
      return throwError(() => new Error('No authentication token available'));
    }

    console.log('Token disponible:', token.substring(0, 5) + '...');
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    return this.http.get<RecipeSummaryPage>(`${this.apiUrl}/favorites/`, { headers });
  }

  getFeaturedRecipes(): Observable<RecipeSummary[]> {
    return this.http.get<RecipeSummary[]>(`${this.apiUrl}/featured`);
  }

  deleteRecipe(): Observable<void> {
    return of();
  }

  addAuthHeader(headers: { [key: string]: string } = {}): { [key: string]: string } {
    const token = this.getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  private tokenKey = 'auth_token';

  public getAccessToken(): string | null {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    return localStorage.getItem(this.tokenKey);
  }
}
