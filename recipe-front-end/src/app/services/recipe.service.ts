import { inject, Injectable } from '@angular/core';
import { Recipe, RecipeSummaryPage } from '../models/recipe_models';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
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

  getRecipesByAuthor(authorId: string): Observable<Recipe> {
    return this.http.get<Recipe>(`${this.apiUrl}/author/${authorId}`);
  }
}
