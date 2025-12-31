import { createClient as createSupabaseClient } from "@/lib/supabase/client";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  code: string;
  details?: Record<string, unknown>;
  data?: Record<string, unknown>;

  constructor(status: number, error: Record<string, unknown>) {
    const errorObj = error.error as Record<string, unknown> | undefined;

    // Handle different error response formats
    let message = "An error occurred";

    if (errorObj?.message && typeof errorObj.message === "string") {
      message = errorObj.message;
    } else if (typeof error.detail === "string") {
      message = error.detail;
    } else if (Array.isArray(error.detail) && error.detail.length > 0) {
      // FastAPI validation error format
      const firstError = error.detail[0] as { msg?: string };
      message = firstError.msg || "Validation error";
    } else if (typeof error.message === "string") {
      message = error.message;
    }

    super(message);
    this.status = status;
    this.code = (errorObj?.code as string) || "UNKNOWN_ERROR";
    this.details = errorObj?.details as Record<string, unknown> | undefined;
    this.data = error;
  }
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async getAuthToken(): Promise<string | null> {
    const supabase = createSupabaseClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token ?? null;
  }

  async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = await this.getAuthToken();

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      });
    } catch (err) {
      // Network error (CORS, offline, server unreachable)
      throw new ApiError(0, {
        detail:
          err instanceof Error
            ? `Network error: ${err.message}`
            : "Network error: Unable to reach server",
      });
    }

    if (!response.ok) {
      let error: Record<string, unknown>;
      try {
        error = await response.json();
      } catch {
        error = { detail: `Server error: ${response.status} ${response.statusText}` };
      }
      throw new ApiError(response.status, error);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.fetch<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.fetch<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.fetch<T>(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.fetch<T>(endpoint, { method: "DELETE" });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
