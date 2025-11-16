import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../enviorments/enviroment';
import { Observable } from 'rxjs';
import { UpdateProfile, UserProfile } from '../models/user_models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/users`;

  getUserProfile(userId: string): Observable<UserProfile> {
    return this.http.get<any>(`${this.apiUrl}/profile`);
  }

  updateProfile(userId: string, data: UpdateProfile): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/profile`, data);
  }

  deleteUserAccount(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/profile`);
  }
}
