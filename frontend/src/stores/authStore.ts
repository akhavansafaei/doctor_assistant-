import { create } from 'zustand';
import { User, LoginCredentials, RegisterData, ClientProfile } from '@/types';
import api from '@/services/api';

interface AuthState {
  user: User | null;
  clientProfile: ClientProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  loadClientProfile: () => Promise<void>;
  updateClientProfile: (data: Partial<ClientProfile>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  clientProfile: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (credentials) => {
    try {
      set({ isLoading: true, error: null });
      await api.login(credentials);
      await get().loadUser();
      set({ isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
      throw error;
    }
  },

  register: async (data) => {
    try {
      set({ isLoading: true, error: null });
      await api.register(data);
      // Auto-login after registration
      await get().login({ username: data.username, password: data.password });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      await api.logout();
      set({
        user: null,
        clientProfile: null,
        isAuthenticated: false,
        error: null,
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  },

  loadUser: async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        set({ isAuthenticated: false });
        return;
      }

      const user = await api.getCurrentUser();
      set({ user, isAuthenticated: true });

      // Load client profile
      await get().loadClientProfile();
    } catch (error) {
      console.error('Load user error:', error);
      set({ isAuthenticated: false });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  loadClientProfile: async () => {
    try {
      const clientProfile = await api.getClientProfile();
      set({ clientProfile });
    } catch (error: any) {
      // If profile doesn't exist yet, that's okay
      if (error.response?.status !== 404) {
        console.error('Load client profile error:', error);
      }
    }
  },

  updateClientProfile: async (data) => {
    try {
      set({ isLoading: true });
      const clientProfile = get().clientProfile
        ? await api.updateClientProfile(data)
        : await api.createClientProfile(data);

      set({ clientProfile, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update client profile',
        isLoading: false,
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
