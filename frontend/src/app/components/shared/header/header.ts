import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { ThemeToggle } from '../theme-toggle/theme-toggle';

@Component({
  selector: 'app-header',
  imports: [RouterLink, RouterLinkActive, ThemeToggle],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  authService = inject(AuthService);
  private router = inject(Router);

  handleLogout(): void {
    this.authService.logout().subscribe();
  }

  onNavClick(route: string): void {
    console.log('🖱️ [HEADER] Nav clicked:', route);
    console.log('🖱️ [HEADER] Current URL:', this.router.url);
  }
}
