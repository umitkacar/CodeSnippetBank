import React from 'react';

interface AvatarProps {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Avatar = ({ src, alt = 'Avatar', fallback = 'U', size = 'md' }: AvatarProps) => {
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
  };

  return (
    <div className={`inline-flex items-center justify-center overflow-hidden rounded-full bg-gray-200 ${sizes[size]}`}>
      {src ? (
        <img src={src} alt={alt} className="h-full w-full object-cover" />
      ) : (
        <span className="font-medium text-gray-600">{fallback}</span>
      )}
    </div>
  );
};
