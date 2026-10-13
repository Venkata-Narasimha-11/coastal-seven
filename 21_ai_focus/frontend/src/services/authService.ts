import apiClient from './apiClient';
import { User, TokenResponse } from '../types/api';
import { LoginFormData, RegisterFormData } from '../types/forms';

export interface LoginResponse {
  user: User;
  token: TokenResponse;
}

export const authService = {
  /**
   * Authenticate user with credentials object or username and password strings.
   */
  async login(
    credentialsOrUsername: LoginFormData | string,
    password?: string
  ): Promise<LoginResponse | any> {
    const payload =
      typeof credentialsOrUsername === 'string'
        ? { username: credentialsOrUsername, password: password || '' }
        : credentialsOrUsername;

    // 1. Post to login endpoint
    const token = await apiClient.post<TokenResponse>('/auth/login', payload);

    // Save token temporarily so subsequent /me call carries Authorization header
    if (token?.access_token) {
      localStorage.setItem('auth_token', token.access_token);
      localStorage.setItem('token', token.access_token);
    }

    // 2. Fetch authenticated user details
    const user = await apiClient.get<User>('/auth/me');
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user));
    }

    return { user, token, access_token: token?.access_token };
  },

  /**
   * Register a new user account.
   */
  async register(data: RegisterFormData | any): Promise<User> {
    return apiClient.post<User>('/auth/register', {
      username: data.username,
      email: data.email,
      password: data.password,
      role: data.role,
    });
  },

  /**
   * Fetch current authenticated user.
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  },

  /**
   * Alias for getCurrentUser for backward compatibility.
   */
  async getProfile(): Promise<User> {
    return this.getCurrentUser();
  },

  /**
   * Update profile.
   */
  async updateProfile(data: any): Promise<User> {
    return apiClient.put<User>('/auth/me', data);
  },
};

export default authService;
