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

  constructor() {}

  login(loginRequest: LoginRequest): Observable<AuthSessionResponse> {
    return this.http.post<AuthSessionResponse>(`${this.apiURL}/login`, loginRequest).pipe(
      tap((response: AuthSessionResponse) => {
        this.handleAuthSuccess(response);
      }),
      catchError((error: HttpErrorResponse) => {
        return this.handleError(error);
      })
    );
  }

  signup(signupRequest: SignupRequest): Observable<AuthSessionResponse> {
    return this.http.post<AuthSessionResponse>(`${this.apiURL}/signup`, signupRequest).pipe(
      tap((response: AuthSessionResponse) => {
        this.handleAuthSuccess(response);
      }),
      catchError((error: HttpErrorResponse) => {
        return this.handleError(error);
      })
    );
  }

  private checkInitialAuthState(): void {
    const token = this.getAccessToken();
    if (token) {
      this.isAuthenticated.set(true);
      this.getCurrentUser().subscribe();
    } else {
      this.isAuthenticated.set(false);
    }
  }

  handleAuthSuccess(response: AuthSessionResponse): void {
    this.setTokens(response.accessToken, response.refreshToken);

    this.isAuthenticated.set(true);
    this.getCurrentUser().subscribe;
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorResponse: ApiErrorResponse;

    if (error.error instanceof ErrorEvent) {
      errorResponse = {
        error: {
          code: 'CLIENT_ERROR',
          message: 'Conection Error',
          details: { string: error.error.message },
        },
      };
    } else {
      errorResponse = (error.error as ApiErrorResponse) || {
        code: `HTTP_${error.status}`,
        message: error.message || 'Error',
        details: { string: error.statusText },
      };
    }

    return throwError(() => errorResponse);
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiURL}/auth/me`).pipe(
      tap((user: User) => {
        this.currentUser.set(user);
      }),
      catchError((error: HttpErrorResponse) => {
        this.currentUser.set(undefined);
        return this.handleError(error);
      })
    );
  }

  logout(): Observable<any> {
    const refreshToken = this.getRefreshToken();

    const logoutRequest = this.http
      .post(`${this.apiURL}/logout`, {
        refreshToken,
      })
      .pipe(
        catchError((error: HttpErrorResponse) => {
          // Clear Even if Backend Fails
          this.clearAuthData();
          return of({});
        })
      );

    this.clearAuthData();
    return logoutRequest;
  }

  private setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem(this.tokenKey, accessToken);
    localStorage.setItem(this.refreshTokenKey, refreshToken);
  }

  private clearAuthData(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    this.isAuthenticated.set(false);
    this.currentUser.set(undefined);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken(): string | null {
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
