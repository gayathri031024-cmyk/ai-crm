import { apiClient } from "./client";
import type { HCP, HCPTier, PaginatedHCPs } from "@/types";

export interface HCPListParams {
  page?: number;
  page_size?: number;
  search?: string;
  tier?: HCPTier;
  city?: string;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export type HCPCreatePayload = Omit<HCP, "id" | "created_at" | "updated_at">;
export type HCPUpdatePayload = Partial<HCPCreatePayload>;

export const hcpApi = {
  list: (params: HCPListParams = {}) =>
    apiClient.get<PaginatedHCPs>("/hcps", { params }).then((r) => r.data),

  get: (id: string) => apiClient.get<HCP>(`/hcps/${id}`).then((r) => r.data),

  create: (payload: HCPCreatePayload) =>
    apiClient.post<HCP>("/hcps", payload).then((r) => r.data),

  update: (id: string, payload: HCPUpdatePayload) =>
    apiClient.put<HCP>(`/hcps/${id}`, payload).then((r) => r.data),

  remove: (id: string) => apiClient.delete(`/hcps/${id}`).then((r) => r.data),
};
