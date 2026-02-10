'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Settings } from '../../types';
import Card from '../../components/ui/card';

export default function SettingsPage() {
  const [settings, setSettings] = React.useState<Settings>({
    ml_threshold_low: 0.7,
    ml_threshold_high: 0.85,
    anomaly_sensitivity: 'medium',
    risk_weights: {
      anomaly_score: 30,
      ml_probability: 40,
      code_violations: 20,
      network_centrality: 10,
    },
    notification_preferences: {
      email_alerts: true,
      sms_alerts: false,
      slack_webhook: '',
      alert_threshold: 'medium',
    },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await api.getSettings();
        setSettings(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const updatedSettings = await api.updateSettings(settings);
      setSettings(prev => ({ ...prev, ...updatedSettings }));
      setSuccess(true);

      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      await api.updateSettings({
        ml_threshold_low: 0.7,
        ml_threshold_high: 0.85,
        anomaly_sensitivity: 'medium',
        risk_weights: {
          anomaly_score: 30,
          ml_probability: 40,
          code_violations: 20,
          network_centrality: 10,
        },
        notification_preferences: {
          email_alerts: true,
          sms_alerts: false,
          slack_webhook: '',
          alert_threshold: 'medium',
        },
      });
      setSettings(prev => ({
        ...prev,
        ml_threshold_low: 0.7,
        ml_threshold_high: 0.85,
        anomaly_sensitivity: 'medium',
        risk_weights: {
          anomaly_score: 30,
          ml_probability: 40,
          code_violations: 20,
          network_centrality: 10,
        },
        notification_preferences: {
          email_alerts: true,
          sms_alerts: false,
          slack_webhook: '',
          alert_threshold: 'medium',
        },
      }));
      setSuccess(true);

      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset settings');
      setLoading(false);
    }
  };

  return React.createElement('div', {
    className: 'min-h-screen bg-gray-50',
  }, [
    React.createElement('div', {
      className: 'max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8',
    }, [
      React.createElement('header', {
        className: 'mb-8',
      }, [
        React.createElement('h1', {
          className: 'text-3xl font-bold text-gray-900',
        }, 'Settings'),
      ]),

      error && React.createElement('div', {
        className: 'mb-4',
      }, error),

      loading && React.createElement('div', {
        className: 'flex items-center justify-center py-12',
      }, 'Loading...'),
      }),

      success && React.createElement('div', {
        className: 'mb-4',
      }, React.createElement('div', {
        className: 'bg-green-50 border-green-500 text-green-700 p-4 rounded-lg',
      }, 'Settings saved successfully!'),
      ]),

      !loading && React.createElement('div', {
        className: 'space-y-6',
      }, [
        React.createElement(Card, {
          title: 'ML Detection Thresholds',
          children: React.createElement('div', {
            className: 'space-y-4',
          }, [
            React.createElement('label', {
              htmlFor: 'ml_threshold_low',
              className: 'block text-sm font-medium text-gray-700 mb-2',
            }, 'Low Fraud Probability Threshold (%)'),
            React.createElement('input', {
              type: 'number',
              id: 'ml_threshold_low',
              value: settings.ml_threshold_low,
              min: '0',
              max: '1',
              step: '0.01',
              className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              onChange: (e) => setSettings(prev => ({ ...prev, ml_threshold_low: parseFloat(e.target.value) })),
            }),

            React.createElement('label', {
              htmlFor: 'ml_threshold_high',
              className: 'block text-sm font-medium text-gray-700 mb-2',
            }, 'High Fraud Probability Threshold (%)'),
            React.createElement('input', {
              type: 'number',
              id: 'ml_threshold_high',
              value: settings.ml_threshold_high,
              min: '0',
              max: '1',
              step: '0.01',
              className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              onChange: (e) => setSettings(prev => ({ ...prev, ml_threshold_high: parseFloat(e.target.value) })),
            }),

            React.createElement('label', {
              htmlFor: 'anomaly_sensitivity',
              className: 'block text-sm font-medium text-gray-700 mb-2',
            }, 'Anomaly Detection Sensitivity'),
            React.createElement('select', {
              id: 'anomaly_sensitivity',
              value: settings.anomaly_sensitivity,
              className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              onChange: (e) => setSettings(prev => ({ ...prev, anomaly_sensitivity: e.target.value as 'low' | 'medium' | 'high' })),
              }, [
              React.createElement('option', {
                value: 'low',
              }, 'Low'),
              React.createElement('option', {
                value: 'medium',
              }, 'Medium'),
              React.createElement('option', {
                value: 'high',
              }, 'High'),
              ]),
            ]),

            React.createElement(Card, {
              title: 'Risk Scoring Weights',
              children: React.createElement('div', {
                className: 'space-y-4',
              }, [
                React.createElement('div', null, [
                  React.createElement('label', {
                    htmlFor: 'anomaly_score',
                    className: 'block text-sm font-medium text-gray-700 mb-2',
                  }, 'Anomaly Score Weight (%)'),
                  React.createElement('input', {
                    type: 'number',
                    id: 'anomaly_score',
                    value: settings.risk_weights.anomaly_score,
                    min: '0',
                    max: '100',
                    step: '1',
                    className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    onChange: (e) => setSettings(prev => ({ ...prev, risk_weights: { ...prev.risk_weights, anomaly_score: parseFloat(e.target.value) })),
                  }),

                  React.createElement('label', {
                    htmlFor: 'ml_probability',
                    className: 'block text-sm font-medium text-gray-700 mb-2',
                  }, 'ML Probability Weight (%)'),
                  React.createElement('input', {
                    type: 'number',
                    id: 'ml_probability',
                    value: settings.risk_weights.ml_probability,
                    min: '0',
                    max: '100',
                    step: '1',
                    className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    onChange: (e) => setSettings(prev => ({ ...prev, risk_weights: { ...prev.risk_weights, ml_probability: parseFloat(e.target.value) })),
                  }),

                  React.createElement('label', {
                    htmlFor: 'code_violations',
                    className: 'block text-sm font-medium text-gray-700 mb-2',
                  }, 'Code Violations Weight (%)'),
                  React.createElement('input', {
                    type: 'number',
                    id: 'code_violations',
                    value: settings.risk_weights.code_violations,
                    min: '0',
                    max: '100',
                    step: '1',
                    className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    onChange: (e) => setSettings(prev => ({ ...prev, risk_weights: { ...prev.risk_weights, code_violations: parseFloat(e.target.value) })),
                  }),

                  React.createElement('label', {
                    htmlFor: 'network_centrality',
                    className: 'block text-sm font-medium text-gray-700 mb-2',
                  }, 'Network Centrality Weight (%)'),
                  React.createElement('input', {
                    type: 'number',
                    id: 'network_centrality',
                    value: settings.risk_weights.network_centrality,
                    min: '0',
                    max: '100',
                    step: '1',
                    className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    onChange: (e) => setSettings(prev => ({ ...prev, risk_weights: { ...prev.risk_weights, network_centrality: parseFloat(e.target.value) })),
                  }),
              ]),
          ]),
        ]),

        React.createElement(Card, {
          title: 'Notification Preferences',
          children: React.createElement('div', {
            className: 'space-y-4',
          }, [
            React.createElement('div', null, [
              React.createElement('label', {
                className: 'flex items-center space-x-2',
              }, [
                React.createElement('input', {
                  id: 'email_alerts',
                  type: 'checkbox',
                  checked: settings.notification_preferences.email_alerts,
                  onChange: (e) => setSettings(prev => ({ ...prev, notification_preferences: { ...prev.notification_preferences, email_alerts: e.target.checked })),
                  className: 'h-4 w-4 h-4 text-blue-600',
                }),
                React.createElement('span', {
                  className: 'ml-2',
                }, 'Email Alerts'),
              ]),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                className: 'flex items-center space-x-2',
              }, [
                React.createElement('input', {
                  id: 'sms_alerts',
                  type: 'checkbox',
                  checked: settings.notification_preferences.sms_alerts,
                  onChange: (e) => setSettings(prev => ({ ...prev, notification_preferences: { ...prev.notification_preferences, sms_alerts: e.target.checked })),
                  className: 'h-4 w-4 h-4 text-blue-600',
                }),
                React.createElement('span', {
                  className: 'ml-2',
                }, 'SMS Alerts'),
              ]),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'alert_threshold',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Alert Threshold'),
              React.createElement('select', {
                id: 'alert_threshold',
                value: settings.notification_preferences.alert_threshold,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                onChange: (e) => setSettings(prev => ({ ...prev, notification_preferences: alert_threshold: e.target.value as 'high' | 'medium' | 'low' | 'all' })),
              }, [
                React.createElement('option', {
                  value: 'all',
                }, 'All Alerts'),
                React.createElement('option', {
                  value: 'high',
                }, 'High & Critical'),
                React.createElement('option', {
                  value: 'medium',
                }, 'Medium & Above'),
                React.createElement('option', {
                  value: 'low',
                }, 'Low'),
                React.createElement('option', {
                  value: 'all',
                }, 'All Levels'),
              ]),
            ]),
          ]),
        ]),

        React.createElement('div', {
          className: 'flex gap-4 mt-8',
        }, [
          React.createElement(Button, {
            onClick: handleReset,
            variant: 'danger',
            children: 'Reset to Defaults',
          }),
          React.createElement(Button, {
            onClick: handleSave,
            isLoading: loading,
            fullWidth: true,
            variant: 'primary',
            children: 'Save Settings',
          }),
        ]),
      ]),
    ])
  );
}
