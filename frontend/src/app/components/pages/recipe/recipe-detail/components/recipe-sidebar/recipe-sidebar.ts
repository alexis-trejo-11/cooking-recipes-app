import { Component, computed, input, output } from '@angular/core';
import { Recipe } from '../../../../../../models/recipe_models';

@Component({
  selector: 'app-recipe-sidebar',
  imports: [],
  template: `<div class="sidebar-card sticky-card">
    <!-- User Actions Section -->
    @if (isUserLoggedIn()) {
    <!-- Owner Actions -->
    @if (isUserRecipeAuthor()) {
    <div class="action-group owner-actions">
      <h3 class="action-group-title">Manage Recipe</h3>

      <button class="action-btn warning" (click)="editRecipe()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
        Edit Recipe
      </button>

      <button class="action-btn danger" (click)="deleteRecipe()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
        Delete Recipe
      </button>
    </div>

    <!-- User Actions (Non-Owner) -->
    } @else {
    <!-- Display Average Rating if available -->
    @if (hasRating()) {
    <div class="rating-section">
      <div class="rating-display">
        <span class="rating-value">{{ getFormattedRating() }}</span>
        <svg class="rating-star" viewBox="0 0 20 20">
          <path
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
        </svg>
      </div>
      <p class="rating-count">{{ getRatingCount() }} ratings</p>
    </div>
    }

    <div class="user-rating-section">
      <button class="action-btn primary" (click)="toggleFavorite()">
        <svg
          class="w-5 h-5"
          [class.fill-current]="isFavorite()"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
        {{ isFavorite() ? 'Remove Favorite' : 'Add to Favorites' }}
      </button>

      <button class="action-btn secondary" (click)="openReview()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
          />
        </svg>
        Write Review
      </button>
    </div>
    } } @else {
    <!-- Show rating to non-logged in users -->
    @if (hasRating()) {
    <div class="rating-section">
      <div class="rating-display">
        <span class="rating-value">{{ getFormattedRating() }}</span>
        <svg class="rating-star" viewBox="0 0 20 20">
          <path
            d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"
          />
        </svg>
      </div>
      <p class="rating-count">{{ getRatingCount() }} ratings</p>
    </div>
    } }

    <!-- Tags Section -->
    @if (recipe().tags && recipe().tags!.length > 0) {
    <div class="tags-section">
      <label class="tags-label">Tags</label>
      <div class="tags-container">
        @for (tag of recipe().tags; track tag) {
        <span class="recipe-tag">{{ tag.name }}</span>
        }
      </div>
    </div>
    }
  </div>`,
  styleUrl: './recipe-sidebar.scss',
})
export class RecipeSidebar {
  recipe = input.required<Recipe>();
  isUserLoggedIn = input(false);
  isUserRecipeAuthor = input(false);
  isFavorite = input(false);

  favoriteToggled = output<void>();
  reviewOpened = output<void>();
  editRequested = output<void>();
  deleteRequested = output<void>();

  hasRating = computed(() => {
    const rating = this.recipe().averageRating;
    return rating !== null && rating !== undefined && !isNaN(Number(rating));
  });

  getFormattedRating(): string {
    const rating = this.recipe().averageRating;
    if (rating === null || rating === undefined) return '0.0';

    const numRating = Number(rating);
    return isNaN(numRating) ? '0.0' : numRating.toFixed(1);
  }

  getRatingCount(): string {
    const count = this.recipe().ratingCount;
    if (count === null || count === undefined) return '0';

    const numCount = Number(count);
    return isNaN(numCount) ? '0' : numCount.toString();
  }

  toggleFavorite(): void {
    this.favoriteToggled.emit();
  }

  openReview(): void {
    this.reviewOpened.emit();
  }

  editRecipe(): void {
    this.editRequested.emit();
  }

  deleteRecipe(): void {
    this.deleteRequested.emit();
  }
}
