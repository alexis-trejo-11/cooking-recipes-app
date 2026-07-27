import { inject, Injectable, signal, PLATFORM_ID } from '@angular/core';
import { catchError, Observable, of, Subject, switchMap, take, tap, throwError } from 'rxjs';
import { User, UserProfile } from '../models/user_models';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { getApiUrl } from '../../enviorments/runtime-config';
import {
  ApiErrorResponse,
  AuthSessionResponse,
  LoginRequest,
  SignupRequest,
} from '../models/auth_models';
import { isPlatformBrowser } from '@angular/common';
import { response } from 'express';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private get apiURL() {
    return getApiUrl() + '/auth';
  }
  private platformId = inject(PLATFORM_ID);

  isAuthenticated = signal(false);
  currentUser = signal<User | undefined>(undefined);
  userProfile = signal<UserProfile | null>(null);

  private tokenKey = 'auth_token';
  private refreshTokenKey = 'refresh_token';
  private refreshInProgress = false;
  private refreshSubject = new Subject<string>();

  private isBrowser: boolean;
  private initialized = false;

  constructor() {
    this.isBrowser = isPlatformBrowser(this.platformId);
    console.log('AuthService - Platform:', this.isBrowser ? 'Browser' : 'Server');
  }

  initialize(): Promise<boolean> {
    if (this.initialized) {
      return Promise.resolve(this.isAuthenticated());
    }

    return new Promise((resolve) => {
      if (this.isBrowser) {
        this.checkInitialAuthState().then((authenticated) => {
          this.initialized = true;
          resolve(authenticated);
        });
      } else {
        this.initialized = true;
        resolve(false);
      }
    });
  }

  login(loginRequest: LoginRequest): Observable<AuthSessionResponse> {
    console.log('Iniciando login para:', loginRequest.email);
    return this.http.post<any>(`${this.apiURL}/login`, loginRequest).pipe(
      tap((response: AuthSessionResponse) => {
        console.log('Login exitoso, respuesta completa:', response);

        console.log(
          ' AccessToken mapeado:',
          response.accessToken ? response.accessToken.substring(0, 4) + '...' : 'NO TOKEN'
        );
        console.log(
          ' RefreshToken mapeado:',
          response.refreshToken ? response.refreshToken.substring(0, 4) + '...' : 'NO TOKEN'
        );

        this.handleAuthSuccess(response);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error en login:', error);
        return this.handleError(error);
      })
    );
  }

  signup(signupRequest: SignupRequest): Observable<AuthSessionResponse> {
    console.log('Iniciando registro para:', signupRequest.email);
    return this.http.post<AuthSessionResponse>(`${this.apiURL}/signup`, signupRequest).pipe(
      tap((response: AuthSessionResponse) => {
        console.log('Registro exitoso, manejando respuesta');
        this.handleAuthSuccess(response);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error en registro:', error);
        return this.handleError(error);
      })
    );
  }

  private async checkInitialAuthState(): Promise<boolean> {
    const token = this.getAccessToken();
    console.log('Token encontrado en localStorage:', !!token);

    if (token && token !== 'undefined' && token !== 'null') {
      console.log('Token válido encontrado, verificando usuario actual');
      this.isAuthenticated.set(true);

      try {
        const user = await this.getCurrentUser().toPromise();
        console.log('Usuario cargado al iniciar:', user);
        this.isAuthenticated.set(true);
        return true;
      } catch (error) {
        console.error('Error cargando usuario inicial:', error);
        this.clearAuthData();
        this.isAuthenticated.set(false);
        return false;
      }
    } else {
      console.log('No hay token válido, usuario no autenticado');
      this.clearAuthData();
      this.isAuthenticated.set(false);
      return false;
    }
  }

  handleAuthSuccess(response: AuthSessionResponse): void {
    console.log('Manejo de autenticación exitosa');
    this.setTokens(response.accessToken, response.refreshToken);

    this.isAuthenticated.set(true);

    this.getCurrentUser().subscribe({
      next: (user) => {
        console.log('Usuario actual cargado después de login:', user);
      },
      error: (error) => {
        console.error('Error cargando usuario después de login:', error);
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
    console.log('Solicitando usuario actual...');

    const token = this.getAccessToken();

    if (!token || token === 'undefined' || token === 'null') {
      console.error('No hay token válido disponible para obtener el usuario');
      this.currentUser.set(undefined);
      this.isAuthenticated.set(false);
      return throwError(() => new Error('No valid authentication token available'));
    }

    console.log('Token disponible:', token.substring(0, 4) + '...');
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    console.log('Headers de la petición:', headers);

    return this.http.get<User>(`${this.apiURL}/me`, { headers }).pipe(
      tap((user: User) => {
        console.log('Usuario actual obtenido:', user);
        this.currentUser.set(user);
        this.isAuthenticated.set(true);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error obteniendo usuario actual:', error);
        console.error('Status:', error.status);
        console.error('URL:', error.url);

        if (error.status === 401) {
          console.log('ERROR 401 - Token inválido o expirado');
          this.clearAuthData();
        }

        this.currentUser.set(undefined);
        this.isAuthenticated.set(false);
        return throwError(() => error);
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
          console.error('Error en logout del servidor:', error);
          // Clear Even if Backend Fails
          this.clearAuthData();
          return of({});
        })
      );

    this.clearAuthData();
    return logoutRequest;
  }

  private checkAndRefreshToken(): void {
    const token = this.getAccessToken();

    if (!token || !this.isAuthenticated()) {
      return;
    }

    if (this.isTokenExpired()) {
      console.log('🔄 Token expirado, intentando refresh...');
      this.refreshToken().subscribe();
    } else if (this.isTokenAboutToExpire()) {
      console.log('🔄 Token por expirar, refrescando preventivamente...');
      this.refreshToken().subscribe();
    }
  }

  private isTokenAboutToExpire(): boolean {
    const token = this.getAccessToken();
    if (!token) return true;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Convertir a milisegundos
      const now = Date.now();
      const timeUntilExpiry = exp - now;

      // Refrescar si queda menos de 10 minutos
      return timeUntilExpiry < 10 * 60 * 1000;
    } catch {
      return true;
    }
  }

  refreshToken(): Observable<AuthSessionResponse> {
    console.log('🔄 Iniciando refresh token...');

    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      console.error('❌ No hay refresh token disponible');
      this.clearAuthData();
      return throwError(() => new Error('No refresh token available'));
    }

    console.log('Refresh token encontrado:', refreshToken.substring(0, 20) + '...');

    // El endpoint y body dependen de tu backend
    return this.http
      .post<any>(`${this.apiURL}/refresh`, {
        refresh_token: refreshToken, // Asegúrate que el nombre del campo sea correcto
      })
      .pipe(
        tap((response: any) => {
          console.log('✅ Refresh token exitoso:', response);

          // Mapear la respuesta según lo que devuelve tu backend
          const mappedResponse: AuthSessionResponse = {
            accessToken: response.access_token || response.accessToken,
            refreshToken: response.refresh_token || response.refreshToken,
            tokenType: response.token_type || 'bearer',
          };

          console.log('Nuevo access token:', mappedResponse.accessToken?.substring(0, 20) + '...');
          console.log(
            'Nuevo refresh token:',
            mappedResponse.refreshToken?.substring(0, 20) + '...'
          );

          // Guardar los nuevos tokens
          this.setTokens(mappedResponse.accessToken, mappedResponse.refreshToken);
        }),
        catchError((error: HttpErrorResponse) => {
          console.error('❌ Error en refresh token:', error);

          if (error.status === 401 || error.status === 400) {
            console.log('🔄 Refresh token expirado o inválido, cerrando sesión...');
            this.clearAuthData();
          }

          return throwError(() => error);
        })
      );
  }

  getValidAccessToken(): Observable<string> {
    const token = this.getAccessToken();

    if (!token) {
      return throwError(() => new Error('No token available'));
    }

    if (!this.isTokenAboutToExpire()) {
      return of(token);
    }

    return this.refreshToken().pipe(switchMap((response) => of(response.accessToken)));
  }

  getTokenInfo(): { exp: number; iat: number; sub: string; email: string } | null {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        exp: payload.exp,
        iat: payload.iat,
        sub: payload.sub,
        email: payload.email,
      };
    } catch {
      return null;
    }
  }

  private setTokens(accessToken: string, refreshToken: string) {
    console.log('Guardando tokens en localStorage');

    if (!this.isBrowser) {
      return;
    }

    if (!accessToken || !refreshToken) {
      console.error('Intentando guardar tokens inválidos');
      return;
    }

    try {
      localStorage.setItem(this.tokenKey, accessToken);
      localStorage.setItem(this.refreshTokenKey, refreshToken);
    } catch (error) {
      console.error('Error saving tokens to localStorage:', error);
    }
  }

  public clearAuthData(): void {
    if (this.isBrowser) {
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.refreshTokenKey);
    }
    this.isAuthenticated.set(false);
    this.currentUser.set(undefined);
    this.userProfile.set(null);
  }

  public getAccessToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }

    try {
      const token = localStorage.getItem(this.tokenKey);

      if (token === 'undefined' || token === 'null') {
        console.warn('Token inválido encontrado en localStorage:', token);
        this.clearAuthData();
        return null;
      }

      return token;
    } catch (error) {
      console.error('Error accessing localStorage:', error);
      return null;
    }
  }

  private getRefreshToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }

    try {
      const token = localStorage.getItem(this.refreshTokenKey);

      if (token === 'undefined' || token === 'null') {
        console.warn('Refresh token inválido encontrado en localStorage:', token);
        localStorage.removeItem(this.refreshTokenKey);
        return null;
      }

      return token;
    } catch (error) {
      console.error('Error accessing localStorage:', error);
      return null;
    }
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
