import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User as UserIcon, UserPlus } from 'lucide-react';
import { registerSchema, RegisterFormData } from '../types/forms';
import authService from '../services/authService';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import ErrorMessage from '../components/common/ErrorMessage';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    try {
      await authService.register(data);
      navigate('/login?registered=true');
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        err.message ||
        'Failed to register account.';
      setServerError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
  };

  return (
    <div className="max-w-md mx-auto py-12">
      <Card className="p-8 shadow-lg">
        <div className="text-center mb-8">
          <div className="h-12 w-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-3">
            <UserPlus className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Create a new account</h1>
          <p className="text-sm text-slate-500 mt-1">
            Experience type-safe React client-side validation
          </p>
        </div>

        {serverError && (
          <div className="mb-6">
            <ErrorMessage
              title="Registration Error"
              message={serverError}
              data-testid="register-server-error"
            />
          </div>
        )}

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-4"
          data-testid="register-form"
          noValidate
        >
          <Input
            label="Username"
            id="reg-username"
            placeholder="johndoe"
            leftIcon={<UserIcon className="h-4 w-4" />}
            error={errors.username?.message}
            data-testid="register-username-input"
            {...register('username')}
          />

          <Input
            label="Email Address"
            id="reg-email"
            type="email"
            placeholder="john@example.com"
            leftIcon={<Mail className="h-4 w-4" />}
            error={errors.email?.message}
            data-testid="register-email-input"
            {...register('email')}
          />

          <Input
            label="Password"
            id="reg-password"
            type="password"
            placeholder="Minimum 8 characters"
            leftIcon={<Lock className="h-4 w-4" />}
            error={errors.password?.message}
            data-testid="register-password-input"
            {...register('password')}
          />

          <Input
            label="Confirm Password"
            id="reg-confirm-password"
            type="password"
            placeholder="Re-type your password"
            leftIcon={<Lock className="h-4 w-4" />}
            error={errors.confirmPassword?.message}
            data-testid="register-confirm-password-input"
            {...register('confirmPassword')}
          />

          <div className="space-y-1.5 pt-1">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
              Account Role / Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="flex items-center gap-2 p-2.5 border rounded-lg cursor-pointer transition-colors hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-medium">
                <input
                  type="radio"
                  value="customer"
                  defaultChecked
                  {...register('role')}
                  className="text-pink-600 focus:ring-pink-500"
                />
                <span>Customer</span>
              </label>
              <label className="flex items-center gap-2 p-2.5 border rounded-lg cursor-pointer transition-colors hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-medium">
                <input
                  type="radio"
                  value="admin"
                  {...register('role')}
                  className="text-purple-600 focus:ring-purple-500"
                />
                <span className="font-bold text-purple-600 dark:text-purple-400">Store Admin</span>
              </label>
            </div>
            <p className="text-[11px] text-slate-400">
              Choose <strong>Store Admin</strong> or username <code>admin</code> for full dashboard access.
            </p>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full mt-4"
            isLoading={isSubmitting}
            data-testid="register-submit-btn"
          >
            Create Account
          </Button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-500">
          Already registered?{' '}
          <Link to="/login" className="text-blue-600 font-semibold hover:underline">
            Sign In here
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default RegisterPage;
