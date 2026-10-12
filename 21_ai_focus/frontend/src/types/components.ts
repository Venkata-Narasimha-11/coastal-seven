import React from 'react';

/**
 * Component-level type definitions demonstrating TypeScript in React.
 */

// Button Variants and Sizes
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost' | 'default' | 'destructive' | 'link' | 'success';
export type ButtonSize = 'sm' | 'md' | 'lg' | 'default' | 'icon';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  as?: React.ElementType;
  asChild?: boolean;
  href?: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  target?: string;
  rel?: string;
}

// Badge Variants
export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'secondary' | 'destructive' | 'outline';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

// Input Component Props
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
}

// Generic List Props (Demonstrating TypeScript Generics in React)
export interface GenericListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string | number;
  emptyMessage?: string;
  className?: string;
  listClassName?: string;
}

// Card Compound Component Props
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  className?: string;
}

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children?: React.ReactNode;
  className?: string;
}

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

// Discriminated Union for Alert Banner
export type AlertState =
  | { status: 'idle' }
  | { status: 'loading'; progress?: number }
  | { status: 'success'; message: string; timestamp: string }
  | { status: 'error'; message: string; errorCode: number };
