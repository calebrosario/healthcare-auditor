'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { FraudAlert, AlertFilter } from '../../types';
import alert from '../../components/ui/alert';
import Card from '../../components/ui/card';
import Button from '../../components/ui/button';

export default function AlertsPage() {
  const [alerts, setAlerts] = React.useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = React.useState<AlertFilter>({});

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true);
        const data = await api.getAlerts(filter);
        setAlerts(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load alerts');
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, [filter]);

  const handleFilterChange = (key: keyof AlertFilter, value: string) => {
    setFilter(prev => ({ ...prev, [key]: value === '' ? undefined : value }));
  };

  const handleStatusUpdate = async (alertId: string, status: 'investigating' | 'resolved' | 'dismissed') => {
    try {
      await api.updateAlertStatus(alertId, status);
      setAlerts(prev => prev.map(alert =>
        alert.id === alertId ? { ...alert, status } : alert
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update alert status');
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter.status && !filter.status.includes(alert.status)) return false;
    if (filter.risk_level && !filter.risk_level.includes(alert.risk_level)) return false;
    if (filter.provider_id && alert.provider_id !== filter.provider_id) return false;
    if (filter.date_from && new Date(alert.created_at) < new Date(filter.date_from)) return false;
    if (filter.date_to && new Date(alert.created_at) > new Date(filter.date_to)) return false;
    return true;
  });

  return React.createElement('div', {
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
        }, 'Fraud Alerts'),

        error && React.createElement(alert, {
          variant: 'error',
          children: error,
        }),

        React.createElement(Card, {
          title: 'Filters',
          children: React.createElement('div', {
            className: 'grid grid-cols-1 md:grid-cols-4 gap-4',
          }, [
            React.createElement('div', null, [
              React.createElement('label', {
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Status'),
              React.createElement('select', {
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                value: filter.status || '',
                onChange: (e) => handleFilterChange('status', e.target.value),
              }, [
                React.createElement('option', {
                  value: '',
                }, 'All'),
                React.createElement('option', {
                  value: 'open',
                }, 'Open'),
                React.createElement('option', {
                  value: 'investigating',
                }, 'Investigating'),
                React.createElement('option', {
                  value: 'resolved',
                }, 'Resolved'),
                React.createElement('option', {
                  value: 'dismissed',
                }, 'Dismissed'),
              ]),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Risk Level'),
              React.createElement('select', {
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                value: filter.risk_level || '',
                onChange: (e) => handleFilterChange('risk_level', e.target.value),
              }, [
                React.createElement('option', {
                  value: '',
                }, 'All'),
                React.createElement('option', {
                  value: 'high',
                }, 'High'),
                React.createElement('option', {
                  value: 'medium',
                }, 'Medium'),
                React.createElement('option', {
                  value: 'low',
                }, 'Low'),
              ]),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Date Range'),
              React.createElement('input', {
                type: 'date',
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                value: filter.date_from || '',
                onChange: (e) => handleFilterChange('date_from', e.target.value),
              }),
              React.createElement('span', {
                className: 'mx-2',
              }, 'to'),
              React.createElement('input', {
                type: 'date',
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                value: filter.date_to || '',
                onChange: (e) => handleFilterChange('date_to', e.target.value),
              }),
            ]),

            Object.keys(filter).length > 0 && React.createElement(Button, {
              fullWidth: true,
              onClick: () => setFilter({}),
              children: 'Clear Filters',
            }),
          ]),
        ]),
      ]),

      loading ? (
        React.createElement('div', {
          className: 'flex items-center justify-center py-12',
        }, 'Loading alerts...')
      ) : (
        React.createElement('div', {
          className: 'space-y-4',
        }, [
          filteredAlerts.length === 0 ? (
            React.createElement('div', {
              className: 'text-center py-12 text-gray-500',
            }, 'No alerts found matching your filters.')
          ) : (
            filteredAlerts.map(alert =>
              React.createElement(Card, {
                key: alert.id,
                title: React.createElement('div', {
                  className: 'flex items-center justify-between mb-2',
                }, [
                  React.createElement('div', null, [
                    React.createElement('span', {
                      className: 'font-semibold',
                    }, alert.claim_id),
                    React.createElement('span', {
                      className: `ml-2 px-2 py-1 rounded text-sm font-medium ${
                        alert.risk_level === 'high' ? 'bg-red-600 text-white' :
                        alert.risk_level === 'medium' ? 'bg-yellow-600 text-white' :
                        'bg-green-600 text-white'
                      }`,
                    }, alert.risk_level.toUpperCase()),
                  ]),
                  React.createElement('span', {
                    className: 'text-sm text-gray-500',
                  }, new Date(alert.created_at).toLocaleString()),
                ]),
              }),
              React.createElement('div', {
                className: 'grid grid-cols-2 gap-4 mb-4',
              }, [
                React.createElement('div', null, [
                  React.createElement('div', {
                    className: 'text-sm text-gray-600 mb-1',
                  }, 'Composite Score:'),
                  React.createElement('div', {
                    className: 'text-2xl font-bold text-gray-900',
                  }, alert.composite_score.toFixed(2)),
                ]),
                React.createElement('div', null, [
                  React.createElement('div', {
                    className: 'text-sm text-gray-600 mb-1',
                  }, 'ML Probability:'),
                  React.createElement('div', {
                    className: 'text-2xl font-bold text-red-600',
                  }, `${(alert.ml_fraud_probability * 100).toFixed(1)}%`),
                ]),
              ]),
              React.createElement('div', {
                className: 'border-t pt-4',
              }, [
                React.createElement('div', {
                  className: 'text-sm text-gray-600 mb-2',
                }, 'Triggered Rules:'),
                React.createElement('div', {
                  className: 'flex flex-wrap gap-2',
                }, alert.triggered_rules.slice(0, 3).map(rule =>
                  React.createElement('span', {
                    key: rule,
                    className: 'px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm',
                  }, rule),
                ),
                alert.triggered_rules.length > 3 && React.createElement('span', {
                  className: 'text-sm text-gray-500',
                }, `+${alert.triggered_rules.length - 3} more`),
              ]),

              alert.status === 'open' && React.createElement('div', {
                className: 'flex gap-2 border-t pt-4',
              }, [
                React.createElement(Button, {
                  onClick: () => handleStatusUpdate(alert.id, 'investigating'),
                  variant: 'secondary',
                  children: 'Investigate',
                }),
                React.createElement(Button, {
                  onClick: () => handleStatusUpdate(alert.id, 'dismissed'),
                  variant: 'danger',
                  children: 'Dismiss',
                }),
              ]),

              alert.status === 'investigating' && React.createElement('div', {
                className: 'border-t pt-4',
              }, [
                React.createElement(Button, {
                  onClick: () => handleStatusUpdate(alert.id, 'resolved'),
                  variant: 'success',
                  fullWidth: true,
                  children: 'Mark as Resolved',
                }),
              ]),

              alert.status === 'resolved' && React.createElement('div', {
                className: 'border-t pt-4',
              }, [
                React.createElement(Button, {
                  onClick: () => handleStatusUpdate(alert.id, 'investigating'),
                  variant: 'secondary',
                  fullWidth: true,
                  children: 'Reopen Investigation',
                }),
              ]),
            ]),
          ),
        ]),
      ]),
    ])
  );
}
