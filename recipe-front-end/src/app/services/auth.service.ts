import { inject, Injectable, signal } from '@angular/core';
import { catchError, Observable, of, tap, throwError } from 'rxjs';
import { User, UserProfile } from '../models/user_models';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../enviorments/enviroment';
import {
  ApiErrorResponse,
  AuthSessionResponse,
  LoginRequest,
  SignupRequest,
} from '../models/auth_models';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private apiURL = environment.apiUrl + '/auth';

  isAuthenticated = signal(false);
  currentUser = signal<User | undefined>(undefined);
  userProfile = signal<UserProfile | null>(null);

  private tokenKey = 'auth_token';
  private refreshTokenKey = 'refresh_token';

  constructor() {
    console.log('🔄 AuthService - Verificando estado de autenticación inicial');
    this.checkInitialAuthState();
  }

  login(loginRequest: LoginRequest): Observable<AuthSessionResponse> {
    console.log('🔐 Iniciando login para:', loginRequest.email);
    return this.http.post<any>(`${this.apiURL}/login`, loginRequest).pipe(
      tap((response: any) => {
        console.log('✅ Login exitoso, respuesta completa:', response);

        // ✅ Mapear los nombres de campos de snake_case a camelCase
        const mappedResponse: AuthSessionResponse = {
          accessToken: response.access_token, // ✅ Mapear access_token → accessToken
          refreshToken: response.refresh_token, // ✅ Mapear refresh_token → refreshToken
          tokenType: response.token_type,
          userId: response.user_id,
        };

        console.log(
          '🔐 AccessToken mapeado:',
          mappedResponse.accessToken
            ? mappedResponse.accessToken.substring(0, 20) + '...'
            : 'NO TOKEN'
        );
        console.log(
          '🔐 RefreshToken mapeado:',
          mappedResponse.refreshToken
            ? mappedResponse.refreshToken.substring(0, 20) + '...'
            : 'NO TOKEN'
        );

        this.handleAuthSuccess(mappedResponse);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('❌ Error en login:', error);
        return this.handleError(error);
      })
    );
  }

  signup(signupRequest: SignupRequest): Observable<AuthSessionResponse> {
    console.log('👤 Iniciando registro para:', signupRequest.email);
    return this.http.post<AuthSessionResponse>(`${this.apiURL}/signup`, signupRequest).pipe(
      tap((response: AuthSessionResponse) => {
        console.log('✅ Registro exitoso, manejando respuesta');
        this.handleAuthSuccess(response);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('❌ Error en registro:', error);
        return this.handleError(error);
      })
    );
  }

  private checkInitialAuthState(): void {
    const token = this.getAccessToken();
    console.log('🔍 Token encontrado en localStorage:', !!token);

    if (token) {
      console.log('✅ Token existe, verificando usuario actual');
      this.isAuthenticated.set(true);
      this.getCurrentUser().subscribe({
        next: (user) => console.log('✅ Usuario cargado al iniciar:', user),
        error: (error) => console.error('❌ Error cargando usuario inicial:', error),
      });
    } else {
      console.log('❌ No hay token, usuario no autenticado');
      this.isAuthenticated.set(false);
    }
  }

  handleAuthSuccess(response: AuthSessionResponse): void {
    console.log('🎯 Manejo de autenticación exitosa');
    this.setTokens(response.accessToken, response.refreshToken);

    this.isAuthenticated.set(true);

    this.getCurrentUser().subscribe({
      next: (user) => {
        console.log('✅ Usuario actual cargado después de login:', user);
      },
      error: (error) => {
        console.error('❌ Error cargando usuario después de login:', error);
      },
    });
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorResponse: ApiErrorResponse;

    if (error.error instanceof ErrorEvent) {
      errorResponse = {
        error: {
          code: 'CLIENT_ERROR',
          message: 'Connection Error',
          details: { string: error.error.message },
        },
      };
    } else {
      errorResponse = (error.error as ApiErrorResponse) || {
        error: {
          code: `HTTP_${error.status}`,
          message: error.message || 'Error',
          details: { string: error.statusText },
        },
      };
    }

    return throwError(() => errorResponse);
  }

  getCurrentUser(): Observable<User> {
    console.log('👤 Solicitando usuario actual...');

    // ✅ PRIMERO: Verificar que existe un token
    const token = this.getAccessToken();
    if (!token) {
      console.error('❌ No hay token disponible para obtener el usuario');
      this.currentUser.set(undefined);
      this.isAuthenticated.set(false);
      return throwError(() => new Error('No authentication token available'));
    }

    console.log('🔐 Token disponible:', token.substring(0, 20) + '...');

    // ✅ SEGUNDO: Construir headers correctamente
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    console.log('📤 Headers de la petición:', headers);

    return this.http.get<User>(`${this.apiURL}/me`, { headers }).pipe(
      tap((user: User) => {
        console.log('✅ Usuario actual obtenido:', user);
        this.currentUser.set(user);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('❌ Error obteniendo usuario actual:', error);
        console.error('🔴 Status:', error.status);
        console.error('🔴 URL:', error.url);

        // Log detallado del error
        if (error.status === 401) {
          console.log('🔐 ERROR 401 - Token inválido o expirado');
          console.log('🔐 Token usado:', token.substring(0, 20) + '...');
          this.clearAuthData();
        }

        this.currentUser.set(undefined);
        this.isAuthenticated.set(false);
        return this.handleError(error);
      })
    );
  }

  logout(): Observable<any> {
    console.log('🚪 Cerrando sesión...');
    const refreshToken = this.getRefreshToken();

    const logoutRequest = this.http
      .post(`${this.apiURL}/logout`, {
        refreshToken,
      })
      .pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('❌ Error en logout del servidor:', error);
          // Clear Even if Backend Fails
          this.clearAuthData();
          return of({});
        })
      );

    this.clearAuthData();
    return logoutRequest;
  }

  private setTokens(accessToken: string, refreshToken: string) {
    console.log('💾 Guardando tokens en localStorage');
    localStorage.setItem(this.tokenKey, accessToken);
    localStorage.setItem(this.refreshTokenKey, refreshToken);
  }

  private clearAuthData(): void {
    console.log('🧹 Limpiando datos de autenticación');
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    this.isAuthenticated.set(false);
    this.currentUser.set(undefined);
    this.userProfile.set(null);
  }

  public getAccessToken(): string | null {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    return localStorage.getItem(this.tokenKey);
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    return localStorage.getItem(this.refreshTokenKey);
  }

  addAuthHeader(headers: { [key: string]: string } = {}): { [key: string]: string } {
    const token = this.getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  isTokenExpired(): boolean {
    const token = this.getAccessToken();
    if (!token) return true;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // To milisecs
      return Date.now() >= exp - 5 * 60 * 1000; // 5 min margin
    } catch {
      return true;
    }
  }
}
