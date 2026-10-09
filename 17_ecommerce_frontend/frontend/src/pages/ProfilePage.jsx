import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { User, Mail, Shield, KeyRound, LogOut, CheckCircle, Calendar, Hash } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export const ProfilePage = () => {
  const { user, token, logout, isAdmin } = useAuth();

  const handleLogout = () => {
    logout();
    toast.info('Signed Out', { description: 'You have been successfully logged out.' });
  };

  // Extract JWT payload info if token exists
  let tokenClaims = null;
  if (token) {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        tokenClaims = JSON.parse(atob(parts[1]));
      }
    } catch (e) {
      console.error('Failed to parse token payload:', e);
    }
  }

  return (
    <div className="container max-w-4xl py-10 px-4 space-y-8 animate-in fade-in-50 duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">User Account Profile</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Authenticated via FastAPI JWT Bearer Tokens & protected route guard
          </p>
        </div>
        <Button variant="destructive" onClick={handleLogout} className="flex items-center gap-2">
          <LogOut className="h-4 w-4" /> Sign Out
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Account Snapshot */}
        <Card className="md:col-span-1 shadow-sm">
          <CardHeader className="text-center pb-4">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary mb-3">
              <User className="h-10 w-10" />
            </div>
            <CardTitle className="text-xl font-bold">{user?.full_name || user?.username}</CardTitle>
            <CardDescription className="text-xs">@{user?.username}</CardDescription>
            <div className="pt-2">
              <Badge variant={isAdmin ? "default" : "secondary"} className="uppercase text-[10px] tracking-wider font-semibold">
                <Shield className="h-3 w-3 mr-1" />
                {user?.role || 'Customer'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-xs border-t pt-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Account Status</span>
              <span className="flex items-center text-emerald-600 dark:text-emerald-400 font-medium">
                <CheckCircle className="h-3.5 w-3.5 mr-1" /> Active
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">User ID</span>
              <span className="font-mono font-medium">#{user?.id || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Joined On</span>
              <span className="text-muted-foreground font-mono">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Account Details & JWT Diagnostics */}
        <div className="md:col-span-2 space-y-6">
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Mail className="h-5 w-5 text-primary" /> Profile Information
              </CardTitle>
              <CardDescription className="text-xs">
                Verified records retrieved via Axios Interceptor (`GET /api/v1/auth/me`)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3 bg-muted/40 rounded-lg border">
                  <span className="text-xs text-muted-foreground block">Username</span>
                  <span className="font-semibold text-foreground">{user?.username}</span>
                </div>
                <div className="p-3 bg-muted/40 rounded-lg border">
                  <span className="text-xs text-muted-foreground block">Email Address</span>
                  <span className="font-semibold text-foreground">{user?.email}</span>
                </div>
                <div className="p-3 bg-muted/40 rounded-lg border">
                  <span className="text-xs text-muted-foreground block">Full Legal Name</span>
                  <span className="font-semibold text-foreground">{user?.full_name || 'Not provided'}</span>
                </div>
                <div className="p-3 bg-muted/40 rounded-lg border">
                  <span className="text-xs text-muted-foreground block">Assigned Role</span>
                  <span className="font-semibold text-foreground uppercase">{user?.role}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* JWT Token Diagnostic Inspector */}
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <KeyRound className="h-5 w-5 text-amber-500" /> Active JWT Bearer Token Inspection
              </CardTitle>
              <CardDescription className="text-xs">
                Token stored in localStorage and automatically injected by Axios Request Interceptor
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div>
                <span className="font-medium text-muted-foreground block mb-1">Decoded Token Claims:</span>
                <pre className="p-3 bg-muted/80 rounded-lg font-mono text-[11px] overflow-x-auto text-primary">
                  {JSON.stringify(tokenClaims || { status: 'Unable to parse token' }, null, 2)}
                </pre>
              </div>

              <div>
                <span className="font-medium text-muted-foreground block mb-1">Raw Bearer Header Preview:</span>
                <code className="p-2 block bg-muted/50 rounded font-mono text-[11px] truncate text-muted-foreground">
                  Authorization: Bearer {token ? `${token.substring(0, 30)}...${token.slice(-15)}` : 'None'}
                </code>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
