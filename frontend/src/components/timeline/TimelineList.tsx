import { Stack, Typography, Box } from "@mui/material";
import TimelineItem from "./TimelineItem";
import type { HCP, Interaction } from "@/types";

interface TimelineListProps {
  interactions: Interaction[];
  hcpsById: Record<string, HCP>;
  onEdit: (interaction: Interaction) => void;
}

export default function TimelineList({ interactions, hcpsById, onEdit }: TimelineListProps) {
  if (interactions.length === 0) {
    return (
      <Box sx={{ textAlign: "center", py: 8 }}>
        <Typography color="text.secondary">No interactions found for the current filters.</Typography>
      </Box>
    );
  }

  return (
    <Stack spacing={2}>
      {interactions.map((interaction) => (
        <TimelineItem
          key={interaction.id}
          interaction={interaction}
          hcpName={hcpsById[interaction.hcp_id]?.full_name}
          onEdit={onEdit}
        />
      ))}
    </Stack>
  );
}
