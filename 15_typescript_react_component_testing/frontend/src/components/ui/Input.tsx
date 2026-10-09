import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { InputProps } from '../../types/components';

/**
 * ForwardRef Input Component with accessibility labels and error states.
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, id, className, disabled, ...rest }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);
    const errorId = inputId ? `${inputId}-error` : undefined;
    const helperId = inputId ? `${inputId}-helper` : undefined;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-slate-700 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative rounded-md shadow-sm">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? errorId : helperText ? helperId : undefined}
            className={twMerge(
              clsx(
                'block w-full rounded-lg border text-sm transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-offset-1',
                leftIcon ? 'pl-10' : 'pl-3',
                'pr-3 py-2',
                error
                  ? 'border-red-500 text-red-900 focus:border-red-500 focus:ring-red-400 bg-red-50/20'
                  : 'border-slate-300 text-slate-900 focus:border-blue-500 focus:ring-blue-400 bg-white',
                disabled && 'bg-slate-100 text-slate-400 cursor-not-allowed',
                className
              )
            )}
            {...rest}
          />
        </div>
        {error && (
          <p id={errorId} className="mt-1 text-xs text-red-600 font-medium" role="alert">
            {error}
          </p>
        )}
        {!error && helperText && (
          <p id={helperId} className="mt-1 text-xs text-slate-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
