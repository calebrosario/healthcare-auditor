'use client';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  footer?: React.ReactNode;
}

export default function Card({ children, className = '', title, footer }: CardProps) {
  return React.createElement('div', {
    className: `bg-white rounded-lg shadow-md border border-gray-200 ${className}`,
  }, [
    title && React.createElement('div', {
      className: 'px-6 py-4 border-b border-gray-200',
    }, React.createElement('h3', {
      className: 'text-lg font-semibold text-gray-900',
    }, title)),
    React.createElement('div', {
      className: 'px-6 py-4',
    }, children),
    footer && React.createElement('div', {
      className: 'px-6 py-4 bg-gray-50 rounded-b-lg border-t border-gray-200',
    }, footer),
  ]);
}
