import { apiClient, ApiError } from "./client";
import type { Player } from "./types";

export async function getPlayerById(playerId: string): Promise<Player | null> {
  try {
    return await apiClient.get<Player>(`/api/v1/players/${playerId}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function getPlayerByMlbId(mlbId: number): Promise<Player | null> {
  try {
    return await apiClient.get<Player>(`/api/v1/players/by-mlb-id/${mlbId}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function searchPlayers(
  query: string,
  limit = 20
): Promise<{ players: Player[]; total: number }> {
  return apiClient.get<{ players: Player[]; total: number }>(
    `/api/v1/players/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
}
