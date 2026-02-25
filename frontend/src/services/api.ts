import axios from 'axios'
import type {
  AIAnalyzeTaskRead,
  AIAnalyzeTaskResponse,
  AuditLogListResponse,
  AlertListResponse,
  ClusterSummary,
  LoginResponse,
  ResourceDetailResponse,
  ResourceKind,
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

export async function getOverviewSummary(): Promise<ClusterSummary> {
  const { data } = await api.get<ClusterSummary>('/overview/summary')
  return data
}

export async function getTimeseries(params: {
  metric: string
  range_minutes: number
  step_seconds?: number
  namespace?: string
  workload?: string
}): Promise<TimeseriesResponse> {
  const { data } = await api.get<TimeseriesResponse>('/metrics/timeseries', { params })
  return data
}

export async function getResources(params: {
  kind: ResourceKind
  namespace?: string
  label_selector?: string
  status?: string
}): Promise<WorkloadListResponse> {
  const { kind, ...query } = params
  const { data } = await api.get<WorkloadListResponse>(`/resources/${kind}`, { params: query })
  return data
}

export async function getResourceDetail(params: {
  kind: ResourceKind
  name: string
  namespace: string
  log_lines?: number
  range_minutes?: number
  step_seconds?: number
}): Promise<ResourceDetailResponse> {
  const { kind, name, ...query } = params
  const { data } = await api.get<ResourceDetailResponse>(`/resources/${kind}/${name}/detail`, { params: query })
  return data
}

export async function scaleResource(params: {
  kind: ResourceKind
  name: string
  namespace: string
  replicas: number
}): Promise<void> {
  const { kind, name, ...body } = params
  await api.post(`/resources/${kind}/${name}/scale`, body)
}

export async function rolloutRestart(params: {
  kind: ResourceKind
  name: string
  namespace: string
}): Promise<void> {
  const { kind, name, ...body } = params
  await api.post(`/resources/${kind}/${name}/rollout-restart`, body)
}

export async function getAlerts(params?: {
  namespace?: string
  limit?: number
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

export async function createAnalyzeTask(payload: Record<string, unknown>): Promise<AIAnalyzeTaskResponse> {
  const { data } = await api.post<AIAnalyzeTaskResponse>('/ai/analyze', payload)
  return data
}

export async function getAnalyzeTask(taskId: number): Promise<AIAnalyzeTaskRead> {
  const { data } = await api.get<AIAnalyzeTaskRead>(`/ai/tasks/${taskId}`)
  return data
}

export function getWsOverviewUrl(token: string): string {
  const base =
    import.meta.env.VITE_OVERVIEW_WS_URL ??
    'ws://localhost:8000/ws/overview'
  return `${base}?token=${encodeURIComponent(token)}`
}
