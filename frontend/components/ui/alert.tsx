'use client';

import React from 'react';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  children: React.ReactNode;
  variant?: AlertVariant;
  onClose?: () => void;
  className?: string;
}

const alertStyles: Record<AlertVariant, string> = {
  info: 'bg-blue-50 border-blue-500 text-blue-700',
  success: 'bg-green-50 border-green-500 text-green-700',
  warning: 'bg-yellow-50 border-yellow-500 text-yellow-700',
  error: 'bg-red-50 border-red-500 text-red-700',
};

const iconMap: Record<AlertVariant, string> = {
  info: '',
  success: '',
  warning: '',
  error: '',
};

export default function Alert({ children, variant = 'info', onClose, className = '' }: AlertProps) {
  return React.createElement('div', {
    className: `p-4 rounded-lg border-l-4 mb-4 ${alertStyles[variant]} ${className}`,
    role: 'alert',
  }, [
    React.createElement('div', {
      className: 'flex items-start',
    }, [
      React.createElement('div', {
        className: 'flex-shrink-0',
      }, iconMap[variant]),
      React.createElement('div', {
        className: 'ml-3 flex-1',
      }, [
        children,
        onClose && React.createElement('button', {
          onClick: onClose,
          className: 'ml-4 text-sm underline hover:opacity-75',
          type: 'button',
        }, 'Dismiss'),
      ]),
    ]),
  ]);
}
