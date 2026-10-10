import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { BadgeProps } from '../../types/components';

const badgeVariantClasses: Record<string, string> = {
  default: 'bg-slate-100 text-slate-800 border-slate-200',
  secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
  destructive: 'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
  outline: 'text-foreground border-border',
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  danger: 'bg-rose-50 text-rose-700 border-rose-200',
  info: 'bg-sky-50 text-sky-700 border-sky-200',
};

export const badgeVariants = ({ variant = 'default', className = '' }: any = {}) => {
  return twMerge(
    clsx(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors',
      badgeVariantClasses[variant] || badgeVariantClasses.default,
      className
    )
  );
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  children,
  className,
  ...rest
}) => {
  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors',
          badgeVariantClasses[variant] || badgeVariantClasses.default,
          className
        )
      )}
      {...rest}
    >
      {children}
    </span>
  );
};

export default Badge;
