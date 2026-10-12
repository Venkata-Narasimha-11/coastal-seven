import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import Button from '../ui/Button';

interface ErrorMessageProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  className = '',
  ...rest
}) => {
  return (
    <div
      role="alert"
      className={`rounded-lg bg-rose-50 border border-rose-200 p-4 text-rose-800 ${className}`}
      {...rest}
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold">{title}</h4>
          <p className="mt-1 text-sm text-rose-700">{message}</p>
          {onRetry && (
            <div className="mt-3">
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
                className="bg-white border-rose-300 text-rose-800 hover:bg-rose-100"
              >
                Try Again
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
