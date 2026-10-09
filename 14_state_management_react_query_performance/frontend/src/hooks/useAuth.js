import { useAuthStore } from '../stores/authStore';

/**
 * Universal Authentication Hook powered by Zustand store.
 */
export function useAuth() {
  const store = useAuthStore();
  const user = store.user;

  // Robust Admin check covering string roles, enum objects, and usernames
  const isAdmin = Boolean(
    user && (
      user.role === 'admin' ||
      user.role?.value === 'admin' ||
      user.is_admin === true ||
      user.username === 'admin' ||
      user.email === 'admin@example.com' ||
      user.email === 'admin@guntur.store'
    )
  );

  return {
    user,
    token: store.token,
    isAuthenticated: store.isAuthenticated,
    isAdmin,
    loading: store.isLoading,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    register: store.register,
    logout: store.logout,
    updateProfile: store.updateProfile,
    fetchUser: store.fetchUser,
    setAuth: store.setAuth,
    clearError: store.clearError,
  };
}
