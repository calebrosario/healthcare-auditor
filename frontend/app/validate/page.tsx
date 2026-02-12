'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import { BillSubmission, ValidationReport } from '@/types';
import Button from '@/components/ui/button';
import Card from '@/components/ui/card';
import Alert from '@/components/ui/alert';

export default function ValidatePage() {
  const [bill, setBill] = useState<BillSubmission>({
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
  const [result, setResult] = useState<ValidationReport | null>(null);
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
    const field = e.currentTarget.id as keyof BillSubmission;
    const value = e.currentTarget.type === 'number' ? parseFloat(e.currentTarget.value) : e.currentTarget.value;
    handleChange(field, value);
  };

  const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const field = e.currentTarget.id as keyof BillSubmission;
    handleChange(field, e.currentTarget.value);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Validate Bill</h1>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && <Alert variant="error">{error}</Alert>}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="patient_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Patient Name
                </label>
                <input
                  type="text"
                  id="patient_name"
                  value={bill.patient_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="patient_id"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Patient ID
                </label>
                <input
                  type="text"
                  id="patient_id"
                  value={bill.patient_id}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="provider_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Provider Name
                </label>
                <input
                  type="text"
                  id="provider_name"
                  value={bill.provider_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="provider_id"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Provider ID (NPI)
                </label>
                <input
                  type="text"
                  id="provider_id"
                  value={bill.provider_id}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="service_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Service Date
                </label>
                <input
                  type="date"
                  id="service_date"
                  value={bill.service_date}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="bill_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Bill Date
                </label>
                <input
                  type="date"
                  id="bill_date"
                  value={bill.bill_date}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="procedure_code"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Procedure Code (CPT)
                </label>
                <input
                  type="text"
                  id="procedure_code"
                  value={bill.procedure_code}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="diagnosis_code"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Diagnosis Code (ICD-10)
                </label>
                <input
                  type="text"
                  id="diagnosis_code"
                  value={bill.diagnosis_code}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="billed_amount"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Billed Amount ($)
                </label>
                <input
                  type="number"
                  id="billed_amount"
                  value={bill.billed_amount}
                  onChange={handleInputChange}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="facility_name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Facility Name
                </label>
                <input
                  type="text"
                  id="facility_name"
                  value={bill.facility_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="md:col-span-2">
                <label
                  htmlFor="documentation_text"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Documentation Text
                </label>
                <textarea
                  id="documentation_text"
                  value={bill.documentation_text}
                  onChange={handleTextAreaChange}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <Button variant="primary" isLoading={loading} fullWidth>
              Validate Bill
            </Button>
          </form>
        </Card>

        {result && (
          <Card title="Validation Results">
            <div className="space-y-6">
              <div
                className={`p-4 rounded-lg border ${
                  result.risk_level === 'high'
                    ? 'bg-red-50 border-red-500'
                    : result.risk_level === 'medium'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-green-50 border-green-500'
                }`}
              >
                <h3 className="text-xl font-bold mb-4">
                  Risk Level: {result.risk_level.toUpperCase()}
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="font-semibold mb-2">Composite Score</h4>
                    <p className="text-2xl font-bold">
                      {result.composite_score
                        ? result.composite_score.toFixed(2)
                        : 'N/A'}
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Execution Time</h4>
                    <p>{result.execution_time_ms.toFixed(0)}ms</p>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Rule Violations</h4>
                <ul className="list-disc list-inside space-y-1">
                  {result.code_violations.map((violation, i) => (
                    <li
                      key={i}
                      className={`p-2 rounded ${
                        violation.severity === 'error'
                          ? 'bg-red-100'
                          : violation.severity === 'warning'
                          ? 'bg-yellow-100'
                          : 'bg-blue-100'
                      }`}
                    >
                      <span className="font-semibold">
                        {violation.violation_type}
                      </span>
                      <br />
                      {violation.message}
                    </li>
                  ))}
                </ul>
              </div>

              {result.anomaly_flags.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Anomaly Flags</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {result.anomaly_flags.map((flag, i) => (
                      <li key={i} className="p-2 bg-orange-50 rounded">
                        <span className="font-semibold">{flag.type}:</span>
                        <br />
                        {flag.message}
                        <br />
                        Score: {flag.anomaly_score.toFixed(2)} (Threshold:{' '}
                        {flag.threshold})
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.ml_predictions.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">ML Predictions</h4>
                  {result.ml_predictions.map((pred, i) => (
                    <div
                      key={i}
                      className="p-2 bg-purple-50 rounded mb-2"
                    >
                      <span className="font-semibold">{pred.model_type}:</span>
                      <br />
                      Is Fraud: {pred.is_fraud ? 'Yes' : 'No'}
                      <br />
                      Probability:{' '}
                      {(pred.fraud_probability * 100).toFixed(1)}%
                      <br />
                      Confidence: {(pred.confidence * 100).toFixed(1)}%
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
