import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { getApiUrl } from '../../enviorments/runtime-config';
import { catchError, Observable, tap, throwError } from 'rxjs';
import { UpdateProfile, UserProfile } from '../models/user_models';
import { ApiErrorResponse } from '../models/auth_models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private tokenKey = 'auth_token';

  private http = inject(HttpClient);
  private get apiUrl() {
    return `${getApiUrl()}/users`;
  }

  getUserProfile(): Observable<UserProfile> {
    const token = this.getAccessToken();
    if (!token) {
      console.error('❌ No hay token disponible para obtener el usuario');
      return throwError(() => new Error('No authentication token available'));
    }

    console.log('🔐 Token disponible:', token.substring(0, 20) + '...');

    const headers = {
      Authorization: `Bearer ${token}`,
    };

    return this.http.get<UserProfile>(`${this.apiUrl}/profile`, { headers }).pipe(
      tap((profile: UserProfile) => {
        return profile;
      }),
      catchError((error: HttpErrorResponse) => {
        return this.handleError(error);
      })
    );
  }

  updateProfile(userId: string, data: UpdateProfile): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/profile`, data);
  }

  deleteUserAccount(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/profile`);
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

  private getAccessToken(): string | null {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    return localStorage.getItem(this.tokenKey);
  }
}
