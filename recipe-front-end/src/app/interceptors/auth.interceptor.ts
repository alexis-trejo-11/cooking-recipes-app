import {
  HttpInterceptorFn,
  HttpErrorResponse,
  HttpRequest,
  HttpHandlerFn,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { catchError, switchMap, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const authService = inject(AuthService);

  // Solo intervenir en peticiones a nuestra API
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
        return handle401Error(authReq, next, authService);
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

// Función helper para manejar error 401
const handle401Error = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
  authService: AuthService
) => {
  return authService.refreshToken().pipe(
    switchMap(() => {
      // Después de refresh exitoso, reintentar la petición original
      console.log('✅ Token refrescado, reintentando petición...');
      const newToken = authService.getAccessToken();
      const newReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${newToken}`),
      });
      return next(newReq);
    }),
    catchError((refreshError: any) => {
      console.error('❌ No se pudo refrescar el token, cerrando sesión...');
      authService.clearAuthData();
      // Redirigir a login
      window.location.href = '/login';
      return throwError(() => refreshError);
    })
  );
};
