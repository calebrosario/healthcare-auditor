'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Settings } from '../../types';
import Card from '../../components/ui/card';
import Button from '../../components/ui/button';

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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        </header>

        {error && (
          <div className="mb-4">
            <div className="bg-red-50 border-red-500 text-red-700 p-4 rounded-lg">
              {error}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Loading...</div>
          </div>
        )}

        {success && (
          <div className="mb-4">
            <div className="bg-green-50 border-green-500 text-green-700 p-4 rounded-lg">
              Settings saved successfully!
            </div>
          </div>
        )}

        {!loading && (
          <form onSubmit={handleSave}>
            <div className="space-y-6">
              <Card title="ML Detection Thresholds">
                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="ml_threshold_low"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Low Fraud Probability Threshold (%)
                    </label>
                    <input
                      type="number"
                      id="ml_threshold_low"
                      value={(settings.ml_threshold_low * 100).toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          ml_threshold_low: parseFloat(e.currentTarget.value) / 100,
                        }))
                      }
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="ml_threshold_high"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      High Fraud Probability Threshold (%)
                    </label>
                    <input
                      type="number"
                      id="ml_threshold_high"
                      value={(settings.ml_threshold_high * 100).toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          ml_threshold_high: parseFloat(e.currentTarget.value) / 100,
                        }))
                      }
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="anomaly_sensitivity"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Anomaly Detection Sensitivity
                    </label>
                    <select
                      id="anomaly_sensitivity"
                      value={settings.anomaly_sensitivity}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          anomaly_sensitivity: e.currentTarget.value as 'low' | 'medium' | 'high',
                        }))
                      }
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
              </Card>

              <Card title="Risk Scoring Weights">
                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="anomaly_score"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Anomaly Score Weight (%)
                    </label>
                    <input
                      type="number"
                      id="anomaly_score"
                      value={settings.risk_weights.anomaly_score.toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          risk_weights: {
                            ...prev.risk_weights,
                            anomaly_score: parseFloat(e.currentTarget.value),
                          },
                        }))
                      }
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="ml_probability"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      ML Probability Weight (%)
                    </label>
                    <input
                      type="number"
                      id="ml_probability"
                      value={settings.risk_weights.ml_probability.toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          risk_weights: {
                            ...prev.risk_weights,
                            ml_probability: parseFloat(e.currentTarget.value),
                          },
                        }))
                      }
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="code_violations"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Code Violations Weight (%)
                    </label>
                    <input
                      type="number"
                      id="code_violations"
                      value={settings.risk_weights.code_violations.toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          risk_weights: {
                            ...prev.risk_weights,
                            code_violations: parseFloat(e.currentTarget.value),
                          },
                        }))
                      }
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="network_centrality"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Network Centrality Weight (%)
                    </label>
                    <input
                      type="number"
                      id="network_centrality"
                      value={settings.risk_weights.network_centrality.toString()}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          risk_weights: {
                            ...prev.risk_weights,
                            network_centrality: parseFloat(e.currentTarget.value),
                          },
                        }))
                      }
                    />
                  </div>
                </div>
              </Card>

              <Card title="Notification Preferences">
                <div className="space-y-4">
                  <label className="flex items-center space-x-2">
                    <input
                      id="email_alerts"
                      type="checkbox"
                      checked={settings.notification_preferences.email_alerts}
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          notification_preferences: {
                            ...prev.notification_preferences,
                            email_alerts: e.currentTarget.checked,
                          },
                        }))
                      }
                      className="h-4 w-4 text-blue-600"
                    />
                    <span className="ml-2">Email Alerts</span>
                  </label>

                  <label className="flex items-center space-x-2">
                    <input
                      id="sms_alerts"
                      type="checkbox"
                      checked={settings.notification_preferences.sms_alerts}
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          notification_preferences: {
                            ...prev.notification_preferences,
                            sms_alerts: e.currentTarget.checked,
                          },
                        }))
                      }
                      className="h-4 w-4 text-blue-600"
                    />
                    <span className="ml-2">SMS Alerts</span>
                  </label>

                  <div>
                    <label
                      htmlFor="alert_threshold"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Alert Threshold
                    </label>
                    <select
                      id="alert_threshold"
                      value={settings.notification_preferences.alert_threshold}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          notification_preferences: {
                            ...prev.notification_preferences,
                            alert_threshold: e.currentTarget.value as 'high' | 'medium' | 'low' | 'all',
                          },
                        }))
                      }
                    >
                      <option value="all">All Alerts</option>
                      <option value="high">High & Critical</option>
                      <option value="medium">Medium & Above</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
              </Card>

              <div className="flex gap-4 mt-8">
                <Button onClick={handleReset} variant="danger">
                  Reset to Defaults
                </Button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Saving...' : 'Save Settings'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
