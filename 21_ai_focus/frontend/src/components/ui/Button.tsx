import React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ButtonProps } from '../../types/components';

const variantClasses: Record<string, string> = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm',
  default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90 active:scale-[0.98]',
  destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 active:scale-[0.98]',
  secondary: 'bg-slate-100 text-slate-800 hover:bg-slate-200 focus:ring-slate-400',
  outline: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-blue-500',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm',
  ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 focus:ring-slate-300',
  link: 'text-primary underline-offset-4 hover:underline',
  success: 'bg-emerald-600 text-white shadow hover:bg-emerald-700 active:scale-[0.98]',
};

const sizeClasses: Record<string, string> = {
  default: 'px-4 py-2 text-sm font-medium rounded-lg gap-2',
  sm: 'px-3 py-1.5 text-xs font-medium rounded-md gap-1.5',
  md: 'px-4 py-2 text-sm font-medium rounded-lg gap-2',
  lg: 'px-6 py-3 text-base font-medium rounded-lg gap-2.5',
  icon: 'h-9 w-9 p-0 inline-flex items-center justify-center',
};

export const buttonVariants = ({ variant = 'primary', size = 'md', className = '' }: any = {}) => {
  return twMerge(
    clsx(
      'inline-flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none font-medium',
      variantClasses[variant] || variantClasses.primary,
      sizeClasses[size] || sizeClasses.md,
      className
    )
  );
};

/**
 * Polymorphic Button Component.
 * Supports rendering as <button>, <a> tag, or asChild (Radix Slot) while retaining full type safety.
 */
export const Button = React.forwardRef<any, ButtonProps>(
  (
    {
      as,
      asChild = false,
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      loading,
      fullWidth = false,
      leftIcon,
      rightIcon,
      className,
      disabled,
      ...rest
    },
    ref
  ) => {
    const Component = asChild ? Slot : (as || 'button');
    const isSpinnerActive = isLoading || Boolean(loading);

    const mergedClassName = twMerge(
      clsx(
        'inline-flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none font-medium',
        variantClasses[variant] || variantClasses.primary,
        sizeClasses[size] || sizeClasses.md,
        fullWidth && 'w-full',
        className
      )
    );

    return (
      <Component
        ref={ref}
        className={mergedClassName}
        disabled={disabled || isSpinnerActive}
        aria-busy={isSpinnerActive}
        {...rest}
      >
        {isSpinnerActive && (
          <svg
            data-testid="loading-spinner"
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {!isLoading && leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="inline-flex shrink-0">{rightIcon}</span>}
      </Component>
    );
  }
);

Button.displayName = 'Button';
export default Button;
