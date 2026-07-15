import { useEffect, useRef } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Box,
  Grid,
  TextField,
  MenuItem,
  Button,
  Autocomplete,
  Chip,
  Paper,
  Typography,
  Stack,
} from "@mui/material";
import RestartAltRoundedIcon from "@mui/icons-material/RestartAltRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import {
  DEFAULT_FORM_VALUES,
  INTERACTION_TYPES,
  LogInteractionFormValues,
  SENTIMENTS,
  logInteractionSchema,
} from "./logInteractionSchema";
import HcpAutocomplete from "./HcpAutocomplete";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { createInteraction, updateInteraction } from "@/features/interactions/interactionSlice";
import { pushToast } from "@/features/ui/uiSlice";
import type { Interaction } from "@/types";

const TYPE_LABELS: Record<string, string> = {
  visit: "In-person Visit",
  call: "Phone Call",
  email: "Email",
  virtual_meeting: "Virtual Meeting",
  event: "Event",
};

const COMMON_PRODUCTS = ["Cardiozen", "NeuroClear", "PulmoEase", "GlucoBalance", "Dermafresh"];

interface LogInteractionFormProps {
  editingInteraction?: Interaction | null;
  onDone?: () => void;
}

export default function LogInteractionForm({ editingInteraction, onDone }: LogInteractionFormProps) {
  const dispatch = useAppDispatch();
  const isEditing = !!editingInteraction;

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<LogInteractionFormValues>({
    resolver: zodResolver(logInteractionSchema),
    defaultValues: editingInteraction
      ? {
          hcp_id: editingInteraction.hcp_id,
          interaction_type: editingInteraction.interaction_type,
          visit_date: editingInteraction.visit_date.slice(0, 16),
          follow_up_date: editingInteraction.follow_up_date ?? "",
          discussion_summary: editingInteraction.discussion_summary ?? "",
          products_discussed: editingInteraction.products_discussed ?? [],
          samples_given: editingInteraction.samples_given,
          sentiment: editingInteraction.sentiment ?? undefined,
          next_action: editingInteraction.next_action ?? "",
          notes: editingInteraction.notes ?? "",
        }
      : DEFAULT_FORM_VALUES,
  });

  // ---------------------------------------------------------------------
  // Auto-fill from a successful AI chat "log_interaction" tool call.
  // Watches the chat message list; when a new successful log_interaction
  // result appears, populate the form with its extracted data.
  // ---------------------------------------------------------------------
  const chatMessages = useAppSelector((s) => s.chat.messages);
  const appliedMessageIdRef = useRef<string | null>(null);

  useEffect(() => {
    for (let i = chatMessages.length - 1; i >= 0; i--) {
      const m = chatMessages[i];
      if (m.role === "tool" && m.tool_name === "log_interaction") {
        const output = m.tool_output as { status?: string; data?: Record<string, any> } | null;
        if (output?.status === "ok" && output.data && m.id !== appliedMessageIdRef.current) {
          appliedMessageIdRef.current = m.id;
          const d = output.data;
          reset({
            hcp_id: d.hcp_id ?? "",
            interaction_type: d.interaction_type ?? "visit",
            visit_date: d.visit_date ? d.visit_date.slice(0, 16) : DEFAULT_FORM_VALUES.visit_date,
            follow_up_date: d.follow_up_date ?? "",
            discussion_summary: d.discussion_summary ?? "",
            products_discussed: d.products_discussed ?? [],
            samples_given: d.samples_given ?? 0,
            sentiment: d.sentiment ?? undefined,
            next_action: d.next_action ?? "",
            notes: "",
          });
        }
        break;
      }
    }
  }, [chatMessages, reset]);

  const onSubmit = async (values: LogInteractionFormValues) => {
    const payload = {
      hcp_id: values.hcp_id,
      interaction_type: values.interaction_type,
      visit_date: new Date(values.visit_date).toISOString(),
      follow_up_date: values.follow_up_date || null,
      discussion_summary: values.discussion_summary || null,
      products_discussed: values.products_discussed?.length ? values.products_discussed : null,
      samples_given: values.samples_given,
      sentiment: values.sentiment || null,
      next_action: values.next_action || null,
      notes: values.notes || null,
      created_via: "form" as const,
    };

    const action = isEditing
      ? updateInteraction({ id: editingInteraction!.id, payload })
      : createInteraction(payload);

    const result = await dispatch(action as any);

    if ((result as any).error) {
      dispatch(pushToast("Could not save interaction. Please check the form.", "error"));
      return;
    }

    dispatch(pushToast(isEditing ? "Interaction updated." : "Interaction logged successfully.", "success"));
    if (!isEditing) reset(DEFAULT_FORM_VALUES);
    onDone?.();
  };

  return (
    <Paper elevation={0} sx={{ p: 4, border: "1px solid #E2E8F0" }}>
      <Typography variant="h6" sx={{ mb: 3 }}>
        {isEditing ? "Edit Interaction" : "Log a New Interaction"}
      </Typography>

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Grid container spacing={2.5}>
          <Grid item xs={12} md={6}>
            <Controller
              name="hcp_id"
              control={control}
              render={({ field }) => (
                <HcpAutocomplete
                  value={field.value}
                  onChange={field.onChange}
                  error={!!errors.hcp_id}
                  helperText={errors.hcp_id?.message}
                />
              )}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Controller
              name="interaction_type"
              control={control}
              render={({ field }) => (
                <TextField {...field} select label="Interaction Type" fullWidth>
                  {INTERACTION_TYPES.map((t) => (
                    <MenuItem key={t} value={t}>
                      {TYPE_LABELS[t]}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Visit / Interaction Date"
              type="datetime-local"
              fullWidth
              InputLabelProps={{ shrink: true }}
              {...register("visit_date")}
              error={!!errors.visit_date}
              helperText={errors.visit_date?.message}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Follow-up Date (optional)"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              {...register("follow_up_date")}
              error={!!errors.follow_up_date}
              helperText={errors.follow_up_date?.message}
            />
          </Grid>

          <Grid item xs={12}>
            <Controller
              name="products_discussed"
              control={control}
              render={({ field }) => (
                <Autocomplete
                  multiple
                  freeSolo
                  options={COMMON_PRODUCTS}
                  value={field.value ?? []}
                  onChange={(_, val) => field.onChange(val)}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip variant="outlined" label={option} {...getTagProps({ index })} key={option} />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Products Discussed" placeholder="Type and press enter" />
                  )}
                />
              )}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Discussion Summary"
              fullWidth
              multiline
              minRows={3}
              {...register("discussion_summary")}
              error={!!errors.discussion_summary}
              helperText={errors.discussion_summary?.message}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              label="Samples Given"
              type="number"
              fullWidth
              {...register("samples_given")}
              error={!!errors.samples_given}
              helperText={errors.samples_given?.message}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <Controller
              name="sentiment"
              control={control}
              render={({ field }) => (
                <TextField {...field} value={field.value ?? ""} select label="Sentiment" fullWidth>
                  <MenuItem value="">Not specified</MenuItem>
                  {SENTIMENTS.map((s) => (
                    <MenuItem key={s} value={s}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField label="Next Action" fullWidth {...register("next_action")} />
          </Grid>

          <Grid item xs={12}>
            <TextField label="Additional Notes" fullWidth multiline minRows={2} {...register("notes")} />
          </Grid>
        </Grid>

        <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
          <Button
            type="submit"
            variant="contained"
            startIcon={<SaveRoundedIcon />}
            disabled={isSubmitting}
          >
            {isSubmitting ? "Saving…" : isEditing ? "Save Changes" : "Log Interaction"}
          </Button>
          <Button
            type="button"
            variant="outlined"
            color="inherit"
            startIcon={<RestartAltRoundedIcon />}
            onClick={() => reset(isEditing ? undefined : DEFAULT_FORM_VALUES)}
          >
            Reset
          </Button>
        </Stack>
      </Box>
    </Paper>
  );
}
