import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Collapse,
  Divider,
  Stack,
} from "@mui/material";
import EditRoundedIcon from "@mui/icons-material/EditRounded";
import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import EventNoteRoundedIcon from "@mui/icons-material/EventNoteRounded";
import SentimentBadge from "@/components/common/SentimentBadge";
import { formatDate, formatDateTime, titleCase } from "@/utils/formatters";
import type { Interaction } from "@/types";

interface TimelineItemProps {
  interaction: Interaction;
  hcpName?: string;
  onEdit: (interaction: Interaction) => void;
}

export default function TimelineItem({ interaction, hcpName, onEdit }: TimelineItemProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Paper elevation={0} sx={{ border: "1px solid #E2E8F0", p: 2.5 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <Box sx={{ display: "flex", gap: 1.5 }}>
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: "50%",
              bgcolor: "#EEF2FF",
              color: "primary.main",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <EventNoteRoundedIcon fontSize="small" />
          </Box>
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              {hcpName ?? interaction.hcp_id}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {titleCase(interaction.interaction_type)} · {formatDateTime(interaction.visit_date)}
            </Typography>
          </Box>
        </Box>

        <Stack direction="row" spacing={1} alignItems="center">
          <SentimentBadge sentiment={interaction.sentiment} />
          {interaction.created_via === "ai_chat" && (
            <Chip size="small" label="via AI Chat" variant="outlined" color="secondary" />
          )}
          <IconButton size="small" onClick={() => onEdit(interaction)}>
            <EditRoundedIcon fontSize="small" />
          </IconButton>
          <IconButton size="small" onClick={() => setExpanded((e) => !e)}>
            <ExpandMoreRoundedIcon
              fontSize="small"
              sx={{ transform: expanded ? "rotate(180deg)" : "none", transition: "0.2s" }}
            />
          </IconButton>
        </Stack>
      </Box>

      <Collapse in={expanded}>
        <Divider sx={{ my: 2 }} />
        <Stack spacing={1.5}>
          {interaction.discussion_summary && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                DISCUSSION SUMMARY
              </Typography>
              <Typography variant="body2">{interaction.discussion_summary}</Typography>
            </Box>
          )}
          {!!interaction.products_discussed?.length && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                PRODUCTS DISCUSSED
              </Typography>
              <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
                {interaction.products_discussed.map((p) => (
                  <Chip key={p} size="small" label={p} />
                ))}
              </Box>
            </Box>
          )}
          <Box sx={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                SAMPLES GIVEN
              </Typography>
              <Typography variant="body2">{interaction.samples_given}</Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                FOLLOW-UP DATE
              </Typography>
              <Typography variant="body2">{formatDate(interaction.follow_up_date)}</Typography>
            </Box>
            {interaction.next_action && (
              <Box>
                <Typography variant="caption" color="text.secondary">
                  NEXT ACTION
                </Typography>
                <Typography variant="body2">{interaction.next_action}</Typography>
              </Box>
            )}
          </Box>
          {interaction.notes && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                NOTES
              </Typography>
              <Typography variant="body2">{interaction.notes}</Typography>
            </Box>
          )}
        </Stack>
      </Collapse>
    </Paper>
  );
}
