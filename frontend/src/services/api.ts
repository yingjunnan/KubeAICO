import axios from 'axios'
import type {
  AIAnalyzeTaskRead,
  AIAnalyzeTaskResponse,
  AuditLogListResponse,
  AlertListResponse,
  ClusterSummary,
  ClusterConnectionTestResponse,
  LoginResponse,
  ManagedCluster,
  ManagedClusterListResponse,
  ResourceDetailResponse,
  ResourceKind,
  ResourceLogsResponse,
  TimeseriesResponse,
  UserRead,
  WorkloadListResponse,
} from '../types/api'

const TOKEN_KEY = 'kubeaico_token'
let redirectingToLogin = false

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function shouldIgnoreAuthRedirect(url: unknown): boolean {
  const value = String(url ?? '')
  return value.includes('/auth/login')
}

export function clearAuthAndRedirectToLogin(): void {
  localStorage.removeItem(TOKEN_KEY)

  if (window.location.pathname === '/login') {
    return
  }
  if (redirectingToLogin) {
    return
  }

  redirectingToLogin = true
  window.location.assign('/login')
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 401 && !shouldIgnoreAuthRedirect(error?.config?.url)) {
      clearAuthAndRedirectToLogin()
    }
    return Promise.reject(error)
  },
)

export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', { username, password })
  return data
}

export async function me(): Promise<UserRead> {
  const { data } = await api.get<UserRead>('/auth/me')
  return data
}

export async function getOverviewSummary(params?: { cluster_id?: string }): Promise<ClusterSummary> {
  const { data } = await api.get<ClusterSummary>('/overview/summary', { params })
  return data
}

export async function getTimeseries(params: {
  metric: string
  range_minutes: number
  step_seconds?: number
  namespace?: string
  workload?: string
  cluster_id?: string
}): Promise<TimeseriesResponse> {
  const { data } = await api.get<TimeseriesResponse>('/metrics/timeseries', { params })
  return data
}

export async function getResources(params: {
  kind: ResourceKind
  namespace?: string
  label_selector?: string
  status?: string
  cluster_id?: string
}): Promise<WorkloadListResponse> {
  const { kind, ...query } = params
  const { data } = await api.get<WorkloadListResponse>(`/resources/${kind}`, { params: query })
  return data
}

export async function getResourceDetail(params: {
  kind: ResourceKind
  name: string
  namespace: string
  range_minutes?: number
  step_seconds?: number
  cluster_id?: string
}): Promise<ResourceDetailResponse> {
  const { kind, name, ...query } = params
  const { data } = await api.get<ResourceDetailResponse>(`/resources/${kind}/${name}/detail`, { params: query })
  return data
}

export async function getResourceLogs(params: {
  kind: ResourceKind
  name: string
  namespace: string
  log_lines?: number
  cluster_id?: string
}): Promise<ResourceLogsResponse> {
  const { kind, name, ...query } = params
  const { data } = await api.get<ResourceLogsResponse>(`/resources/${kind}/${name}/logs`, { params: query })
  return data
}

export async function scaleResource(params: {
  kind: ResourceKind
  name: string
  namespace: string
  replicas: number
  cluster_id?: string
}): Promise<void> {
  const { kind, name, ...body } = params
  await api.post(`/resources/${kind}/${name}/scale`, body)
}

export async function rolloutRestart(params: {
  kind: ResourceKind
  name: string
  namespace: string
  cluster_id?: string
}): Promise<void> {
  const { kind, name, ...body } = params
  await api.post(`/resources/${kind}/${name}/rollout-restart`, body)
}

export async function getAlerts(params?: {
  namespace?: string
  limit?: number
  cluster_id?: string
}): Promise<AlertListResponse> {
  const { data } = await api.get<AlertListResponse>('/alerts', { params })
  return data
}

export async function getAuditLogs(params?: {
  limit?: number
  offset?: number
  action?: string
  kind?: string
  namespace?: string
}): Promise<AuditLogListResponse> {
  const { data } = await api.get<AuditLogListResponse>('/audit/logs', { params })
  return data
}

export async function getClusters(): Promise<ManagedClusterListResponse> {
  const { data } = await api.get<ManagedClusterListResponse>('/clusters')
  return data
}

export async function createCluster(payload: {
  name: string
  cluster_id: string
  k8s_api_url: string
  prometheus_url?: string
  k8s_bearer_token?: string
  is_active: boolean
  description?: string
}): Promise<ManagedCluster> {
  const { data } = await api.post<ManagedCluster>('/clusters', payload)
  return data
}

export async function updateCluster(params: {
  cluster_pk: number
  payload: {
    name?: string
    cluster_id?: string
    k8s_api_url?: string
    prometheus_url?: string
    k8s_bearer_token?: string
    is_active?: boolean
    description?: string
  }
}): Promise<ManagedCluster> {
  const { cluster_pk, payload } = params
  const { data } = await api.put<ManagedCluster>(`/clusters/${cluster_pk}`, payload)
  return data
}

export async function deleteCluster(clusterPk: number): Promise<void> {
  await api.delete(`/clusters/${clusterPk}`)
}

export async function testClusterConnectionDraft(payload: {
  k8s_api_url: string
  prometheus_url?: string
  k8s_bearer_token?: string
}): Promise<ClusterConnectionTestResponse> {
  const { data } = await api.post<ClusterConnectionTestResponse>('/clusters/test', payload)
  return data
}

export async function testClusterConnection(clusterPk: number): Promise<ClusterConnectionTestResponse> {
  const { data } = await api.post<ClusterConnectionTestResponse>(`/clusters/${clusterPk}/test`)
  return data
}

export async function createAnalyzeTask(payload: Record<string, unknown>): Promise<AIAnalyzeTaskResponse> {
  const { data } = await api.post<AIAnalyzeTaskResponse>('/ai/analyze', payload)
  return data
}

export async function getAnalyzeTask(taskId: number): Promise<AIAnalyzeTaskRead> {
  const { data } = await api.get<AIAnalyzeTaskRead>(`/ai/tasks/${taskId}`)
  return data
}

export function getWsOverviewUrl(token: string, clusterId?: string): string {
  const base =
    import.meta.env.VITE_OVERVIEW_WS_URL ??
    'ws://localhost:8000/ws/overview'
  const params = new URLSearchParams({ token })
  if (clusterId) {
    params.set('cluster_id', clusterId)
  }
  return `${base}?${params.toString()}`
}
