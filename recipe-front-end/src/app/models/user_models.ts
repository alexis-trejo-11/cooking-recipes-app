export interface User {
  id: string;
  fullName: string;
  email: string;
  phoneNumber?: string;
  roles: string[];
}

export interface UserProfile {
  id: string; // id (alias)
  full_name: string;
  profile_picture_url?: string | null;
  bio?: string | null;
  date_of_birth?: string | null; // ISO datetime
  gender?: string | null;

  email: string;
  phone_number?: string | null;

  joined_at: string; // ISO datetime
  last_login?: string | null; // ISO datetime

  favorite_recipes_count: number;
  created_recipes_count: number;
  reviewed_recipes_count: number;
}

export interface UpdateProfile {
  user_id: string; // id (alias)
  full_name: string;
  profile_picture_url?: string | null;
  bio?: string | null;
  date_of_birth?: string | null; // ISO datetime
  gender?: string | null;

  email: string;
  phone_number?: string | null;
}
