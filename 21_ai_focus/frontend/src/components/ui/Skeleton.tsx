import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className, ...rest }) => {
  return (
    <div
      data-testid="skeleton"
      className={twMerge(
        clsx('animate-pulse rounded-md bg-slate-200/80', className)
      )}
      {...rest}
    />
  );
};

export default Skeleton;
