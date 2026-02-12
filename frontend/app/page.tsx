'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import { DashboardStats } from '../types';
import Alert from '../components/ui/alert';
import Card from '../components/ui/card';

export default function Home() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await api.getDashboardStats();
        setStats(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Healthcare Auditor Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Healthcare billing fraud detection and compliance verification
          </p>
        </header>

        {error && <Alert variant="error">{error}</Alert>}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Loading dashboard...</div>
          </div>
        ) : stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card title="Overview">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Bills</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {stats.total_bills.toString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Fraud Detected</span>
                  <span
                    className={`text-3xl font-bold ${
                      stats.fraud_detected > 0 ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {stats.fraud_detected.toString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Fraud Rate</span>
                  <span
                    className={`text-3xl font-bold ${
                      stats.fraud_rate > 0.05 ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {(stats.fraud_rate * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </Card>

            <Card title="Alerts">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">New Today</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {stats.alerts_today.toString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">This Week</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {stats.alerts_week.toString()}
                  </span>
                </div>
              </div>
            </Card>

            <Card title="Active Investigations">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Active</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {stats.active_investigations.toString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Avg Validation Time</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {stats.avg_validation_time.toFixed(0)}ms
                  </span>
                </div>
              </div>
            </Card>

            <Card
              title="Quick Actions"
              footer={
                <div className="text-center text-sm text-gray-500">
                  Last updated: {new Date().toLocaleString()}
                </div>
              }
            >
              <div className="space-y-3">
                <Link href="/validate" className="block w-full">
                  <button
                    className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    type="button"
                  >
                    Validate New Bill
                  </button>
                </Link>
                <Link href="/alerts" className="block w-full">
                  <button
                    className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    type="button"
                  >
                    View All Alerts
                  </button>
                </Link>
                <Link href="/analytics" className="block w-full">
                  <button
                    className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    type="button"
                  >
                    View Analytics
                  </button>
                </Link>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
