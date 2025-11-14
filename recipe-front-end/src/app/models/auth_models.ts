export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupRequest {
  firstname: string;
  lastname: string;
  email: string;
  phoneNumber?: string;
  password: string;
  gender?: 'male' | 'female' | 'other';
  dateOfBirth?: string;
}

export interface User {
  id: number;
  name: string;
}
