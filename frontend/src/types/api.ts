export type ResourceKind =
  | 'deployment'
  | 'statefulset'
  | 'daemonset'
  | 'pod'
  | 'service'
  | 'ingress'

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserRead {
  id: number
  username: string
  is_active: boolean
}

export interface NamespaceUsage {
  namespace: string
  cpu_millicores: number
  memory_bytes: number
  pod_count: number
}

export interface ClusterSummary {
  cluster_id: string
  generated_at: string
  nodes_total: number
  nodes_ready: number
  pods_total: number
  pods_pending: number
  pods_crashloop: number
  pods_oomkilled: number
  cpu_usage_cores: number
  cpu_capacity_cores: number
  memory_usage_bytes: number
  memory_capacity_bytes: number
  alerts_count: number
  risk_score: number
  top_namespaces: NamespaceUsage[]
}

export interface TimeseriesPoint {
  ts: number
  value: number
}

export interface TimeseriesSeries {
  name: string
  points: TimeseriesPoint[]
}

export interface TimeseriesResponse {
  metric: string
  range_minutes: number
  step_seconds: number
  series: TimeseriesSeries[]
}

export interface WorkloadItem {
  name: string
  namespace: string
  kind: ResourceKind
  status: string
  replicas?: number
  available_replicas?: number
  ready_ratio?: number
  restarts: number
  labels: Record<string, string>
}

export interface WorkloadListResponse {
  kind: ResourceKind
  total: number
  items: WorkloadItem[]
}

export interface ResourceEvent {
  type: string
  reason: string
  message: string
  timestamp: string
}

export interface ResourceMetricPoint {
  ts: number
  value: number
}

export interface ResourceMetricSeries {
  key: string
  label: string
  unit: string
  points: ResourceMetricPoint[]
}

export interface ResourceMetricsPanel {
  range_minutes: number
  step_seconds: number
  series: ResourceMetricSeries[]
}

export interface ResourceDetailResponse {
  item: WorkloadItem
  events: ResourceEvent[]
  logs: string[]
  metrics?: ResourceMetricsPanel
}

export interface AlertItem {
  id: string
  severity: 'P1' | 'P2' | 'P3'
  source: string
  title: string
  message: string
  namespace?: string
  start_time: string
  recommendation: string
}

export interface AlertListResponse {
  total: number
  items: AlertItem[]
}

export interface AuditLogItem {
  id: number
  user_id?: number
  action: string
  target_kind: string
  target_name: string
  namespace?: string
  status: string
  message?: string
  created_at: string
}

export interface AuditLogListResponse {
  total: number
  limit: number
  offset: number
  items: AuditLogItem[]
}

export interface AIAnalyzeTaskResponse {
  task_id: number
  status: string
}

export interface RootCauseCandidate {
  cause: string
  confidence: number
  evidence: string[]
}

export interface AIAnalyzeResult {
  summary: string
  recommendations: string[]
  root_causes: RootCauseCandidate[]
  risk_level: string
  generated_at: string
}

export interface AIAnalyzeTaskRead {
  task_id: number
  status: string
  created_at: string
  updated_at: string
  result?: AIAnalyzeResult
  error?: string
}
