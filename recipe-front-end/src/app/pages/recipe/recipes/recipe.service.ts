import { inject, Injectable } from '@angular/core';
import {
  CuisineType,
  DifficultyLevel,
  MealType,
  Recipe,
  getDummyDetailedRecipe,
  RecipeSummary,
} from '../../../models/recipe_models';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class RecipeService {
  //private http = inject(HttpClient);
  //private apiUrl = 'https://localhost:8080/api/v1/recipes';
  dummy_data: RecipeSummary[] = [
    {
      id: 1,
      name: 'Spaghetti Carbonara',
      cuisine: CuisineType.ITALIAN,
      difficulty: DifficultyLevel.MEDIUM,
      imageUrl: 'assets/images/spaghetti_carbonara.jpg',
      mealType: MealType.DINNER,
      averageRating: 4.5,
      viewCount: 150,
      favoriteCount: 75,
    },
  ];

  getAllRecipes(): Observable<RecipeSummary[]> {
    // TODO
    return of(this.dummy_data);
  }

  getRecipeById(id: string): Observable<Recipe> {
    // TODO
    //return this.http.get<RecipeSummary>(`${this.apiUrl}/${id}`);
    return of(getDummyDetailedRecipe());
  }
}
