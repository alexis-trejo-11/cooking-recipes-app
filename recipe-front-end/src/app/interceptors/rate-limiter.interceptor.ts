import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const rateLimitInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 429) {
        console.log('Rate limit excedido, redirigiendo...');

        const retryAfter = error.headers?.get('Retry-After');
        const resetTime = retryAfter ? parseInt(retryAfter) * 1000 : 60000;

        router.navigate(['/rate-limit'], {
          state: {
            resetTime,
            errorMessage: error.error?.message || 'Too many requests',
          },
        });

        return throwError(() => error);
      }

      return throwError(() => error);
    })
  );
};
