import { Component, inject, input, OnInit, output, signal } from '@angular/core';
import { ReviewService } from '../../../../../../services/review.services';
import { AuthService } from '../../../../../../services/auth.service';
import { CreateReviewRequest, Review } from '../../../../../../models/review_models';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-review-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './review-modal.html',
  styleUrl: './review-modal.scss',
})
export class ReviewModal implements OnInit {
  private reviewService = inject(ReviewService);
  private authService = inject(AuthService);

  recipeId = input.required<string>();
  isOpen = input(false);

  closed = output<void>();
  reviewSubmitted = output<Review>();
  reviewDeleted = output<string>();

  userReview = signal<Review | null>(null);
  loading = signal(true);
  submitting = signal(false);
  deleting = signal(false);

  rating = signal(0);
  comment = signal('');
  hoverRating = signal(0);

  ngOnInit() {
    const recipeId = this.recipeId();
    const currentUser = this.currentUser;

    console.log('[ReviewModal] Component initialized', {
      recipeId,
      userId: currentUser?.id,
      userEmail: currentUser?.email,
      timestamp: new Date().toISOString(),
    });

    this.loadUserReview();
  }

  private loadUserReview(): void {
    const recipeId = this.recipeId();

    console.log('[ReviewModal] Loading user review', {
      recipeId,
      timestamp: new Date().toISOString(),
    });

    this.loading.set(true);

    this.reviewService.getUserReview(recipeId).subscribe({
      next: (review) => {
        console.log('[ReviewModal] User review loaded successfully', {
          recipeId,
          hasReview: !!review,
          reviewId: review?.id,
          rating: review?.rating,
          commentLength: review?.comment?.length,
          timestamp: new Date().toISOString(),
        });

        this.userReview.set(review);
        if (review) {
          this.rating.set(review.rating);
          this.comment.set(review.comment);

          console.log('[ReviewModal] Review data populated into form', {
            rating: review.rating,
            hasComment: !!review.comment,
          });
        }
        this.loading.set(false);
      },
      error: (error) => {
        console.error('[ReviewModal] Failed to load user review', {
          recipeId,
          error: error?.message || 'Unknown error',
          status: error?.status,
          timestamp: new Date().toISOString(),
        });

        this.loading.set(false);
      },
    });
  }

  setRating(rating: number): void {
    console.log('[ReviewModal] User set rating', {
      recipeId: this.recipeId(),
      previousRating: this.rating(),
      newRating: rating,
      timestamp: new Date().toISOString(),
    });

    this.rating.set(rating);
  }

  setHoverRating(rating: number): void {
    this.hoverRating.set(rating);
  }

  submitReview(): void {
    console.log('Submitting review for recipeId:', this.recipeId());
    if (this.rating() === 0 || !this.comment().trim()) {
      return;
    }

    this.submitting.set(true);

    const reviewData: CreateReviewRequest = {
      recipeId: this.recipeId(),
      rating: this.rating(),
      comment: this.comment().trim(),
    };

    if (this.userReview()) {
      // Update existing review
      this.reviewService.updateReview(this.userReview()!.id, reviewData).subscribe({
        next: (updatedReview) => {
          this.userReview.set(updatedReview);
          this.reviewSubmitted.emit(updatedReview);
          this.submitting.set(false);
          this.close();
        },
        error: () => {
          this.submitting.set(false);
        },
      });
    } else {
      // Create new review
      this.reviewService.createReview(reviewData).subscribe({
        next: (newReview) => {
          this.userReview.set(newReview);
          this.reviewSubmitted.emit(newReview);
          this.submitting.set(false);
          this.close();
        },
        error: () => {
          this.submitting.set(false);
        },
      });
    }
  }

  deleteReview(): void {
    if (!this.userReview()) return;

    this.deleting.set(true);
    this.reviewService.deleteReview(this.userReview()!.id).subscribe({
      next: () => {
        this.userReview.set(null);
        this.rating.set(0);
        this.comment.set('');
        this.reviewDeleted.emit(this.userReview()!.id);
        this.deleting.set(false);
        this.close();
      },
      error: () => {
        this.deleting.set(false);
      },
    });
  }

  close(): void {
    this.closed.emit();
  }

  get modalTitle(): string {
    return this.userReview() ? 'Edit Your Review' : 'Write a Review';
  }

  get submitButtonText(): string {
    if (this.submitting()) return 'Submitting...';
    return this.userReview() ? 'Update Review' : 'Submit Review';
  }

  get canSubmit(): boolean {
    return this.rating() > 0 && this.comment().trim().length > 0 && !this.submitting();
  }

  get currentUser() {
    return this.authService.currentUser();
  }

  getRatingText(rating: number): string {
    const ratingTexts: { [key: number]: string } = {
      1: 'Poor',
      2: 'Fair',
      3: 'Good',
      4: 'Very Good',
      5: 'Excellent',
    };
    return ratingTexts[rating] || '';
  }
}
