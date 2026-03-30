// src/api/client.js
import axios from 'axios';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '');

const api = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json' },
});

// Attach JWT access token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
    (res) => res,
    async (err) => {
        const original = err.config;
        if (err.response?.status === 401 && !original._retry) {
            original._retry = true;
            const refresh = localStorage.getItem('refresh_token');
            if (refresh) {
                try {
                    const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
                        refresh,
                    });
                    localStorage.setItem('access_token', data.access);
                    original.headers.Authorization = `Bearer ${data.access}`;
                    return api(original);
                } catch {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }
        }
        return Promise.reject(err);
    }
);

export default api;

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
    login: (username, password) =>
        axios.post(`${BASE_URL}/auth/token/`, { username, password }),
    refresh: (refresh) =>
        axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh }),
};

// ── Projects ──────────────────────────────────────────────────────────────────
export const projectsApi = {
    list: (params) => api.get('/projects/', { params }),
    get: (id) => api.get(`/projects/${id}/`),
    create: (data) => api.post('/projects/', data),
    update: (id, data) => api.patch(`/projects/${id}/`, data),
    delete: (id) => api.delete(`/projects/${id}/`),
    tasks: (id, params) => api.get(`/projects/${id}/tasks/`, { params }),
    stats: (id) => api.get(`/projects/${id}/stats/`),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────
export const tasksApi = {
    list: (params) => api.get('/tasks/', { params }),
    get: (id) => api.get(`/tasks/${id}/`),
    create: (data) => api.post('/tasks/', data),
    update: (id, data) => api.patch(`/tasks/${id}/`, data),
    delete: (id) => api.delete(`/tasks/${id}/`),
    setStatus: (id, status) =>
        api.patch(`/tasks/${id}/set_status/`, { status }),
    myTasks: () => api.get('/tasks/my/'),
};

// ── Activities ────────────────────────────────────────────────────────────────
export const activitiesApi = {
    list: (params) => api.get('/activities/', { params }),
};

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
    list: (params) => api.get('/users/', { params }),
    me: () => api.get('/users/me/'),
};
