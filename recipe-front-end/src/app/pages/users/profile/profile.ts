import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { UserService } from '../../../services/user.service';
import { AuthService } from '../../../services/auth.service';
import { RecipeService } from '../../../services/recipe.service';
import { RecipeCard } from '../../../shared/recipe-card/recipe-card';
import {
  PaginationResponse,
  RecipeSummary,
  RecipeSummaryPage,
} from '../../../models/recipe_models';
import { UpdateProfile, UserProfile } from '../../../models/user_models';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, RecipeCard],
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss'],
})
export class Profile implements OnInit {
  private userService = inject(UserService);
  private authService = inject(AuthService);
  private recipeService = inject(RecipeService);

  profile = signal<UserProfile | null>(null);
  userRecipes = signal<RecipeSummary[]>([]);
  pagination = signal<PaginationResponse | null>(null);
  loading = signal(true);
  loadingRecipes = signal(true);
  editing = signal(false);
  saving = signal(false);

  editData: UpdateProfile = {
    user_id: '',
    full_name: '',
    email: '',
  };

  currentPage = 1;
  pageSize = 9;

  ngOnInit(): void {
    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.loadProfile();
      this.loadUserRecipes(currentUser.id, this.currentPage, this.pageSize);
    }
  }

  loadProfile(): void {
    this.userService.getUserProfile().subscribe({
      next: (profile) => {
        this.profile.set(profile);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  loadUserRecipes(userId: string, page: number, pageSize: number): void {
    this.loadingRecipes.set(true);
    this.recipeService.getRecipesByAuthor().subscribe({
      next: (recipePage: RecipeSummaryPage) => {
        this.userRecipes.set(recipePage.recipes);
        this.pagination.set(recipePage.pagination);
        this.loadingRecipes.set(false);
      },
      error: () => this.loadingRecipes.set(false),
    });
  }

  startEdit(): void {
    const current = this.profile();
    if (current) {
      this.editData = {
        user_id: current.id,
        full_name: current.full_name,
        email: current.email,
        bio: current.bio || '',
        phone_number: current.phone_number || '',
        date_of_birth: current.date_of_birth || '',
        gender: current.gender || '',
        profile_picture_url: current.profile_picture_url || '',
      };
      this.editing.set(true);
    }
  }

  cancelEdit(): void {
    this.editing.set(false);
    this.editData = {
      user_id: '',
      full_name: '',
      email: '',
    };
  }

  saveProfile(): void {
    const currentUser = this.authService.currentUser();
    if (!currentUser) return;

    this.saving.set(true);
    this.userService.updateProfile(currentUser.id, this.editData).subscribe({
      next: (updatedProfile) => {
        this.profile.set(updatedProfile);
        this.editing.set(false);
        this.saving.set(false);
      },
      error: () => this.saving.set(false),
    });
  }

  nextPage(): void {
    if (this.pagination()?.next_page) {
      this.currentPage = this.pagination()!.next_page!;
      const currentUser = this.authService.currentUser();
      if (currentUser) {
        this.loadUserRecipes(currentUser.id, this.currentPage, this.pageSize);
      }
    }
  }

  previousPage(): void {
    if (this.pagination()?.previous_page) {
      this.currentPage = this.pagination()!.previous_page!;
      const currentUser = this.authService.currentUser();
      if (currentUser) {
        this.loadUserRecipes(currentUser.id, this.currentPage, this.pageSize);
      }
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  formatDateTime(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  formatGender(gender: string): string {
    const genderMap: { [key: string]: string } = {
      male: 'Male',
      female: 'Female',
      other: 'Other',
      prefer_not_to_say: 'Prefer not to say',
    };
    return genderMap[gender] || gender;
  }
}
