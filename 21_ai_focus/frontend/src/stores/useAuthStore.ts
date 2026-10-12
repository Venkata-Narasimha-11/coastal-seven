import { create } from 'zustand';
import { AuthState } from '../types/state';
import { User } from '../types/api';

const getInitialUser = (): User | null => {
  try {
    const raw = localStorage.getItem('auth_user') || localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

const getInitialToken = (): string | null => {
  try {
    return localStorage.getItem('auth_token') || localStorage.getItem('token') || null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthState>((set) => ({
  user: getInitialUser(),
  token: getInitialToken(),
  isAuthenticated: Boolean(getInitialToken()),
  isLoading: false,

  login: (user: User, token: string) => {
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('auth_token', token);
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true, isLoading: false });
  },

  logout: () => {
    localStorage.removeItem('auth_user');
    localStorage.removeItem('user');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false, isLoading: false });
  },

  setUser: (user: User) => {
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, isAuthenticated: true });
  },
}));

export default useAuthStore;
