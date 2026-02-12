'use client';

import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { AnalyticsMetrics, TrendData } from '../../types';
import Card from '../../components/ui/card';

export default function AnalyticsPage() {
  const [metrics, setMetrics] = React.useState<AnalyticsMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await api.getAnalytics();
        setMetrics(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

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
        }, 'Analytics Dashboard'),
      ]),

      error && React.createElement('div', {
        className: 'mb-4',
      }, error),

      loading ? (
        React.createElement('div', {
          className: 'flex items-center justify-center py-12',
        }, 'Loading analytics...')
      ) : metrics && (
        React.createElement('div', {
          className: 'grid grid-cols-1 lg:grid-cols-2 gap-6',
        }, [
          React.createElement(Card, {
            title: 'Fraud Trend',
            children: React.createElement('div', {
              className: 'text-sm text-gray-600 mb-4',
            }, 'Number of fraud cases detected over time'),
            metrics && metrics.fraud_trend && metrics.fraud_trend.map((item, i) =>
              React.createElement('div', {
                key: i,
                className: 'flex items-center justify-between',
              }, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, item.date),
                React.createElement('span', {
                  className: `ml-2 px-2 py-1 rounded text-sm font-medium ${
                    item.fraud_rate > 0.05 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                  }`,
                }, `${item.fraud_rate.toFixed(1)}%`),
              ]),
            ),
          ),

          React.createElement(Card, {
            title: 'Top Risk Providers',
            children: React.createElement('div', {
              className: 'space-y-4',
            }, metrics && metrics.top_risk_providers && metrics.top_risk_providers.map((provider, i) =>
              React.createElement('div', {
                key: i,
                className: 'p-3 rounded-lg border-l-4 mb-2 hover:bg-gray-50',
              }, [
                React.createElement('div', null, [
                  React.createElement('div', {
                    className: 'flex items-center justify-between',
                  }, [
                    React.createElement('span', {
                      className: 'text-gray-600',
                    }, provider.provider_name),
                    React.createElement('span', {
                      className: `text-2xl font-bold ${
                        provider.risk_score > 0.7 ? 'text-red-600' : 'text-gray-900'
                      }`,
                    }, provider.risk_score.toFixed(2)),
                  ]),
                  React.createElement('div', null, [
                    React.createElement('span', {
                      className: 'text-sm text-gray-500',
                    }, `${provider.fraud_count} fraud cases`),
                  ]),
                  React.createElement('div', null, [
                    React.createElement('span', {
                      className: 'text-sm text-gray-500',
                    }, `out of ${provider.bills_processed} bills`),
                  ]),
                  React.createElement('div', {
                      className: 'text-sm text-gray-500',
                    }, `${((provider.fraud_count / provider.bills_processed) * 100).toFixed(1)}% rate`),
                  ]),
                ]),
              ]),
            ),

          React.createElement(Card, {
            title: 'Code Violation Breakdown',
            children: React.createElement('div', {
              className: 'space-y-4',
            }, metrics && metrics.code_violation_breakdown && [
              React.createElement('div', {
                className: 'flex items-center justify-between mb-2',
              }, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Invalid ICD-10'),
                React.createElement('span', {
                  className: 'text-2xl font-bold text-gray-900',
                }, metrics.code_violation_breakdown.invalid_icd10),
              ]),
              React.createElement('div', {
                className: 'flex items-center justify-between mb-2',
              }, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Invalid CPT'),
                React.createElement('span', {
                  className: 'text-2xl font-bold text-gray-900',
                }, metrics.code_violation_breakdown.invalid_cpt),
                ]),
              React.createElement('div', {
                  className: 'flex items-center justify-between mb-2',
              }, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Invalid DX Pair'),
                React.createElement('span', {
                  className: 'text-2xl font-bold text-gray-900',
                }, metrics.code_violation_breakdown.invalid_dx_pair),
                ]),
              ]),
            ]),

          React.createElement(Card, {
            title: 'ML Model Performance',
            children: metrics && metrics.ml_model_performance && [
              React.createElement('div', {
                className: 'space-y-4',
              }, metrics.ml_model_performance.map((model, i) =>
                React.createElement('div', {
                  key: i,
                  className: 'border-l p-3 mb-2',
                }, [
                  React.createElement('div', null, [
                    React.createElement('h4', {
                      className: 'text-lg font-semibold text-gray-900 mb-1',
                    }, model.model_type),
                  ]),
                  React.createElement('div', {
                    className: 'text-sm text-gray-600 mb-3',
                  }, [
                    React.createElement('div', null, [
                      React.createElement('span', {
                        className: 'text-gray-600',
                      }, 'Accuracy: '),
                      React.createElement('span', {
                        className: 'text-2xl font-bold text-gray-900',
                      }, model.accuracy ? model.accuracy.toFixed(2) : 'N/A'),
                      ]),
                    React.createElement('br', null),
                    React.createElement('span', {
                        className: 'text-gray-600',
                      }, 'Precision: '),
                      React.createElement('span', {
                        className: 'text-2xl font-bold text-gray-900',
                      }, model.precision ? model.precision.toFixed(2) : 'N/A'),
                      ]),
                    React.createElement('br', null),
                    React.createElement('span', {
                        className: 'text-gray-600',
                      }, 'Recall: '),
                      React.createElement('span', {
                        className: 'text-2xl font-bold text-gray-900',
                      }, model.recall ? model.recall.toFixed(2) : 'N/A'),
                      ]),
                    React.createElement('br', null),
                    React.createElement('span', {
                      className: 'text-gray-600',
                      }, 'F1 Score: '),
                      React.createElement('span', {
                        className: 'text-2xl font-bold text-gray-900',
                      }, model.f1_score ? model.f1_score.toFixed(2) : 'N/A'),
                      ]),
                    React.createElement('br', null),
                    React.createElement('span', {
                      className: 'text-gray-600',
                      }, 'False Positive Rate: '),
                      React.createElement('span', {
                        className: 'text-2xl font-bold text-gray-900',
                      }, model.false_positive_rate ? model.false_positive_rate.toFixed(2) : 'N/A'),
                      ]),
                  ]),
                ]),
              ]),
            ]),
        ]),
      ]),
    ])
  );
}
