import { Component, inject, signal } from '@angular/core';
import { Router } from 'express';
import { AuthService } from '../../../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LoginCredentials } from '../../../models/auth_models';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  //private router = inject(Router);
  private authService = inject(AuthService);

  credentials: LoginCredentials = { email: '', password: '' };

  loading = signal(false);
  error = signal('');

  handleLogin(): void {}
}
