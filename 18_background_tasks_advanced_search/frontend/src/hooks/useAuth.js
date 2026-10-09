import { useAuthStore } from '../stores/useAuthStore';

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
      user.role === 'ADMIN' ||
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
    error: null,
    login: store.login,
    logout: store.logout,
    setUser: store.setUser,
  };
}
