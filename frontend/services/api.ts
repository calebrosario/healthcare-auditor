/**
 * API service for communicating with the Healthcare Auditor backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ErrorResponse {
  detail: string;
}

// Billing codes
export interface BillingCode {
  id: number;
  code: string;
  code_type: string;
  description?: string;
  effective_date: string;
  termination_date?: string;
  category?: string;
  status: string;
}

export async function getBillingCodes(params?: {
  code_type?: string;
  category?: string;
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<BillingCode[]> {
  const queryString = new URLSearchParams(params as any).toString();
  const response = await fetch(`${API_URL}/api/v1/billing-codes?${queryString}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch billing codes');
  }
  
  const data = await response.json();
  return data;
}

// Providers
export interface Provider {
  id: number;
  npi: string;
  name: string;
  provider_type: string;
  specialty?: string;
  city?: string;
  state: string;
  license_status?: string;
}

export async function getProviders(params?: {
  provider_type?: string;
  specialty?: string;
  state?: string;
  skip?: number;
  limit?: number;
}): Promise<Provider[]> {
  const queryString = new URLSearchParams(params as any).toString();
  const response = await fetch(`${API_URL}/api/v1/providers?${queryString}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch providers');
  }
  
  const data = await response.json();
  return data;
}

// Bills
export interface Bill {
  id: number;
  claim_id: string;
  bill_date: string;
  billed_amount: number;
  status: string;
  fraud_score?: number;
}

export interface BillValidationRequest {
  patient_id: string;
  provider_npi: string;
  insurer_id: number;
  procedure_code: string;
  diagnosis_code?: string;
  billed_amount: number;
  bill_date: string;
}

export interface BillValidationResponse {
  claim_id: string;
  fraud_score: number;
  fraud_risk_level: string;
  compliance_score: number;
  issues: string[];
  warnings: string[];
}

export async function validateBill(request: BillValidationRequest): Promise<BillValidationResponse> {
  const response = await fetch(`${API_URL}/api/v1/bills/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error('Failed to validate bill');
  }
  
  return await response.json();
}

// Alerts
export interface Alert {
  id: number;
  alert_type: string;
  alert_name: string;
  description?: string;
  priority: string;
  score: number;
  status: string;
  created_at: string;
}

export async function getAlerts(params?: {
  alert_type?: string;
  status?: string;
  priority?: string;
  skip?: number;
  limit?: number;
}): Promise<Alert[]> {
  const queryString = new URLSearchParams(params as any).toString();
  const response = await fetch(`${API_URL}/api/v1/alerts?${queryString}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch alerts');
  }
  
  const data = await response.json();
  return data;
}

// Knowledge Graph
export interface GraphNode {
  id: string;
  labels: string[];
  properties: Record<string, any>;
}

export interface GraphStats {
  nodes: number;
  edges: number;
  node_types: string[];
  edge_types: string[];
}

export async function getGraphStats(): Promise<GraphStats> {
  const response = await fetch(`${API_URL}/api/v1/knowledge-graph/stats`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch graph stats');
  }
  
  return await response.json();
}
