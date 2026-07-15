import { z } from "zod";

export const INTERACTION_TYPES = ["visit", "call", "email", "virtual_meeting", "event"] as const;
export const SENTIMENTS = ["positive", "neutral", "negative"] as const;

export const logInteractionSchema = z
  .object({
    hcp_id: z.string().min(1, "Select an HCP"),
    interaction_type: z.enum(INTERACTION_TYPES),
    visit_date: z.string().min(1, "Visit date is required"),
    follow_up_date: z.string().optional().or(z.literal("")),
    discussion_summary: z.string().max(4000).optional().or(z.literal("")),
    products_discussed: z.array(z.string()).optional(),
    samples_given: z.coerce.number().int().min(0, "Cannot be negative").max(100000),
    sentiment: z.enum(SENTIMENTS).optional(),
    next_action: z.string().max(255).optional().or(z.literal("")),
    notes: z.string().max(4000).optional().or(z.literal("")),
  })
  .refine(
    (data) => {
      if (!data.follow_up_date) return true;
      return new Date(data.follow_up_date) >= new Date(data.visit_date.slice(0, 10));
    },
    { message: "Follow-up date cannot be before the visit date", path: ["follow_up_date"] }
  );

export type LogInteractionFormValues = z.infer<typeof logInteractionSchema>;

export const DEFAULT_FORM_VALUES: LogInteractionFormValues = {
  hcp_id: "",
  interaction_type: "visit",
  visit_date: new Date().toISOString().slice(0, 16),
  follow_up_date: "",
  discussion_summary: "",
  products_discussed: [],
  samples_given: 0,
  sentiment: undefined,
  next_action: "",
  notes: "",
};
