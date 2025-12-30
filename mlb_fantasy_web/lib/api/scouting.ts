import { apiClient } from "./client";
import type {
  JobStatusResponse,
  ResearchResponse,
  ScoutingReport,
} from "./types";

export async function researchPlayer(
  playerName: string
): Promise<ResearchResponse> {
  return apiClient.post<ResearchResponse>("/api/v1/scouting/research", {
    player_name: playerName,
  });
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return apiClient.get<JobStatusResponse>(`/api/v1/scouting/jobs/${jobId}`);
}

export async function getReportByPlayer(
  playerName: string
): Promise<ScoutingReport> {
  return apiClient.get<ScoutingReport>(
    `/api/v1/scouting/reports/${encodeURIComponent(playerName)}`
  );
}

export async function listReports(
  limit = 20,
  offset = 0
): Promise<{ reports: ScoutingReport[]; total: number }> {
  return apiClient.get<{ reports: ScoutingReport[]; total: number }>(
    `/api/v1/scouting/reports?limit=${limit}&offset=${offset}`
  );
}

// Helper to poll for job completion
export async function waitForJobCompletion(
  jobId: string,
  maxAttempts = 60,
  intervalMs = 2000
): Promise<JobStatusResponse> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const status = await getJobStatus(jobId);

    if (status.status === "success" || status.status === "failed") {
      return status;
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new Error("Job timed out");
}
