import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 24, className = '', text = '' }) => {
  return (
    <div className={`flex flex-col items-center justify-center gap-2 ${className}`}>
      <Loader2 size={size} className="animate-spin text-indigo-500" />
      {text && <p className="text-sm text-gray-400 font-medium">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
