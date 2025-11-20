export interface User {
  id: string;
  fullName: string;
  email: string;
  phoneNumber?: string;
  roles: string[];
}

export interface UserProfile {
  id: string; // id (alias)
  fullName: string;
  profilePictureUrl?: string | null;
  bio?: string | null;
  dateOfBirth?: string | null; // ISO datetime
  gender?: string | null;

  email: string;
  phoneNumber?: string | null;

  joinedAt: string; // ISO datetime
  lastLogin?: string | null; // ISO datetime

  favoriteRecipesCount: number;
  createdRecipesCount: number;
  reviewedRecipesCount: number;
}

export interface UpdateProfile {
  userId: string; // id (alias)
  fullName: string;
  profilePictureUrl?: string | null;
  bio?: string | null;
  dateOfBirth?: string | null; // ISO datetime
  gender?: string | null;

  email: string;
  phoneNumber?: string | null;
}
