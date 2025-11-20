import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators';

export const publicGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    console.log('PublicGuard: User already authenticated, redirecting to dashboard');
    router.navigate(['/dashboard']);
    return false;
  }

  const token = authService.getAccessToken();
  if (token) {
    console.log('PublicGuard: Token found, verifying user...');
    return authService.getCurrentUser().pipe(
      take(1),
      map((user) => {
        if (user) {
          console.log('PublicGuard: Valid user, redirecting to dashboard');
          router.navigate(['/dashboard']);
          return false;
        } else {
          console.log('PublicGuard: Invalid token, allowing access');
          return true;
        }
      })
    );
  }
  console.log('PublicGuard: User not authenticated, access allowed');
  return true;
};
