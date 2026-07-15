
import { apiClient } from "./client";
import type { ChatResponse, ConversationDetail, ConversationSummary } from "@/types";

export const chatApi = {
  sendMessage: (message: string, conversationId?: string | null) =>
    apiClient
      .post<ChatResponse>("/chat", { message, conversation_id: conversationId ?? null })
      .then((r) => r.data),

  history: () => apiClient.get<ConversationSummary[]>("/history").then((r) => r.data),

  conversation: (id: string) =>
    apiClient.get<ConversationDetail>(`/history/${id}`).then((r) => r.data),
};
