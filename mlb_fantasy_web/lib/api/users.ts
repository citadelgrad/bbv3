import { apiClient } from "./client";
import type { UserProfile, UserProfileUpdate } from "./types";

export async function getCurrentUser(): Promise<UserProfile> {
  return apiClient.get<UserProfile>("/api/v1/users/me");
}

export async function updateCurrentUser(
  data: UserProfileUpdate
): Promise<UserProfile> {
  return apiClient.put<UserProfile>("/api/v1/users/me", data);
}
