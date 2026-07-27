import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { getApiUrl } from '../../enviorments/runtime-config';
import { Observable } from 'rxjs';
import { CreateReviewRequest, Review, UpdateReviewRequest } from '../models/review_models';

@Injectable({
  providedIn: 'root',
})
export class ReviewService {
  private http = inject(HttpClient);
  private get apiUrl() {
    return getApiUrl();
  }

  getRecipeReviews(recipeId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/recipes/${recipeId}/reviews`);
  }

  getUserReview(recipeId: string): Observable<Review | null> {
    return this.http.get<Review | null>(`${this.apiUrl}/users/recipes/${recipeId}/reviews`);
  }

  createReview(review: CreateReviewRequest): Observable<Review> {
    return this.http.post<Review>(`${this.apiUrl}/recipes/reviews`, review);
  }

  updateReview(reviewId: string, review: UpdateReviewRequest): Observable<Review> {
    return this.http.put<Review>(`${this.apiUrl}/recipes/reviews/${reviewId}`, review);
  }

  deleteReview(reviewId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/recipes/reviews/${reviewId}`);
  }
}
