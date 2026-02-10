// Domain types for Healthcare Auditor
export interface BillSubmission {
  claim_id?: string;
  patient_id: string;
  provider_id: string;
  patient_name: string;
  provider_name: string;
  service_date: string;
  bill_date: string;
  procedure_code: string;
  diagnosis_code: string;
  billed_amount: number;
  allowed_amount?: number;
  documentation_text: string;
  facility_name?: string;
  facility_type?: string;
  insurer_payer_id?: string;
}

export interface Bill {
  id: string;
  claim_id: string;
  patient_id: string;
  patient_name: string;
  provider_id: string;
  provider_name: string;
  service_date: string;
  bill_date: string;
  procedure_code: string;
  diagnosis_code: string;
  billed_amount: number;
  allowed_amount?: number;
  documentation_text?: string;
  facility_name?: string;
  facility_type?: string;
  insurer_payer_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ValidationReport {
  bill: Bill;
  results: RuleResult[];
  composite_score?: number;
  risk_level: 'low' | 'medium' | 'high';
  anomaly_flags: AnomalyFlag[];
  ml_predictions: MLPrediction[];
  network_metrics: NetworkMetrics;
  code_violations: CodeViolation[];
  execution_time_ms: number;
}

export interface RuleResult {
  rule_id: string;
  rule_name: string;
  passed: boolean | null;
  skipped: boolean;
  message: string;
  details: Record<string, unknown>;
  execution_time_ms: number;
}

export interface AnomalyFlag {
  type: 'z_score' | 'benfords_law' | 'frequency_spike' | 'time_series';
  flag: boolean;
  anomaly_score: number;
  threshold: number;
  value: number;
  message: string;
}

export interface MLPrediction {
  model_type: 'random_forest' | 'isolation_forest' | 'ensemble';
  is_fraud: boolean;
  fraud_probability: number;
  confidence: number;
}

export interface NetworkMetrics {
  provider_centrality?: number;
  provider_betweenness?: number;
  community_id?: number;
  community_size?: number;
  network_density?: number;
}

export interface CodeViolation {
  violation_type: 'invalid_icd10' | 'invalid_cpt' | 'invalid_dx_pair' | 'bundling' | 'amount_limit';
  code: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
}

export interface FraudAlert {
  id: string;
  bill_id: string;
  claim_id: string;
  risk_level: 'low' | 'medium' | 'high';
  composite_score: number;
  triggered_rules: string[];
  anomaly_count: number;
  ml_fraud_probability: number;
  created_at: string;
  status: 'open' | 'investigating' | 'resolved' | 'dismissed';
  investigation_notes?: string;
  assigned_to?: string;
}

export interface DashboardStats {
  total_bills: number;
  fraud_detected: number;
  fraud_rate: number;
  alerts_today: number;
  alerts_week: number;
  active_investigations: number;
  avg_validation_time: number;
  top_risk_providers: ProviderRisk[];
}

export interface ProviderRisk {
  provider_id: string;
  provider_name: string;
  risk_score: number;
  fraud_count: number;
  bills_processed: number;
}

export interface AlertFilter {
  status?: string[];
  risk_level?: string[];
  date_from?: string;
  date_to?: string;
  provider_id?: string;
}

export interface InvestigationResult {
  bill: Bill;
  validation: ValidationReport;
  knowledge_graph: GraphData;
  timeline: TimelineEvent[];
  provider_network: GraphData;
  audit_trail: AuditTrailEntry[];
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'provider' | 'hospital' | 'insurer' | 'bill' | 'patient';
  risk_score?: number;
  fraud_flags?: number;
  details?: Record<string, unknown>;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  actor?: string;
  details?: Record<string, unknown>;
}

export interface AuditTrailEntry {
  id: string;
  bill_id: string;
  action: string;
  actor: string;
  timestamp: string;
  details: string;
}

export interface AnalyticsMetrics {
  fraud_trend: TrendData[];
  top_risk_providers: ProviderRisk[];
  code_violation_breakdown: CodeViolationBreakdown;
  ml_model_performance: ModelPerformance;
  rule_effectiveness: RuleEffectiveness;
}

export interface TrendData {
  date: string;
  fraud_count: number;
  total_count: number;
  fraud_rate: number;
}

export interface CodeViolationBreakdown {
  invalid_icd10: number;
  invalid_cpt: number;
  invalid_dx_pair: number;
  bundling: number;
  amount_limit: number;
}

export interface ModelPerformance {
  model_type: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  false_negative_rate: number;
}

export interface RuleEffectiveness {
  rule_id: string;
  rule_name: string;
  total_evaluations: number;
  violations_found: number;
  violation_rate: number;
  avg_execution_time_ms: number;
}

export interface Settings {
  ml_threshold_low: number;
  ml_threshold_high: number;
  anomaly_sensitivity: 'low' | 'medium' | 'high';
  risk_weights: RiskWeights;
  notification_preferences: NotificationPreferences;
}

export interface RiskWeights {
  anomaly_score: number;
  ml_probability: number;
  code_violations: number;
  network_centrality: number;
}

export interface NotificationPreferences {
  email_alerts: boolean;
  sms_alerts: boolean;
  slack_webhook?: string;
  alert_threshold: 'high' | 'medium' | 'low' | 'all';
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
}
