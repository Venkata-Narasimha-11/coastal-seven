import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import {
  CardProps,
  CardHeaderProps,
  CardTitleProps,
  CardDescriptionProps,
  CardContentProps,
  CardFooterProps,
} from '../../types/components';

export const CardRoot = React.forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, ...rest }, ref) => (
    <div
      ref={ref}
      className={twMerge(
        clsx(
          'bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden transition-shadow duration-200 hover:shadow-md',
          className
        )
      )}
      {...rest}
    >
      {children}
    </div>
  )
);
CardRoot.displayName = 'Card';

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className, ...rest }, ref) => (
    <div
      ref={ref}
      className={twMerge(clsx('px-6 py-4 border-b border-slate-100 flex items-center justify-between', className))}
      {...rest}
    >
      {children}
    </div>
  )
);
CardHeader.displayName = 'CardHeader';

export const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ children, className, ...rest }, ref) => (
    <h3
      ref={ref}
      className={twMerge(clsx('text-base font-semibold text-slate-900', className))}
      {...rest}
    >
      {children}
    </h3>
  )
);
CardTitle.displayName = 'CardTitle';

export const CardDescription = React.forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ children, className, ...rest }, ref) => (
    <p
      ref={ref}
      className={twMerge(clsx('text-sm text-slate-500', className))}
      {...rest}
    >
      {children}
    </p>
  )
);
CardDescription.displayName = 'CardDescription';

export const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ children, className, ...rest }, ref) => (
    <div ref={ref} className={twMerge(clsx('p-6', className))} {...rest}>
      {children}
    </div>
  )
);
CardContent.displayName = 'CardContent';

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, className, ...rest }, ref) => (
    <div
      ref={ref}
      className={twMerge(clsx('px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center', className))}
      {...rest}
    >
      {children}
    </div>
  )
);
CardFooter.displayName = 'CardFooter';

export const Card = Object.assign(CardRoot, {
  Header: CardHeader,
  Title: CardTitle,
  Description: CardDescription,
  Content: CardContent,
  Footer: CardFooter,
});

export default Card;
