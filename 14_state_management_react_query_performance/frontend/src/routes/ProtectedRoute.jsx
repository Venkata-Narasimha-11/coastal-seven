import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ShieldAlert } from 'lucide-react';
import { Button } from '../components/ui/button';

/**
 * ProtectedRoute Guard Component.
 * Restricts access to authenticated users and optionally checks role requirements.
 * Preserves the target route in state and query parameter so users are returned
 * to their destination upon logging in.
 */
export const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, isAuthenticated, loading, isAdmin } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center p-8">
        <LoadingSpinner text="Verifying authentication credentials..." />
      </div>
    );
  }

  // If user is not authenticated, redirect to login preserving intended target
  if (!isAuthenticated) {
    const returnUrl = encodeURIComponent(location.pathname + location.search);
    return (
      <Navigate
        to={`/login?redirect=${returnUrl}`}
        state={{ from: location }}
        replace
      />
    );
  }

  // If route is admin only and user lacks admin role
  if (adminOnly && !isAdmin) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center p-8 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <ShieldAlert className="h-8 w-8" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight">Access Restricted</h2>
        <p className="mt-2 max-w-md text-sm text-muted-foreground">
          You are currently signed in as <strong className="text-foreground">{user?.username}</strong> ({user?.role}),
          which does not possess Administrator privileges required for this area.
        </p>
        <div className="mt-6 flex gap-3">
          <Button variant="default" onClick={() => window.history.back()}>
            Go Back
          </Button>
          <Button variant="outline" onClick={() => (window.location.href = '/')}>
            Storefront
          </Button>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
