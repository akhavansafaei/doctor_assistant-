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

export interface ClientProfile {
  id?: number;
  user_id?: number;
  age?: number;
  gender?: string;
  occupation?: string;
  employer?: string;
  citizenship?: string;
  marital_status?: string;
  legal_areas_of_interest?: string[];
  active_legal_matters?: LegalMatter[];
  previous_legal_issues?: LegalIssue[];
  legal_restrictions?: LegalRestriction[];
  business_entities?: BusinessEntity[];
  financial_concerns?: string[];
  preferred_communication?: string;
  availability?: Record<string, string[]>;
  emergency_contact?: {
    name?: string;
    phone?: string;
    relationship?: string;
  };
  created_at?: string;
  updated_at?: string;
}

export interface LegalMatter {
  description: string;
  type?: string;
  status?: string;
  started_at?: string;
}

export interface LegalIssue {
  type: string;
  year?: string;
  date?: string;
  notes?: string;
}

export interface LegalRestriction {
  type: string;
  details?: string;
  expires_at?: string;
}

export interface BusinessEntity {
  name: string;
  type?: string;
  ownership_percentage?: number;
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
  urgency?: string;
  urgent_matter?: boolean;
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
  type: 'connection' | 'token' | 'stream_start' | 'stream_end' | 'status' | 'error' | 'context_retrieved' | 'onboarding_question' | 'onboarding_complete' | 'profile_saved';
  content?: string;
  status?: string;
  message?: string;
  question?: string;
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
  client_profile?: Partial<ClientProfile>;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  agent_type?: string;
  urgency_level?: string;
  urgent_matter_detected: boolean;
  sources?: Source[];
  timestamp: string;
}
