'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '../../lib/api';
import { InvestigationResult, GraphData, TimelineEvent } from '../../types';
import Card from '../../components/ui/card';
import Button from '../../components/ui/button';

export default function InvestigatePage() {
  const { id } = useParams();
  const [investigation, setInvestigation] = React.useState<InvestigationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;

    const fetchInvestigation = async () => {
      try {
        setLoading(true);
        const data = await api.getInvestigation(id);
        setInvestigation(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load investigation');
      } finally {
        setLoading(false);
      }
    };

    fetchInvestigation();
  }, [id]);

  if (loading) {
    return React.createElement('div', {
      className: 'min-h-screen bg-gray-50 flex items-center justify-center',
    }, 'Loading investigation...');
  }

  if (!investigation) {
    return null;
  }

  return React.createElement('div', {
    className: 'min-h-screen bg-gray-50 py-8',
  }, [
    React.createElement('div', {
      className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    }, [
      React.createElement('header', {
        className: 'mb-8',
      }, [
        React.createElement('div', null, [
          React.createElement('button', {
            onClick: () => history.back(),
            className: 'text-blue-600 hover:text-blue-700 flex items-center',
            type: 'button',
          }, '← Back to Alerts'),
          React.createElement('h1', {
            className: 'text-3xl font-bold text-gray-900',
          }, `Investigation: ${investigation.bill.claim_id}`),
        ]),

        error && React.createElement('div', {
          className: 'mb-4',
        }, error),
      ]),

      React.createElement('div', {
        className: 'grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8',
      }, [
        React.createElement(Card, {
          title: 'Bill Details',
          children: React.createElement('div', {
            className: 'space-y-4',
          }, [
            React.createElement('div', null, [
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Claim ID:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, investigation.bill.claim_id),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Patient:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, `${investigation.bill.patient_name} (${investigation.bill.patient_id})`),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Provider:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, `${investigation.bill.provider_name} (${investigation.bill.provider_id})`),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Service Date:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, new Date(investigation.bill.service_date).toLocaleDateString()),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Bill Date:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, new Date(investigation.bill.bill_date).toLocaleDateString()),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Procedure:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, `${investigation.bill.procedure_code}`),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Diagnosis:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, `${investigation.bill.diagnosis_code}`),
              ]),
              React.createElement('div', null, [
                React.createElement('span', {
                  className: 'text-gray-600',
                }, 'Amount:'),
                React.createElement('span', {
                  className: 'font-semibold text-gray-900',
                }, `$${investigation.bill.billed_amount.toFixed(2)}`),
              ]),
            ]),
          ]),
        ]),

        React.createElement(Card, {
          title: 'Validation Results',
          children: React.createElement('div', {
            className: 'space-y-4',
          }, [
            React.createElement('div', null, [
              React.createElement('div', {
                className: `p-4 rounded-lg ${
                  investigation.validation.risk_level === 'high' ? 'bg-red-50 border-red-500' :
                  investigation.validation.risk_level === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                  'bg-green-50 border-green-500'
                }`,
              }, [
                React.createElement('h3', {
                  className: 'text-lg font-bold mb-2',
                }, `Risk Level: ${investigation.validation.risk_level.toUpperCase()}`),
                React.createElement('div', null, [
                  React.createElement('span', {
                    className: 'text-gray-600',
                  }, 'Composite Score:'),
                  React.createElement('span', {
                    className: 'text-2xl font-bold text-gray-900',
                  }, investigation.validation.composite_score ? investigation.validation.composite_score.toFixed(2) : 'N/A'),
                ]),
              ]),
            ]),

            investigation.validation.anomaly_flags.length > 0 && React.createElement('div', {
              className: 'border-t pt-4',
            }, [
              React.createElement('h4', {
                className: 'font-semibold mb-2',
              }, 'Anomaly Flags'),
              investigation.validation.anomaly_flags.map((flag, i) =>
                React.createElement('div', {
                  key: i,
                  className: 'p-3 bg-orange-50 rounded mb-2',
                }, [
                  React.createElement('span', {
                    className: 'font-semibold',
                  }, `${flag.type}`),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-sm',
                  }, flag.message),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-xs',
                  }, `Score: ${flag.anomaly_score.toFixed(2)} (Threshold: ${flag.threshold})`),
                ]),
              )),
            ]),
            ]),

            investigation.validation.ml_predictions.length > 0 && React.createElement('div', {
              className: 'border-t pt-4',
            }, [
              React.createElement('h4', {
                className: 'font-semibold mb-2',
              }, 'ML Predictions'),
              investigation.validation.ml_predictions.map((pred, i) =>
                React.createElement('div', {
                  key: i,
                  className: `p-3 rounded ${
                    pred.is_fraud ? 'bg-red-100 border-red-500' :
                    'bg-green-100 border-green-500'
                  } mb-2`,
                }, [
                  React.createElement('span', {
                    className: 'font-semibold',
                  }, `${pred.model_type}`),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-sm',
                  }, `Is Fraud: ${pred.is_fraud ? 'Yes' : 'No'}`),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-xs',
                  }, `Probability: ${(pred.fraud_probability * 100).toFixed(1)}%`),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-xs',
                  }, `Confidence: ${(pred.confidence * 100).toFixed(1)}%`),
                ]),
              )),
            ]),
            ]),

            investigation.validation.code_violations.length > 0 && React.createElement('div', {
              className: 'border-t pt-4',
            }, [
              React.createElement('h4', {
                className: 'font-semibold mb-2',
              }, 'Code Violations'),
              investigation.validation.code_violations.map((violation, i) =>
                React.createElement('div', {
                  key: i,
                  className: `p-2 rounded ${
                    violation.severity === 'error' ? 'bg-red-50' :
                    violation.severity === 'warning' ? 'bg-yellow-50' :
                    'bg-blue-50'
                  }`,
                }, [
                  React.createElement('span', {
                    className: 'font-semibold',
                  }, violation.violation_type),
                  React.createElement('br', null),
                  React.createElement('span', {
                    className: 'text-sm',
                  }, violation.message),
                ]),
              )),
            ]),
          ]),
        ]),

        React.createElement(Card, {
          title: 'Audit Trail',
          children: React.createElement('div', {
            className: 'space-y-3',
          }, [
            investigation.audit_trail.map((entry, i) =>
              React.createElement('div', {
                key: i,
                className: 'p-3 bg-gray-50 rounded border border-gray-200',
              }, [
                React.createElement('div', {
                  className: 'text-sm text-gray-500 mb-1',
                }, new Date(entry.timestamp).toLocaleString()),
                React.createElement('div', {
                  className: 'font-medium',
                }, entry.action),
                React.createElement('div', {
                  className: 'text-gray-700',
                }, entry.actor),
                React.createElement('div', {
                  className: 'text-sm mt-1',
                }, entry.details),
              ]),
            ]),
          ]),
        ]),
      ]),
    ])
  );
}
