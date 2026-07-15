import { Grid, Paper, Typography, Box } from "@mui/material";
import EventAvailableRoundedIcon from "@mui/icons-material/EventAvailableRounded";
import PendingActionsRoundedIcon from "@mui/icons-material/PendingActionsRounded";
import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";
import SentimentSatisfiedAltRoundedIcon from "@mui/icons-material/SentimentSatisfiedAltRounded";
import type { DashboardSummary } from "@/types";

interface SummaryCardsProps {
  summary: DashboardSummary | null;
}

const CARD_CONFIG = [
  {
    key: "todays_visits",
    label: "Today's Visits",
    icon: <EventAvailableRoundedIcon />,
    color: "#4F46E5",
  },
  {
    key: "pending_follow_ups",
    label: "Pending Follow-ups",
    icon: <PendingActionsRoundedIcon />,
    color: "#D97706",
  },
  {
    key: "total_interactions",
    label: "Total Interactions",
    icon: <Inventory2RoundedIcon />,
    color: "#0EA5E9",
  },
  {
    key: "positive_sentiment_pct",
    label: "Positive Sentiment",
    icon: <SentimentSatisfiedAltRoundedIcon />,
    color: "#16A34A",
    suffix: "%",
  },
];

export default function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <Grid container spacing={2.5}>
      {CARD_CONFIG.map((card) => {
        const raw = summary?.[card.key];
        const value = raw === undefined || raw === null ? "—" : `${raw}${card.suffix ?? ""}`;
        return (
          <Grid item xs={12} sm={6} md={3} key={card.key}>
            <Paper elevation={0} sx={{ p: 2.5, border: "1px solid #E2E8F0" }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                <Box
                  sx={{
                    width: 42,
                    height: 42,
                    borderRadius: 2,
                    bgcolor: `${card.color}1A`,
                    color: card.color,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {card.icon}
                </Box>
                <Box>
                  <Typography variant="h5" fontWeight={700} lineHeight={1.2}>
                    {value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.label}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        );
      })}
    </Grid>
  );
}
