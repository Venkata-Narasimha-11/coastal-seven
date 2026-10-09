import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  text?: string;
  className?: string;
}

const sizeMap = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-3',
  lg: 'h-12 w-12 border-4',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  label = 'Loading...',
  text,
  className = '',
}) => {
  const displayText = text || label;
  return (
    <div
      role="status"
      aria-label={displayText}
      className={`inline-flex flex-col items-center justify-center gap-2 ${className}`}
    >
      <div
        className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizeMap[size]}`}
      />
      {text ? (
        <span className="text-sm text-slate-500 dark:text-slate-400">{text}</span>
      ) : label ? (
        <span className="sr-only">{label}</span>
      ) : null}
    </div>
  );
};

export default LoadingSpinner;
