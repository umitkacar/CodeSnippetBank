import React, { forwardRef } from 'react';

interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  ({ label, className = '', ...props }, ref) => (
    <div className="flex items-center">
      <input
        ref={ref}
        type="radio"
        className={`h-4 w-4 border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 ${className}`}
        {...props}
      />
      {label && (
        <label className="ml-2 text-sm text-gray-700">{label}</label>
      )}
    </div>
  )
);

Radio.displayName = 'Radio';
