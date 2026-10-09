import api from './api';

export const authService = {
  /**
   * Register a new user account.
   */
  async register(data) {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  /**
   * Authenticate with username/email and password using JSON body.
   */
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  /**
   * Fetch currently logged-in user profile.
   */
  async getProfile() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Update profile.
   */
  async updateProfile(data) {
    const response = await api.put('/auth/me', data);
    return response.data;
  },
};
