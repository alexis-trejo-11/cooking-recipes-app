import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { SignupRequest } from '../../../models/auth_models';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-singup',
  imports: [CommonModule, FormsModule],
  templateUrl: './singup.html',
  styleUrl: './singup.scss',
})
export class Singup {
  private authService = inject(AuthService);
  //private router = inject(Router);
  userData: SignupRequest = {
    firstname: '',
    lastname: '',
    email: '',
    phoneNumber: '',
    password: '',
    gender: undefined,
    dateOfBirth: '',
  };

  confirmPassword = '';
  loading = signal(false);
  error = signal('');

  genderOptions = [
    { value: '', label: 'Select Gender' },
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
    { value: 'other', label: 'Other' },
  ];

  handleSignup(): void {}

  getMinBirthDateAllowed(): string {
    const today = new Date();
    const minAgeDate = new Date(today.getFullYear() - 13, today.getMonth(), today.getDate()); // Users must be at least 13 years old
    return minAgeDate.toISOString().split('T')[0];
  }

  getMaxBirthDateAllowed(): string {
    const today = new Date();
    const maxAgeDate = new Date(today.getFullYear() - 100, today.getMonth(), today.getDate()); // Users can be at most 100 years old
    return maxAgeDate.toISOString().split('T')[0];
  }
}
