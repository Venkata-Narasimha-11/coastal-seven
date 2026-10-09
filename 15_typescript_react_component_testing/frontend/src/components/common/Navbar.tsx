import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  ShoppingCart,
  FlaskConical,
  Store,
  User as UserIcon,
  LogOut,
  Layers,
  Gauge,
  Heart,
  Sun,
  Moon,
  ShieldCheck,
} from 'lucide-react';
import useAuthStore from '../../stores/useAuthStore';
import useCartStore from '../../stores/useCartStore';
import { useTheme, Theme } from '../../context/ThemeContext';
import Button from '../ui/Button';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const totalCartItems = useCartStore((state) =>
    state.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
  );

  let theme: Theme = 'light';
  let setTheme: (theme: Theme) => void = () => {};
  try {
    const themeCtx = useTheme();
    if (themeCtx) {
      theme = themeCtx.theme;
      setTheme = themeCtx.setTheme;
    }
  } catch {
    // In test environment without ThemeProvider
  }

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-6">
            <Link
              to="/"
              className="flex items-center gap-2.5 font-bold text-slate-900 dark:text-white text-lg tracking-tight hover:text-blue-600 transition-colors"
            >
              <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/30">
                <Store className="h-5 w-5" />
              </div>
              <span className="hidden sm:inline">TypeScript & Vitest E-Shop</span>
              <span className="sm:hidden font-bold">TS-Shop</span>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden lg:flex items-center space-x-1" aria-label="Main Navigation">
              <Link
                to="/"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                Products
              </Link>
              <Link
                to="/state-comparison"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  isActive('/state-comparison')
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                <Layers className="h-4 w-4 text-blue-500" />
                <span>State Comparison</span>
              </Link>
              <Link
                to="/performance-lab"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  isActive('/performance-lab')
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                <Gauge className="h-4 w-4 text-emerald-500" />
                <span>Performance Lab</span>
              </Link>
              <Link
                to="/testing-lab"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  isActive('/testing-lab')
                    ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-600 font-bold'
                    : 'text-amber-600 dark:text-amber-400 hover:bg-amber-50/50'
                }`}
              >
                <FlaskConical className="h-4 w-4 text-amber-500" />
                <span>Testing Lab</span>
              </Link>
              <Link
                to="/wishlist"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  isActive('/wishlist')
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                <Heart className="h-4 w-4 text-rose-500" />
                <span>Wishlist</span>
              </Link>
              <Link
                to="/orders"
                data-testid="nav-orders-link"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  isActive('/orders')
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                <span>Orders</span>
              </Link>
              {isAuthenticated && user?.role === 'admin' && (
                <Link
                  to="/admin"
                  data-testid="nav-admin-link"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                    isActive('/admin')
                      ? 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 font-bold'
                      : 'text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30 font-semibold'
                  }`}
                >
                  <ShieldCheck className="h-4 w-4" />
                  <span>Admin</span>
                </Link>
              )}
            </nav>
          </div>

          {/* Right Action Icons */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle theme"
              data-testid="theme-toggle-btn"
            >
              {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </button>

            {/* Cart Link */}
            <Link
              to="/cart"
              data-testid="nav-cart-link"
              aria-label={`Shopping cart with ${totalCartItems} items`}
              className="relative p-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <ShoppingCart className="h-5 w-5" />
              {totalCartItems > 0 && (
                <span
                  data-testid="cart-badge-count"
                  className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow"
                >
                  {totalCartItems}
                </span>
              )}
            </Link>

            {/* Auth Actions */}
            {isAuthenticated && user ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-700">
                <div className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-200">
                  <div className="h-8 w-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
                    <UserIcon className="h-4 w-4" />
                  </div>
                  <span className="font-medium hidden md:inline">{user.username}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  aria-label="Logout"
                  className="text-slate-500 hover:text-red-600"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  <span>Logout</span>
                </Button>
              </div>
            ) : (
              <Link to="/login">
                <Button variant="primary" size="sm">
                  Sign In
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
