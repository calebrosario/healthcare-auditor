'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { InvestigationResult } from '../../types';
import Card from '../../components/ui/card';
import Button from '../../components/ui/button';

export default function InvestigatePage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
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
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading investigation...</div>
      </div>
    );
  }

  if (!investigation) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="mb-8">
          <div>
            <button
              onClick={() => router.back()}
              className="text-blue-600 hover:text-blue-700 flex items-center mb-4"
              type="button"
            >
              ← Back to Alerts
            </button>
            <h1 className="text-3xl font-bold text-gray-900">
              Investigation: {investigation.bill.claim_id}
            </h1>
          </div>

          {error && (
            <div className="mb-4 text-red-600">
              {error}
            </div>
          )}
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card title="Bill Details">
            <div className="space-y-4">
              <div>
                <div>
                  <span className="text-gray-600">Claim ID:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {investigation.bill.claim_id}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Patient:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {investigation.bill.patient_name} ({investigation.bill.patient_id})
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Provider:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {investigation.bill.provider_name} ({investigation.bill.provider_id})
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Service Date:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {new Date(investigation.bill.service_date).toLocaleDateString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Bill Date:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {new Date(investigation.bill.bill_date).toLocaleDateString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Procedure:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {investigation.bill.procedure_code}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Diagnosis:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {investigation.bill.diagnosis_code}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    ${investigation.bill.billed_amount.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Validation Results">
            <div className="space-y-4">
              <div
                className={`p-4 rounded-lg border ${
                  investigation.validation.risk_level === 'high'
                    ? 'bg-red-50 border-red-500'
                    : investigation.validation.risk_level === 'medium'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-green-50 border-green-500'
                }`}
              >
                <h3 className="text-lg font-bold mb-2">
                  Risk Level: {investigation.validation.risk_level.toUpperCase()}
                </h3>
                <div>
                  <span className="text-gray-600">Composite Score:</span>
                  <span className="text-2xl font-bold text-gray-900 ml-2">
                    {investigation.validation.composite_score
                      ? investigation.validation.composite_score.toFixed(2)
                      : 'N/A'}
                  </span>
                </div>
              </div>

              {investigation.validation.anomaly_flags.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Anomaly Flags</h4>
                  {investigation.validation.anomaly_flags.map((flag, i) => (
                    <div key={i} className="p-3 bg-orange-50 rounded mb-2">
                      <span className="font-semibold">{flag.type}</span>
                      <br />
                      <span className="text-sm">{flag.message}</span>
                      <br />
                      <span className="text-xs">
                        Score: {flag.anomaly_score.toFixed(2)} (Threshold:{' '}
                        {flag.threshold})
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {investigation.validation.ml_predictions.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">ML Predictions</h4>
                  {investigation.validation.ml_predictions.map((pred, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded ${
                        pred.is_fraud ? 'bg-red-100 border-red-500' : 'bg-green-100 border-green-500'
                      } mb-2`}
                    >
                      <span className="font-semibold">{pred.model_type}</span>
                      <br />
                      <span className="text-sm">
                        Is Fraud: {pred.is_fraud ? 'Yes' : 'No'}
                      </span>
                      <br />
                      <span className="text-xs">
                        Probability: {(pred.fraud_probability * 100).toFixed(1)}%
                      </span>
                      <br />
                      <span className="text-xs">
                        Confidence: {(pred.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {investigation.validation.code_violations.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Code Violations</h4>
                  {investigation.validation.code_violations.map((violation, i) => (
                    <div
                      key={i}
                      className={`p-2 rounded ${
                        violation.severity === 'error'
                          ? 'bg-red-50'
                          : violation.severity === 'warning'
                          ? 'bg-yellow-50'
                          : 'bg-blue-50'
                      }`}
                    >
                      <span className="font-semibold">
                        {violation.violation_type}
                      </span>
                      <br />
                      <span className="text-sm">{violation.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          <Card title="Audit Trail">
            <div className="space-y-3">
              {investigation.audit_trail.map((entry, i) => (
                <div
                  key={i}
                  className="p-3 bg-gray-50 rounded border border-gray-200"
                >
                  <div className="text-sm text-gray-500 mb-1">
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                  <div className="font-medium">{entry.action}</div>
                  <div className="text-gray-700">{entry.actor}</div>
                  <div className="text-sm mt-1">{entry.details}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
