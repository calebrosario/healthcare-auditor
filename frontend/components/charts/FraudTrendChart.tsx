'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface FraudTrendChartProps {
  data: Array<{
    date: string;
    fraud_count: number;
    total_count: number;
    fraud_rate: number;
  }>;
}

export default function FraudTrendChart({ data }: FraudTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" stroke="#8884d8" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="fraud_count"
          stroke="#ef4444"
          name="Fraud Detected"
        />
        <Line
          type="monotone"
          dataKey="total_count"
          stroke="#8884d8"
          name="Total Bills"
          strokeDasharray="5 5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
