import axios from 'axios'
import type {
  AIAnalyzeTaskRead,
  AIAnalyzeTaskResponse,
  AlertListResponse,
  ClusterSummary,
  LoginResponse,
  ResourceKind,
  TimeseriesResponse,
  UserRead,
  WorkloadListResponse,
} from '../types/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kubeaico_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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
