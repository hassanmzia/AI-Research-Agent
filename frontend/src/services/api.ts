import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 - refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const res = await axios.post(`${API_BASE}/api/auth/token/refresh/`, {
            refresh,
          });
          localStorage.setItem('access_token', res.data.access);
          if (res.data.refresh) {
            localStorage.setItem('refresh_token', res.data.refresh);
          }
          error.config.headers.Authorization = `Bearer ${res.data.access}`;
          return api.request(error.config);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data: { username: string; email: string; password: string; password_confirm: string }) =>
    api.post('/auth/register/', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/token/', data),
  refresh: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
  me: () => api.get('/auth/me/'),
};

// Sessions
export const sessionsAPI = {
  list: (params?: Record<string, any>) => api.get('/sessions/', { params }),
  get: (id: string) => api.get(`/sessions/${id}/`),
  create: (data: {
    research_objective: string;
    title?: string;
    max_papers?: number;
    days_lookback?: number;
    custom_keywords?: string[];
  }) => api.post('/sessions/', data),
  cancel: (id: string) => api.post(`/sessions/${id}/cancel/`),
  export: (id: string, format: string) => api.post(`/sessions/${id}/export/`, { format }),
  logs: (id: string) => api.get(`/sessions/${id}/logs/`),
};

// Papers
export const papersAPI = {
  list: (params?: Record<string, any>) => api.get('/papers/', { params }),
  get: (id: string) => api.get(`/papers/${id}/`),
  bookmark: (id: string) => api.post(`/papers/${id}/bookmark/`),
  notes: (id: string, notes: string) => api.patch(`/papers/${id}/notes/`, { notes }),
};

// Evaluations
export const evaluationsAPI = {
  list: (params?: Record<string, any>) => api.get('/evaluations/', { params }),
  get: (id: string) => api.get(`/evaluations/${id}/`),
};

// Dashboard
export const dashboardAPI = {
  stats: () => api.get('/dashboard/'),
};

// Collections
export const collectionsAPI = {
  list: () => api.get('/collections/'),
  create: (data: { name: string; description?: string }) => api.post('/collections/', data),
  addPaper: (collectionId: string, paperId: string) =>
    api.post(`/collections/${collectionId}/add_paper/`, { paper_id: paperId }),
  removePaper: (collectionId: string, paperId: string) =>
    api.post(`/collections/${collectionId}/remove_paper/`, { paper_id: paperId }),
};

// Scheduled Research
export const scheduledAPI = {
  list: () => api.get('/scheduled/'),
  create: (data: Record<string, any>) => api.post('/scheduled/', data),
  toggle: (id: string) => api.post(`/scheduled/${id}/toggle/`),
  delete: (id: string) => api.delete(`/scheduled/${id}/`),
};

export default api;
