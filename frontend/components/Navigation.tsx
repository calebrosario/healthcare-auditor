'use client';

import React from 'react';
import Link from 'next/link';
import Button from '../components/ui/button';

export default function Navigation() {
  const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';

  const navLinks = [
    { href: '/', label: 'Dashboard', path: '/' },
    { href: '/validate', label: 'Validate Bill', path: '/validate' },
    { href: '/alerts', label: 'Alerts', path: '/alerts' },
    { href: '/investigate', label: 'Investigate', path: '/investigate' },
    { href: '/analytics', label: 'Analytics', path: '/analytics' },
    { href: '/settings', label: 'Settings', path: '/settings' },
  ];

  return React.createElement('nav', {
    className: 'bg-white border-b border-gray-200',
  }, [
    React.createElement('div', {
      className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    }, [
      React.createElement('div', {
        className: 'flex justify-between h-16',
      }, [
        React.createElement('div', {
          className: 'flex items-center',
        }, [
          React.createElement('span', {
            className: 'text-2xl font-bold text-blue-600',
          }, '🏥 Healthcare Auditor'),
        ]),

        React.createElement('div', {
          className: 'hidden md:flex space-x-8',
        }, navLinks.map(link =>
          React.createElement(Link, {
            key: link.path,
            href: link.href,
            className: `inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              currentPath === link.path
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-700 hover:bg-gray-50'
            }`,
          }, [
            React.createElement('span', null, link.label),
          ]),
        )),
      ]),
    ]),
  ]);
}
