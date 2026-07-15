
import { apiClient } from "./client";
import type {
  DashboardSummary,
  Interaction,
  InteractionHistoryEntry,
  InteractionType,
  PaginatedInteractions,
  Sentiment,
} from "@/types";

export interface InteractionListParams {
  page?: number;
  page_size?: number;
  hcp_id?: string;
  user_id?: string;
  interaction_type?: InteractionType;
  sentiment?: Sentiment;
  date_from?: string;
  date_to?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export type InteractionCreatePayload = Omit<
  Interaction,
  "id" | "user_id" | "created_at" | "updated_at"
>;
export type InteractionUpdatePayload = Partial<InteractionCreatePayload>;

export const interactionApi = {
  list: (params: InteractionListParams = {}) =>
    apiClient.get<PaginatedInteractions>("/interactions", { params }).then((r) => r.data),

  get: (id: string) => apiClient.get<Interaction>(`/interactions/${id}`).then((r) => r.data),

  create: (payload: InteractionCreatePayload) =>
    apiClient.post<Interaction>("/interactions", payload).then((r) => r.data),

  update: (id: string, payload: InteractionUpdatePayload) =>
    apiClient.put<Interaction>(`/interactions/${id}`, payload).then((r) => r.data),

  remove: (id: string) => apiClient.delete(`/interactions/${id}`).then((r) => r.data),

  history: (id: string) =>
    apiClient.get<InteractionHistoryEntry[]>(`/interactions/${id}/history`).then((r) => r.data),

  dashboardSummary: (mineOnly = true) =>
    apiClient
      .get<DashboardSummary>("/interactions/dashboard/summary", { params: { mine_only: mineOnly } })
      .then((r) => r.data),
};
