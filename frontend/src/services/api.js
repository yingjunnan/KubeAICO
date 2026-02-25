import axios from 'axios';
const TOKEN_KEY = 'kubeaico_token';
let redirectingToLogin = false;
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
    timeout: 15000,
});
api.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
function shouldIgnoreAuthRedirect(url) {
    const value = String(url ?? '');
    return value.includes('/auth/login');
}
export function clearAuthAndRedirectToLogin() {
    localStorage.removeItem(TOKEN_KEY);
    if (window.location.pathname === '/login') {
        return;
    }
    if (redirectingToLogin) {
        return;
    }
    redirectingToLogin = true;
    window.location.assign('/login');
}
api.interceptors.response.use((response) => response, (error) => {
    const status = error?.response?.status;
    if (status === 401 && !shouldIgnoreAuthRedirect(error?.config?.url)) {
        clearAuthAndRedirectToLogin();
    }
    return Promise.reject(error);
});
export async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password });
    return data;
}
export async function me() {
    const { data } = await api.get('/auth/me');
    return data;
}
export async function getOverviewSummary() {
    const { data } = await api.get('/overview/summary');
    return data;
}
export async function getTimeseries(params) {
    const { data } = await api.get('/metrics/timeseries', { params });
    return data;
}
export async function getResources(params) {
    const { kind, ...query } = params;
    const { data } = await api.get(`/resources/${kind}`, { params: query });
    return data;
}
export async function getResourceDetail(params) {
    const { kind, name, ...query } = params;
    const { data } = await api.get(`/resources/${kind}/${name}/detail`, { params: query });
    return data;
}
export async function scaleResource(params) {
    const { kind, name, ...body } = params;
    await api.post(`/resources/${kind}/${name}/scale`, body);
}
export async function rolloutRestart(params) {
    const { kind, name, ...body } = params;
    await api.post(`/resources/${kind}/${name}/rollout-restart`, body);
}
export async function getAlerts(params) {
    const { data } = await api.get('/alerts', { params });
    return data;
}
export async function getAuditLogs(params) {
    const { data } = await api.get('/audit/logs', { params });
    return data;
}
export async function createAnalyzeTask(payload) {
    const { data } = await api.post('/ai/analyze', payload);
    return data;
}
export async function getAnalyzeTask(taskId) {
    const { data } = await api.get(`/ai/tasks/${taskId}`);
    return data;
}
export function getWsOverviewUrl(token) {
    const base = import.meta.env.VITE_OVERVIEW_WS_URL ??
        'ws://localhost:8000/ws/overview';
    return `${base}?token=${encodeURIComponent(token)}`;
}
