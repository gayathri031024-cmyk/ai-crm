// ---- Shared enums, mirroring backend/app/models & schemas ----

export type UserRole = "rep" | "manager" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  territory: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export type HCPTier = "A" | "B" | "C";

export interface HCP {
  id: string;
  full_name: string;
  specialization: string | null;
  hospital_name: string | null;
  phone: string | null;
  email: string | null;
  city: string | null;
  tier: HCPTier;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export type InteractionType = "visit" | "call" | "email" | "virtual_meeting" | "event";
export type Sentiment = "positive" | "neutral" | "negative";
export type CreatedVia = "form" | "ai_chat";

export interface Interaction {
  id: string;
  hcp_id: string;
  user_id: string;
  interaction_type: InteractionType;
  visit_date: string;
  follow_up_date: string | null;
  discussion_summary: string | null;
  products_discussed: string[] | null;
  samples_given: number;
  sentiment: Sentiment | null;
  next_action: string | null;
  notes: string | null;
  created_via: CreatedVia;
  created_at: string;
  updated_at: string;
}

export interface InteractionHistoryEntry {
  id: string;
  interaction_id: string;
  changed_by: string;
  change_source: "form" | "ai_chat";
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  changed_at: string;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedInteractions {
  items: Interaction[];
  meta: PaginationMeta;
}

export interface PaginatedHCPs {
  items: HCP[];
  meta: PaginationMeta;
}

export interface DashboardSummary {
  todays_visits?: number;
  pending_follow_ups?: number;
  total_interactions?: number;
  positive_sentiment_pct?: number;
  [key: string]: number | undefined;
}

// ---- Chat ----

export type ChatRole = "user" | "assistant" | "tool" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  tool_name: string | null;
  tool_output: Record<string, unknown> | null;
  model_used: string | null;
  created_at: string;
}

export interface ChatResponse {
  conversation_id: string;
  reply: string;
  messages: ChatMessage[];
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  started_at: string;
  ended_at: string | null;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

export interface ApiError {
  detail: string | { msg: string; loc?: (string | number)[] }[];
}
