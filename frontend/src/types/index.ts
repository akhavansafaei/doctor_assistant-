// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface HealthProfile {
  id: number;
  user_id: number;
  height_cm?: number;
  weight_kg?: number;
  blood_type?: string;
  chronic_conditions?: string[];
  allergies?: {
    drug?: string[];
    food?: string[];
    environmental?: string[];
  };
  current_medications?: Medication[];
  past_surgeries?: Surgery[];
  family_history?: Record<string, string[]>;
  smoking_status?: string;
  alcohol_consumption?: string;
  exercise_frequency?: string;
  diet_type?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  created_at: string;
  updated_at: string;
}

export interface Medication {
  name: string;
  dose?: string;
  frequency?: string;
  started_at?: string;
}

export interface Surgery {
  name: string;
  date: string;
  notes?: string;
}

// Chat types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  streaming?: boolean;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  agent_type?: string;
  severity?: string;
  emergency?: boolean;
  sources?: Source[];
  confidence_score?: number;
}

export interface Source {
  title: string;
  text: string;
  source: string;
  relevance_score: number;
}

export interface Conversation {
  id: string;
  session_id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  message_count: number;
  last_message?: string;
}

// WebSocket types
export interface WSMessage {
  type: 'connection' | 'token' | 'stream_start' | 'stream_end' | 'status' | 'error' | 'context_retrieved';
  content?: string;
  status?: string;
  message?: string;
  session_id?: string;
  timestamp?: string;
  metadata?: any;
  details?: any;
  sources?: Source[];
  error_type?: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Settings types
export interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  notifications: boolean;
  sound_enabled: boolean;
  auto_play_responses: boolean;
  show_sources: boolean;
  enable_agents: boolean;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  enable_agents?: boolean;
  patient_profile?: Partial<HealthProfile>;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  agent_type?: string;
  severity_level?: string;
  emergency_detected: boolean;
  sources?: Source[];
  timestamp: string;
}
