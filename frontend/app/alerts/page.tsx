'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { FraudAlert, AlertFilter } from '@/types';
import Alert from '@/components/ui/alert';
import Card from '@/components/ui/card';
import Button from '@/components/ui/button';

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
    setFilter((prev) => ({ ...prev, [key]: value === '' ? undefined : value }));
  };

  const handleStatusUpdate = async (alertId: string, status: 'investigating' | 'resolved' | 'dismissed') => {
    try {
      await api.updateAlertStatus(alertId, status);
      setAlerts((prev) => prev.map((alert) => (alert.id === alertId ? { ...alert, status } : alert)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update alert status');
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (filter.status && !filter.status.includes(alert.status)) return false;
    if (filter.risk_level && !filter.risk_level.includes(alert.risk_level)) return false;
    // provider_id doesn't exist on FraudAlert - skip this filter
    // if (filter.provider_id && alert.provider_id !== filter.provider_id) return false;
    if (filter.date_from && new Date(alert.created_at) < new Date(filter.date_from)) return false;
    if (filter.date_to && new Date(alert.created_at) > new Date(filter.date_to)) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Fraud Alerts</h1>

          {error && <Alert variant="error">{error}</Alert>}

          <Card title="Filters">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={filter.status || ''}
                  onChange={(e) => handleFilterChange('status', e.currentTarget.value)}
                >
                  <option value="">All</option>
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="resolved">Resolved</option>
                  <option value="dismissed">Dismissed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={filter.risk_level || ''}
                  onChange={(e) => handleFilterChange('risk_level', e.currentTarget.value)}
                >
                  <option value="">All</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={filter.date_from || ''}
                  onChange={(e) => handleFilterChange('date_from', e.currentTarget.value)}
                />
                <span className="mx-2">to</span>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={filter.date_to || ''}
                  onChange={(e) => handleFilterChange('date_to', e.currentTarget.value)}
                />
              </div>

              {Object.keys(filter).length > 0 && (
                <Button fullWidth onClick={() => setFilter({})}>
                  Clear Filters
                </Button>
              )}
            </div>
          </Card>
        </header>

        {loading ? (
          <div className="flex items-center justify-center py-12">Loading alerts...</div>
        ) : (
          <div className="space-y-4">
            {filteredAlerts.length === 0 ? (
              <div className="text-center py-12 text-gray-500">No alerts found matching your filters.</div>
            ) : (
              filteredAlerts.map((alert) => (
                <Card key={alert.id} title={alert.claim_id}>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                          alert.risk_level === 'high'
                            ? 'bg-red-600 text-white'
                            : alert.risk_level === 'medium'
                              ? 'bg-yellow-600 text-white'
                              : 'bg-green-600 text-white'
                        }`}
                      >
                        {alert.risk_level.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">{new Date(alert.created_at).toLocaleString()}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Composite Score:</div>
                        <div className="text-2xl font-bold text-gray-900">{alert.composite_score.toFixed(2)}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">ML Probability:</div>
                        <div className="text-2xl font-bold text-red-600">
                          {(alert.ml_fraud_probability * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div className="border-t pt-4">
                      <div className="text-sm text-gray-600 mb-2">Triggered Rules:</div>
                      <div className="flex flex-wrap gap-2">
                        {alert.triggered_rules.slice(0, 3).map((rule: string) => (
                          <span key={rule} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                            {rule}
                          </span>
                        ))}
                        {alert.triggered_rules.length > 3 && (
                          <span className="text-sm text-gray-500">+{alert.triggered_rules.length - 3} more</span>
                        )}
                      </div>

                      {alert.status === 'open' && (
                        <div className="flex gap-2 border-t pt-4">
                          <Button variant="secondary" onClick={() => handleStatusUpdate(alert.id, 'investigating')}>
                            Investigate
                          </Button>
                          <Button variant="danger" onClick={() => handleStatusUpdate(alert.id, 'dismissed')}>
                            Dismiss
                          </Button>
                        </div>
                      )}

                      {alert.status === 'investigating' && (
                        <div className="border-t pt-4">
                          <Button variant="success" fullWidth onClick={() => handleStatusUpdate(alert.id, 'resolved')}>
                            Mark as Resolved
                          </Button>
                        </div>
                      )}

                      {alert.status === 'resolved' && (
                        <div className="border-t pt-4">
                          <Button
                            variant="secondary"
                            fullWidth
                            onClick={() => handleStatusUpdate(alert.id, 'investigating')}
                          >
                            Reopen Investigation
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
