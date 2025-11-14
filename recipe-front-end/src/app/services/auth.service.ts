import { Injectable, signal } from '@angular/core';
import { sign } from 'crypto';
import { Observable, of } from 'rxjs';
import { User } from '../models/auth_models';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  isAuthenticated = signal(false);

  currentUser(): User | undefined {
    return {
      id: 1,
      name: 'Alexis Trejo',
    };
  }

  logout(): Observable<any> {
    return of({});
  }
}
