import { create } from 'zustand';
import { User } from '../types';
import { authAPI } from '../services/api';
import wsService from '../services/websocket';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: { username: string; email: string; password: string; password_confirm: string }) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (username, password) => {
    const res = await authAPI.login({ username, password });
    localStorage.setItem('access_token', res.data.access);
    localStorage.setItem('refresh_token', res.data.refresh);
    set({ isAuthenticated: true });

    // Connect WebSocket
    wsService.connect(res.data.access);

    // Load user profile
    const userRes = await authAPI.me();
    set({ user: userRes.data });
  },

  register: async (data) => {
    await authAPI.register(data);
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    wsService.disconnect();
    set({ user: null, isAuthenticated: false });
  },

  loadUser: async () => {
    set({ isLoading: true });
    try {
      const res = await authAPI.me();
      set({ user: res.data, isAuthenticated: true });

      // Connect WebSocket
      const token = localStorage.getItem('access_token');
      if (token) wsService.connect(token);
    } catch {
      set({ isAuthenticated: false, user: null });
    } finally {
      set({ isLoading: false });
    }
  },
}));
