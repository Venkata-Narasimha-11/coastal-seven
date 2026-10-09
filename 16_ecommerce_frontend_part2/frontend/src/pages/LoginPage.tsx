import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, User as UserIcon, LogIn } from 'lucide-react';
import { loginSchema, LoginFormData } from '../types/forms';
import authService from '../services/authService';
import useAuthStore from '../stores/useAuthStore';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import ErrorMessage from '../components/common/ErrorMessage';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const loginToStore = useAuthStore((state) => state.login);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      const response = await authService.login(data);
      loginToStore(response.user, response.token.access_token);
      if (response.user?.role === 'admin' || data.username === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        err.message ||
        'Failed to authenticate. Please verify your credentials.';
      setServerError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
  };

  return (
    <div className="max-w-md mx-auto py-12">
      <Card className="p-8 shadow-lg">
        <div className="text-center mb-6">
          <div className="h-12 w-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-3">
            <LogIn className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sign in to your account</h1>
          <p className="text-xs text-slate-500 mt-1">
            Admin: <span className="font-mono text-purple-600 font-semibold">admin</span> | Customer: <span className="font-mono text-blue-600 font-semibold">customer1</span>
          </p>
        </div>

        {serverError && (
          <div className="mb-6">
            <ErrorMessage
              title="Authentication Failed"
              message={serverError}
              data-testid="login-server-error"
            />
          </div>
        )}

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-5"
          data-testid="login-form"
          noValidate
        >
          <Input
            label="Username or Email"
            id="username"
            placeholder="admin"
            leftIcon={<UserIcon className="h-4 w-4" />}
            error={errors.username?.message}
            data-testid="username-input"
            {...register('username')}
          />

          <Input
            label="Password"
            id="password"
            type="password"
            placeholder="••••••••"
            leftIcon={<Lock className="h-4 w-4" />}
            error={errors.password?.message}
            data-testid="password-input"
            {...register('password')}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full mt-2"
            isLoading={isSubmitting}
            data-testid="login-submit-btn"
          >
            Sign In
          </Button>
        </form>

        {/* 1-Click Demo Login Helpers */}
        <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 space-y-2.5">
          <p className="text-xs text-center text-slate-500 font-semibold uppercase tracking-wider">
            Quick 1-Click Demo Login:
          </p>
          <div className="grid grid-cols-2 gap-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setValue('username', 'admin');
                setValue('password', 'AdminPassword123!');
              }}
              className="text-xs font-semibold text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-950/40"
            >
              👑 Fill Admin
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setValue('username', 'customer1');
                setValue('password', 'SecretPassword123!');
              }}
              className="text-xs font-semibold text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-950/40"
            >
              🛍️ Fill Customer
            </Button>
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 font-semibold hover:underline">
            Register here
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
