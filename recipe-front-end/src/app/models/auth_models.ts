export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber?: string;
  password: string;
  gender?: 'male' | 'female' | 'other';
  dateOfBirth?: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: { string: string };
  };
}

export interface AuthSessionResponse {
  tokenType: string;
  accessToken: string;
  refreshToken: string;
  userId?: string;
}
