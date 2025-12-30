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

// Scouting Report Types
export interface GroundingSource {
  title: string;
  uri: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  response_tokens: number;
  total_tokens: number;
  estimated_cost: string;
}

export interface ScoutingReport {
  id: string;
  player_name: string;
  player_name_normalized: string;
  summary: string;
  recent_stats: string;
  injury_status: string;
  fantasy_outlook: string;
  detailed_analysis: string;
  sources: GroundingSource[];
  token_usage: TokenUsage;
  created_at: string;
  expires_at: string;
}

export interface ResearchResponsePending {
  status: "pending";
  job_id: string;
  message: string;
}

export interface ResearchResponseComplete {
  status: "cached" | "generated";
  report: ScoutingReport;
}

export type ResearchResponse = ResearchResponsePending | ResearchResponseComplete;

export interface JobStatusResponse {
  job_id: string;
  status: "pending" | "running" | "success" | "failed";
  result?: {
    status: string;
    report_id: string;
    player_name: string;
    summary: string;
    recent_stats: string;
    injury_status: string;
    fantasy_outlook: string;
    detailed_analysis: string;
    sources: GroundingSource[];
    token_usage: TokenUsage;
    created_at: string;
    expires_at: string;
  };
  error?: string;
}
