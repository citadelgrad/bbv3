import { apiClient, ApiError } from "./client";
import type {
  JobStatusResponse,
  ResearchResponse,
  ResearchResponseAmbiguous,
  ScoutingReport,
} from "./types";

export async function researchPlayer(
  playerName: string
): Promise<ResearchResponse> {
  try {
    return await apiClient.post<ResearchResponse>("/api/v1/scouting/research", {
      player_name: playerName,
    });
  } catch (error) {
    // Handle 300 Multiple Choices (ambiguous player)
    if (error instanceof ApiError && error.status === 300 && error.data) {
      const ambiguous = error.data as unknown as ResearchResponseAmbiguous;
      if (ambiguous && ambiguous.status === "ambiguous") {
        return ambiguous;
      }
    }
    throw error;
  }
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

export async function getReportByPlayerName(
  playerName: string
): Promise<ScoutingReport | null> {
  try {
    return await apiClient.get<ScoutingReport>(
      `/api/v1/scouting/reports/by-name/${encodeURIComponent(playerName)}`
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
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
