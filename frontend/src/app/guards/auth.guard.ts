import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  const token = authService.getAccessToken();
  if (token) {
    return authService.getCurrentUser().pipe(
      take(1),
      map((user) => {
        if (user) {
          return true;
        } else {
          console.log('AuthGuard: Invalid token, redirecting to login');
          router.navigate(['/login'], {
            queryParams: { returnUrl: state.url },
          });
          return false;
        }
      })
    );
  }

  console.log('AuthGuard: Not authenticated, redirecting to login');
  router.navigate(['/login'], {
    queryParams: { returnUrl: state.url },
  });
  return false;
};
