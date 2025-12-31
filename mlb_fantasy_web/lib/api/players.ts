import { apiClient, ApiError } from "./client";
import type { Player } from "./types";

export interface ListPlayersParams {
  limit?: number;
  offset?: number;
  status?: string;
  team?: string;
  position?: string;
}

export interface PlayersListResponse {
  players: Player[];
  total: number;
}

export async function listPlayers(
  params: ListPlayersParams = {}
): Promise<PlayersListResponse> {
  const searchParams = new URLSearchParams();

  if (params.limit) searchParams.set("limit", String(params.limit));
  if (params.offset) searchParams.set("offset", String(params.offset));
  if (params.status) searchParams.set("status", params.status);
  if (params.team) searchParams.set("team", params.team);
  if (params.position) searchParams.set("position", params.position);

  const query = searchParams.toString();
  const url = `/api/v1/players${query ? `?${query}` : ""}`;

  return apiClient.get<PlayersListResponse>(url);
}

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
): Promise<PlayersListResponse> {
  return apiClient.get<PlayersListResponse>(
    `/api/v1/players/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
}
