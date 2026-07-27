import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../../../services/user.service';
import { AuthService } from '../../../../services/auth.service';
import { UpdateProfile, UserProfile } from '../../../../models/user_models';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss'],
})
export class Profile implements OnInit {
  private userService = inject(UserService);
  private authService = inject(AuthService);

  profile = signal<UserProfile | null>(null);
  loading = signal(true);
  editing = signal(false);
  saving = signal(false);

  editData: UpdateProfile = {
    userId: '',
    fullName: '',
    email: '',
  };

  ngOnInit(): void {
    console.log('📝 Init Profile');

    const currentUser = this.authService.currentUser();
    if (currentUser) {
      this.loadProfile();
    }
  }

  loadProfile(): void {
    console.log('📝 Cargando perfil del usuario...');
    this.userService.getUserProfile().subscribe({
      next: (profile) => {
        console.log('✅ Perfil cargado exitosamente:', profile);
        this.profile.set(profile);
        this.loading.set(false);
        console.log('🔴 Loading establecido en:', false);
      },
      error: (error) => {
        console.error('❌ Error cargando perfil:', error);
        this.loading.set(false);
        console.log('🔴 Loading establecido en:', false);
      },
    });
  }

  startEdit(): void {
    const current = this.profile();
    if (current) {
      this.editData = {
        userId: current.id,
        fullName: current.fullName,
        email: current.email,
        bio: current.bio || '',
        phoneNumber: current.phoneNumber || '',
        dateOfBirth: current.dateOfBirth || '',
        gender: current.gender || '',
        profilePictureUrl: current.profilePictureUrl || '',
      };
      this.editing.set(true);
    }
  }

  cancelEdit(): void {
    this.editing.set(false);
    this.editData = {
      userId: '',
      fullName: '',
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
