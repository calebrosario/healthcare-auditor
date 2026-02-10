'use client';

import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeStyles: Record<NonNullable<ModalProps['size']>, string> = {
  sm: 'max-w-md',
  md: 'max-w-2xl',
  lg: 'max-w-5xl',
  xl: 'max-w-7xl',
};

export default function Modal({ isOpen, onClose, title, children, size = 'lg' }: ModalProps) {
  if (!isOpen) return null;

  return React.createElement('div', {
    className: 'fixed inset-0 z-50 overflow-y-auto',
    role: 'dialog',
    'aria-modal': 'true',
  }, [
    React.createElement('div', {
      className: 'flex min-h-screen items-center justify-center p-4',
    }, [
      React.createElement('div', {
        className: 'fixed inset-0 bg-black bg-opacity-50 transition-opacity',
        onClick: onClose,
      }),
      React.createElement('div', {
        className: `relative bg-white rounded-lg shadow-xl ${sizeStyles[size]} w-full`,
        onClick: (e) => e.stopPropagation(),
      }, [
        React.createElement('div', {
          className: 'flex items-center justify-between p-6 border-b border-gray-200',
        }, [
          React.createElement('h3', {
            className: 'text-xl font-semibold text-gray-900',
          }, title),
          React.createElement('button', {
            onClick: onClose,
            className: 'text-gray-400 hover:text-gray-600 transition-colors',
            type: 'button',
          }, '✕'),
        ]),
        React.createElement('div', {
          className: 'p-6',
        }, children),
      ]),
    ]),
  ]);
}
