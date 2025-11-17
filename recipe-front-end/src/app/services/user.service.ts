import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../enviorments/enviroment';
import { catchError, Observable, tap, throwError } from 'rxjs';
import { UpdateProfile, UserProfile } from '../models/user_models';
import { ApiErrorResponse } from '../models/auth_models';
import { error } from 'console';

@Injectable({ providedIn: 'root' })
export class UserService {
  private tokenKey = 'auth_token';

  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/users`;

  getUserProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.apiUrl}/profile`).pipe(
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

  getAccessToken(): string | null {
    return localStorage.getItem(this.tokenKey);
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
}
