'use client';

import React from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success';

export interface ButtonProps {
  variant?: ButtonVariant;
  isLoading?: boolean;
  fullWidth?: boolean;
  className?: string;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}

export default function Button({
  variant = 'primary',
  isLoading = false,
  fullWidth = false,
  className = '',
  children = '',
  disabled,
  onClick,
}: ButtonProps) {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles: Record<ButtonVariant, string> = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
  };

  return React.createElement('button', {
    className: `${baseStyles} ${variantStyles[variant]} ${fullWidth ? 'w-full' : ''} ${className}`,
    disabled: disabled || isLoading,
    onClick,
  }, isLoading ? (
    React.createElement('svg', {
      className: 'animate-spin h-5 w-5 inline',
      fill: 'none',
      viewBox: '0 0 24 24',
    }, [
      React.createElement('circle', {
        className: 'opacity-25',
        cx: '12',
        cy: '12',
        r: '10',
        stroke: 'currentColor',
        strokeWidth: '4',
      }),
      React.createElement('path', {
        className: 'opacity-75',
        fill: 'currentColor',
        d: 'M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 5.291V17h4V5.291z',
      }),
    ])
  ) : (
    children
  ));
}
