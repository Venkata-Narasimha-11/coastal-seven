import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  ShoppingCart,
  Store,
  User as UserIcon,
  LogOut,
  Heart,
  Sun,
  Moon,
  ShieldCheck,
} from 'lucide-react';
import useAuthStore from '../../stores/useAuthStore';
import useCartStore from '../../stores/useCartStore';
import { useWishlist } from '../../hooks/useWishlist';
import { useTheme, Theme } from '../../context/ThemeContext';
import Button from '../ui/Button';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { totalItems: wishlistCount } = useWishlist();
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
              <span className="font-black text-xl tracking-tight text-blue-600 dark:text-blue-400">Gunturu</span>
              <span className="sr-only">TypeScript & Vitest E-Shop</span>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden lg:flex items-center space-x-1" aria-label="Main Navigation">
              {user?.role === 'admin' ? (
                <>
                  <Link
                    to="/admin"
                    data-testid="nav-admin-link"
                    className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                      isActive('/admin')
                        ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-bold'
                        : 'text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30'
                    }`}
                  >
                    <ShieldCheck className="h-4 w-4" />
                    <span>Admin Dashboard</span>
                  </Link>

                  <Link
                    to="/"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/')
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <span>Storefront View</span>
                  </Link>

                  <Link
                    to="/profile"
                    data-testid="nav-profile-link"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/profile')
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <UserIcon className="h-4 w-4" />
                    <span>Admin Profile</span>
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    to="/"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/')
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    Products
                  </Link>

                  <Link
                    to="/orders"
                    data-testid="nav-orders-link"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/orders')
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <span>Orders</span>
                  </Link>

                  <Link
                    to="/wishlist"
                    data-testid="nav-wishlist-link"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/wishlist')
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <Heart className={`h-4 w-4 ${wishlistCount > 0 ? 'text-rose-500 fill-rose-500' : 'text-rose-500'}`} />
                    <span>Wishlist</span>
                    {wishlistCount > 0 && (
                      <span
                        data-testid="wishlist-badge-count"
                        className="ml-1 bg-rose-500 text-white text-[10px] font-bold rounded-full h-4 min-w-[16px] px-1 flex items-center justify-center shadow-sm"
                      >
                        {wishlistCount}
                      </span>
                    )}
                  </Link>
                </>
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

            {/* Cart Link (Hidden for admin, visible for customer/guest) */}
            {user?.role !== 'admin' && (
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
            )}

            {/* Auth Actions */}
            {isAuthenticated && user ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-700">
                <Link
                  to="/profile"
                  data-testid="navbar-profile-pill"
                  title="View Account Profile"
                  className={`flex items-center gap-2 text-sm px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                    user.role === 'admin'
                      ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 hover:bg-purple-100 dark:hover:bg-purple-900/60'
                      : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <div
                    className={`h-7 w-7 rounded-full flex items-center justify-center ${
                      user.role === 'admin'
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                    }`}
                  >
                    {user.role === 'admin' ? <ShieldCheck className="h-4 w-4" /> : <UserIcon className="h-4 w-4" />}
                  </div>
                  <span className="font-semibold hidden md:inline" data-testid="navbar-username">
                    {user.username}
                  </span>
                  {user.role === 'admin' && (
                    <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/60 px-1.5 py-0.5 rounded">
                      Admin
                    </span>
                  )}
                </Link>
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
