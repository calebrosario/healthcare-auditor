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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-500 rounded-lg">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              Loading analytics...
            </div>
          ) : metrics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card title="Fraud Trend">
                <div className="text-sm text-gray-600 mb-4">Number of fraud cases detected over time</div>
                {metrics.fraud_trend && metrics.fraud_trend.map((item: TrendData, i: number) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-gray-600">{item.date}</span>
                    <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                      item.fraud_rate > 0.05 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {item.fraud_rate.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </Card>

              <Card title="Top Risk Providers">
                <div className="space-y-4">
                  {metrics.top_risk_providers && metrics.top_risk_providers.map((provider, i: number) => (
                    <div key={i} className="p-3 rounded-lg border-l-4 mb-2 hover:bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">{provider.provider_name}</span>
                        <span className={`text-2xl font-bold ${
                          provider.risk_score > 0.7 ? 'text-red-600' : 'text-gray-900'
                        }`}>
                          {provider.risk_score.toFixed(2)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {provider.fraud_count} fraud cases out of {provider.bills_processed} bills ({((provider.fraud_count / provider.bills_processed) * 100).toFixed(1)}% rate)
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="Code Violation Breakdown">
                <div className="space-y-4">
                  {metrics.code_violation_breakdown && (
                    <>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">Invalid ICD-10</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {metrics.code_violation_breakdown.invalid_icd10}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">Invalid CPT</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {metrics.code_violation_breakdown.invalid_cpt}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">Invalid DX Pair</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {metrics.code_violation_breakdown.invalid_dx_pair}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">Bundling</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {metrics.code_violation_breakdown.bundling}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600">Amount Limit</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {metrics.code_violation_breakdown.amount_limit}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </Card>

              <Card title="ML Model Performance">
                <div className="space-y-4">
                  {metrics.ml_model_performance && metrics.ml_model_performance.map((model, i: number) => (
                    <div key={i} className="border-l p-3 mb-2">
                      <h4 className="text-lg font-semibold text-gray-900 mb-1">
                        {model.model_type}
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                        <div>
                          <span className="text-gray-600">Accuracy:</span>
                          <span className="text-2xl font-bold text-gray-900">
                            {model.accuracy ? model.accuracy.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Precision:</span>
                          <span className="text-2xl font-bold text-gray-900">
                            {model.precision ? model.precision.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Recall:</span>
                          <span className="text-2xl font-bold text-gray-900">
                            {model.recall ? model.recall.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">F1 Score:</span>
                          <span className="text-2xl font-bold text-gray-900">
                            {model.f1_score ? model.f1_score.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">False Positive Rate:</span>
                          <span className="text-2xl font-bold text-gray-900">
                            {model.false_positive_rate ? model.false_positive_rate.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </header>
      </div>
    </div>
  );
}
