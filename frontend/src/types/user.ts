export type UserRole = 
  | 'researcher' 
  | 'startup_founder' 
  | 'innovation_manager' 
  | 'administrator';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface ApiError {
  success: boolean;
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
