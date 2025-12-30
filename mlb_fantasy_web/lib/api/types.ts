// Match the backend schemas exactly

export interface UserProfile {
  id: string;
  supabase_user_id: string;
  username: string;
  display_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  username?: string;
  display_name?: string | null;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    request_id?: string;
  };
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  checks: {
    database: {
      status: string;
      latency_ms: number;
    };
  };
}
