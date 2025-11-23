import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  LoginCredentials,
  RegisterData,
  TokenResponse,
  User,
  HealthProfile,
  ChatRequest,
  ChatResponse,
  Conversation
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                refresh_token: refreshToken,
              });

              localStorage.setItem('access_token', data.access_token);
              this.client.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

              return this.client(originalRequest);
            }
          } catch (refreshError) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<User> {
    const response = await this.client.post('/api/v1/auth/register', data);
    return response.data;
  }

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.client.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Health Profile endpoints
  async getHealthProfile(): Promise<HealthProfile> {
    const response = await this.client.get('/api/v1/profile/health-profile');
    return response.data;
  }

  async createHealthProfile(data: Partial<HealthProfile>): Promise<HealthProfile> {
    const response = await this.client.post('/api/v1/profile/health-profile', data);
    return response.data;
  }

  async updateHealthProfile(data: Partial<HealthProfile>): Promise<HealthProfile> {
    const response = await this.client.put('/api/v1/profile/health-profile', data);
    return response.data;
  }

  // Chat endpoints (REST fallback)
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post('/api/v1/chat/message', request);
    return response.data;
  }

  async getConversationHistory(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/api/v1/chat/history/${sessionId}`);
    return response.data;
  }

  async deleteConversation(sessionId: string): Promise<void> {
    await this.client.delete(`/api/v1/chat/history/${sessionId}`);
  }

  // Emergency check
  async checkEmergency(message: string): Promise<any> {
    const response = await this.client.get('/api/v1/chat/emergency-check', {
      params: { message },
    });
    return response.data;
  }
}

export const api = new ApiService();
export default api;
