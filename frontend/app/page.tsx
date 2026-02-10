'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import { DashboardStats } from '../types';
import Alert from '../components/ui/alert';
import Card from '../components/ui/card';

export default function Home() {
  const [stats, setStats] = React.useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await api.getDashboardStats();
        setStats(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    React.createElement('div', {
      className: 'min-h-screen bg-gray-50',
    }, [
      React.createElement('div', {
        className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8',
      }, [
        React.createElement('header', {
          className: 'mb-8',
        }, [
          React.createElement('h1', {
            className: 'text-3xl font-bold text-gray-900',
          }, 'Healthcare Auditor Dashboard'),
          React.createElement('p', {
            className: 'text-gray-600 mt-2',
          }, 'Healthcare billing fraud detection and compliance verification'),
        ]),

        error && React.createElement(Alert, {
          variant: 'error',
          children: error,
        }),

        loading ? (
          React.createElement('div', {
            className: 'flex items-center justify-center py-12',
          }, 'Loading dashboard...')
        ) : stats && (
          React.createElement('div', {
            className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
          }, [
            React.createElement(Card, {
              title: 'Overview',
              children: React.createElement('div', {
                className: 'space-y-4',
              }, [
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Total Bills'),
                  React.createElement('span', {
                    className: 'text-3xl font-bold text-gray-900',
                  }, stats.total_bills.toString()),
                ]),
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Fraud Detected'),
                  React.createElement('span', {
                    className: `text-3xl font-bold ${stats.fraud_detected > 0 ? 'text-red-600' : 'text-green-600'}`,
                  }, stats.fraud_detected.toString()),
                ]),
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Fraud Rate'),
                  React.createElement('span', {
                    className: `text-3xl font-bold ${stats.fraud_rate > 0.05 ? 'text-red-600' : 'text-green-600'}`,
                  }, `${(stats.fraud_rate * 100).toFixed(2)}%`),
                ]),
              ]),
            }),

            React.createElement(Card, {
              title: 'Alerts',
              children: React.createElement('div', {
                className: 'space-y-4',
              }, [
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'New Today'),
                  React.createElement('span', {
                    className: 'text-3xl font-bold text-gray-900',
                  }, stats.alerts_today.toString()),
                ]),
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'This Week'),
                  React.createElement('span', {
                    className: 'text-3xl font-bold text-gray-900',
                  }, stats.alerts_week.toString()),
                ]),
              ]),
            }),

            React.createElement(Card, {
              title: 'Active Investigations',
              children: React.createElement('div', {
                className: 'space-y-4',
              }, [
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Active'),
                  React.createElement('span', {
                    className: 'text-3xl font-bold text-gray-900',
                  }, stats.active_investigations.toString()),
                ]),
                React.createElement('div', {
                  className: 'flex items-center justify-between',
                }, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Avg Validation Time'),
                  React.createElement('span', {
                    className: 'text-3xl font-bold text-gray-900',
                  }, `${stats.avg_validation_time.toFixed(0)}ms`),
                ]),
              ]),
            }),

            React.createElement(Card, {
              title: 'Quick Actions',
              children: React.createElement('div', {
                className: 'space-y-3',
              }, [
                React.createElement(Link, {
                  href: '/validate',
                  className: 'block w-full',
                }, React.createElement('button', {
                  className: 'w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors',
                  type: 'button',
                }, 'Validate New Bill')),
                React.createElement(Link, {
                  href: '/alerts',
                  className: 'block w-full',
                }, React.createElement('button', {
                  className: 'w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors',
                  type: 'button',
                }, 'View All Alerts')),
                React.createElement(Link, {
                  href: '/analytics',
                  className: 'block w-full',
                }, React.createElement('button', {
                  className: 'w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors',
                  type: 'button',
                }, 'View Analytics')),
              ]),
              footer: React.createElement('div', {
                className: 'text-center text-sm text-gray-500',
              }, 'Last updated: ' + new Date().toLocaleString()),
            }),
          ])
        ),
      ])
    ])
  );
}
