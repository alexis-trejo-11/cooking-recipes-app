import {
  HttpInterceptorFn,
  HttpErrorResponse,
  HttpRequest,
  HttpHandlerFn,
  HttpEvent,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { Observable, throwError, BehaviorSubject, from } from 'rxjs';
import { catchError, switchMap, take, filter, finalize } from 'rxjs/operators';

let refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);
let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!req.url.includes('/api/')) {
    return next(req);
  }

  // Clonar la request con el token actual
  const authReq = addToken(req, authService);

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si es error 401 (Unauthorized) → intentar refresh
      if (error.status === 401) {
        console.log('🔐 Interceptor: Token expirado, intentando refresh...');
        return handle401Error(authReq, next, authService, router);
      }

      // Para otros errores, simplemente propagar
      return throwError(() => error);
    })
  );
};

// Función helper para agregar token
const addToken = (req: HttpRequest<unknown>, authService: AuthService) => {
  const token = authService.getAccessToken();
  if (token) {
    return req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`),
    });
  }
  return req;
};

const handle401Error = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
  authService: AuthService,
  router: Router
): Observable<HttpEvent<unknown>> => {
  // Si ya estamos refrescando, esperar a que termine
  if (isRefreshing) {
    return refreshTokenSubject.pipe(
      filter((token) => token !== null),
      take(1),
      switchMap((token) => {
        const newReq = addToken(req, authService);
        return next(newReq);
      })
    );
  }

  isRefreshing = true;
  refreshTokenSubject.next(null);

  return authService.refreshToken().pipe(
    switchMap((response: any) => {
      console.log('✅ Token refrescado exitosamente');
      isRefreshing = false;
      refreshTokenSubject.next(response.accessToken);

      // Reintentar la petición original con el nuevo token
      const newReq = addToken(req, authService);
      return next(newReq);
    }),
    catchError((refreshError: any) => {
      console.error('❌ No se pudo refrescar el token:', refreshError);
      isRefreshing = false;
      refreshTokenSubject.next(null);

      // Limpiar datos de autenticación
      authService.clearAuthData();

      // Redirigir a login
      if (typeof window !== 'undefined') {
        router.navigate(['/login'], {
          queryParams: { sessionExpired: true },
        });
      }

      return throwError(() => refreshError);
    }),
    finalize(() => {
      isRefreshing = false;
    })
  );
};
