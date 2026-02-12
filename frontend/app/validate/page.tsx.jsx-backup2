'use client';

import React, { useState } from 'react';
import { api } from '../../lib/api';
import { BillSubmission, ValidationReport } from '../../types';
import Button from '../../components/ui/button';
import Card from '../../components/ui/card';
import Alert from '../../components/ui/alert';

export default function ValidatePage() {
  const [bill, setBill] = React.useState<BillSubmission>({
    patient_id: '',
    provider_id: '',
    patient_name: '',
    provider_name: '',
    service_date: new Date().toISOString().split('T')[0],
    bill_date: new Date().toISOString().split('T')[0],
    procedure_code: '',
    diagnosis_code: '',
    billed_amount: 0,
    documentation_text: '',
    facility_name: '',
    facility_type: '',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = React.useState<ValidationReport | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const validationData = await api.validateBill(bill);
      setResult(validationData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate bill');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof BillSubmission, value: string | number) => {
    setBill(prev => ({ ...prev, [field]: value }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const field = e.target.id as keyof BillSubmission;
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    handleChange(field, value);
  };

  return React.createElement('div', {
    className: 'min-h-screen bg-gray-50 py-8',
  }, [
    React.createElement('div', {
      className: 'max-w-3xl mx-auto px-4 sm:px-6 lg:px-8',
    }, [
      React.createElement('h1', {
        className: 'text-3xl font-bold text-gray-900 mb-8',
      }, 'Validate Bill'),

            React.createElement(Card, {}, React.createElement('form', {
              onSubmit: handleSubmit,
              className: 'space-y-6',
            }, [
          error && React.createElement(Alert, {
            variant: 'error',
          }, error),

          React.createElement('div', {
            className: 'grid grid-cols-1 md:grid-cols-2 gap-6',
          }, [
            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'patient_name',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Patient Name'),
              React.createElement('input', {
                type: 'text',
                id: 'patient_name',
                value: bill.patient_name,
                onChange: (e) => handleChange('patient_name', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'patient_id',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Patient ID'),
              React.createElement('input', {
                type: 'text',
                id: 'patient_id',
                value: bill.patient_id,
                onChange: (e) => handleChange('patient_id', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'provider_name',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Provider Name'),
              React.createElement('input', {
                type: 'text',
                id: 'provider_name',
                value: bill.provider_name,
                onChange: (e) => handleChange('provider_name', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'provider_id',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Provider ID (NPI)'),
              React.createElement('input', {
                type: 'text',
                id: 'provider_id',
                value: bill.provider_id,
                onChange: (e) => handleChange('provider_id', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'service_date',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Service Date'),
              React.createElement('input', {
                type: 'date',
                id: 'service_date',
                value: bill.service_date,
                onChange: (e) => handleChange('service_date', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'bill_date',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Bill Date'),
              React.createElement('input', {
                type: 'date',
                id: 'bill_date',
                value: bill.bill_date,
                onChange: (e) => handleChange('bill_date', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'procedure_code',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Procedure Code (CPT)'),
              React.createElement('input', {
                type: 'text',
                id: 'procedure_code',
                value: bill.procedure_code,
                onChange: (e) => handleChange('procedure_code', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'diagnosis_code',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Diagnosis Code (ICD-10)'),
              React.createElement('input', {
                type: 'text',
                id: 'diagnosis_code',
                value: bill.diagnosis_code,
                onChange: (e) => handleChange('diagnosis_code', e.target.value),
                required: true,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'billed_amount',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Billed Amount ($)'),
              React.createElement('input', {
                type: 'number',
                id: 'billed_amount',
                value: bill.billed_amount,
                onChange: (e) => handleChange('billed_amount', parseFloat(e.target.value)),
                required: true,
                step: '0.01',
                min: '0',
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'facility_name',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Facility Name'),
              React.createElement('input', {
                type: 'text',
                id: 'facility_name',
                value: bill.facility_name,
                onChange: (e) => handleChange('facility_name', e.target.value),
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement('div', null, [
              React.createElement('label', {
                htmlFor: 'documentation_text',
                className: 'block text-sm font-medium text-gray-700 mb-2',
              }, 'Documentation Text'),
              React.createElement('textarea', {
                id: 'documentation_text',
                value: bill.documentation_text,
                onChange: (e) => handleChange('documentation_text', e.target.value),
                rows: 4,
                className: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
              }),
            ]),

            React.createElement(Button, {
              variant: 'primary',
              isLoading: loading,
              fullWidth: true,
            }, 'Validate Bill'),
          ]),
        ]),
      }),

      result && React.createElement(Card, {
        title: 'Validation Results',
      }, React.createElement('div', {
        className: 'space-y-6',
      }, [
          React.createElement('div', {
            className: `p-4 rounded-lg ${
              result.risk_level === 'high' ? 'bg-red-50 border-red-500' :
              result.risk_level === 'medium' ? 'bg-yellow-50 border-yellow-500' :
              'bg-green-50 border-green-500'
            }`,
          }, [
            React.createElement('h3', {
              className: 'text-xl font-bold mb-4',
            }, `Risk Level: ${result.risk_level.toUpperCase()}`),

            React.createElement('div', {
              className: 'grid grid-cols-1 md:grid-cols-2 gap-4 mb-4',
            }, [
              React.createElement('div', null, [
                React.createElement('h4', {
                  className: 'font-semibold mb-2',
                }, 'Composite Score'),
                React.createElement('p', {
                  className: 'text-2xl font-bold',
                }, result.composite_score ? result.composite_score.toFixed(2) : 'N/A'),
              ]),

              React.createElement('div', null, [
                React.createElement('h4', {
                  className: 'font-semibold mb-2',
                }, 'Execution Time'),
                React.createElement('p', null, `${result.execution_time_ms.toFixed(0)}ms`),
              ]),
            ]),

            React.createElement('div', {
              className: 'border-t pt-4',
            }, [
              React.createElement('h4', {
                className: 'font-semibold mb-2',
              }, 'Rule Violations'),
              React.createElement('ul', {
                className: 'list-disc list-inside space-y-1',
              }, result.code_violations.map((violation, i) => 
                React.createElement('li', {
                  key: i,
                  className: `p-2 rounded ${
                    violation.severity === 'error' ? 'bg-red-100' :
                    violation.severity === 'warning' ? 'bg-yellow-100' :
                    'bg-blue-100'
                  }`,
                }, [
                  React.createElement('span', {
                    className: 'font-semibold',
                  }, violation.violation_type),
                  React.createElement('br', null),
                  violation.message,
                ])
              )),

              result.anomaly_flags.length > 0 && React.createElement('div', {
                className: 'border-t pt-4',
              }, [
                React.createElement('h4', {
                  className: 'font-semibold mb-2',
                }, 'Anomaly Flags'),
                React.createElement('ul', {
                  className: 'list-disc list-inside space-y-1',
                }, result.anomaly_flags.map((flag, i) =>
                  React.createElement('li', {
                    key: i,
                    className: 'p-2 bg-orange-50 rounded',
                  }, [
                    React.createElement('span', {
                      className: 'font-semibold',
                    }, `${flag.type}:`),
                    React.createElement('br', null),
                    flag.message,
                    React.createElement('br', null),
                    `Score: ${flag.anomaly_score.toFixed(2)} (Threshold: ${flag.threshold})`,
                  ])
                )),

              result.ml_predictions.length > 0 && React.createElement('div', {
                className: 'border-t pt-4',
              }, [
                React.createElement('h4', {
                  className: 'font-semibold mb-2',
                }, 'ML Predictions'),
                result.ml_predictions.map((pred, i) =>
                  React.createElement('div', {
                    key: i,
                    className: 'p-2 bg-purple-50 rounded mb-2',
                  }, [
                    React.createElement('span', {
                      className: 'font-semibold',
                    }, `${pred.model_type}: `),
                    React.createElement('br', null),
                    `Is Fraud: ${pred.is_fraud ? 'Yes' : 'No'}`,
                    React.createElement('br', null),
                    `Probability: ${(pred.fraud_probability * 100).toFixed(1)}%`,
                    React.createElement('br', null),
                    `Confidence: ${(pred.confidence * 100).toFixed(1)}%`,
                  ])
                ),
              ]),
            ]),
          ]),
        ]),
      ]),
    ])
  );
}
