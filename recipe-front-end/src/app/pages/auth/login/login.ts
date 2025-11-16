import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiErrorResponse, LoginRequest } from '../../../models/auth_models';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private router = inject(Router);
  private authService = inject(AuthService);

  credentials: LoginRequest = { email: '', password: '' };

  loading = signal(false);
  error = signal('');

  handleLogin(): void {
    // Reset prev err
    this.error.set('');

    if (!this.credentials.email || !this.credentials.password) {
      this.error.set('Please enter both email and password');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.credentials.email)) {
      this.error.set('Please enter a valid email address');
      return;
    }

    this.loading.set(true);

    this.authService.login(this.credentials).subscribe({
      next: (response) => {
        this.loading.set(false);
        console.log('Login successful:', response);

        this.router.navigate(['/users/dashboard']);
      },
    });
  }

  private handleLoginError(error: ApiErrorResponse): void {
    const errorCode = error.error?.code;
    const errorMessage = error.error?.message;

    switch (errorCode) {
      case 'INVALID_CREDENTIALS':
      case 'USER_NOT_FOUND':
        this.error.set('Invalid email or password');
        break;
      case 'USER_DISABLED':
        this.error.set('Your account has been disabled. Please contact support.');
        break;
      case 'EMAIL_NOT_VERIFIED':
        this.error.set('Please verify your email address before logging in.');
        break;
      case 'TOO_MANY_ATTEMPTS':
        this.error.set('Too many login attempts. Please try again later.');
        break;
      case 'NETWORK_ERROR':
        this.error.set('Network error. Please check your connection and try again.');
        break;
      default:
        this.error.set(errorMessage || 'An unexpected error occurred. Please try again.');
        break;
    }
  }

  clearError(): void {
    if (this.error()) {
      this.error.set('');
    }
  }
}
