import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { authService } from '../services/authService';

/**
 * Zustand Global Authentication Store.
 * Provides high-performance, atomic auth state without top-level re-render penalties.
 */
export const useAuthStore = create(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        token: localStorage.getItem('token') || null,
        isAuthenticated: Boolean(localStorage.getItem('token')),
        isLoading: false,
        error: null,

        // Set Auth Directly (e.g. for demo logins or mock testing)
        setAuth: (user, token) => {
          if (token) {
            localStorage.setItem('token', token);
          } else {
            localStorage.removeItem('token');
          }
          set(
            {
              user,
              token,
              isAuthenticated: Boolean(token && user),
              error: null,
            },
            false,
            'auth/setAuth'
          );
        },

        // Login Action
        login: async (username, password) => {
          set({ isLoading: true, error: null }, false, 'auth/loginPending');
          try {
            const data = await authService.login(username, password);
            const token = data.access_token || data.token;
            localStorage.setItem('token', token);

            // Fetch user profile immediately
            let user = data.user || null;
            if (!user) {
              try {
                user = await authService.getProfile();
              } catch (e) {
                user = { email: username, full_name: username, role: 'customer' };
              }
            }

            set(
              {
                user,
                token,
                isAuthenticated: true,
                isLoading: false,
                error: null,
              },
              false,
              'auth/loginSuccess'
            );
            return { success: true, user };
          } catch (err) {
            const message = err.response?.data?.detail || err.message || 'Login failed';
            set({ error: message, isLoading: false }, false, 'auth/loginFailure');
            return { success: false, error: message };
          }
        },

        // Register Action
        register: async (userData) => {
          set({ isLoading: true, error: null }, false, 'auth/registerPending');
          try {
            const user = await authService.register(userData);
            set({ isLoading: false, error: null }, false, 'auth/registerSuccess');
            return { success: true, user };
          } catch (err) {
            const message = err.response?.data?.detail || err.message || 'Registration failed';
            set({ error: message, isLoading: false }, false, 'auth/registerFailure');
            return { success: false, error: message };
          }
        },

        // Logout Action
        logout: () => {
          localStorage.removeItem('token');
          set(
            {
              user: null,
              token: null,
              isAuthenticated: false,
              error: null,
            },
            false,
            'auth/logout'
          );
        },

        // Fetch / Refresh Current User
        fetchUser: async () => {
          const { token } = get();
          if (!token) return;

          set({ isLoading: true }, false, 'auth/fetchUserPending');
          try {
            const user = await authService.getProfile();
            set({ user, isAuthenticated: true, isLoading: false }, false, 'auth/fetchUserSuccess');
          } catch (err) {
            console.error('Failed to restore user session:', err);
            // If token expired, log out cleanly
            if (err.response?.status === 401) {
              get().logout();
            } else {
              set({ isLoading: false });
            }
          }
        },

        // Update Profile Action
        updateProfile: async (data) => {
          set({ isLoading: true }, false, 'auth/updateProfilePending');
          try {
            const updated = await authService.updateProfile(data);
            set({ user: updated, isLoading: false }, false, 'auth/updateProfileSuccess');
            return { success: true, user: updated };
          } catch (err) {
            const message = err.response?.data?.detail || err.message || 'Profile update failed';
            set({ isLoading: false, error: message });
            return { success: false, error: message };
          }
        },

        clearError: () => set({ error: null }, false, 'auth/clearError'),
      }),
      {
        name: 'ecommerce-auth-storage',
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' }
  )
);
