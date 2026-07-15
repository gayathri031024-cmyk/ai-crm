import { Chip } from "@mui/material";
import SentimentSatisfiedAltRoundedIcon from "@mui/icons-material/SentimentSatisfiedAltRounded";
import SentimentNeutralRoundedIcon from "@mui/icons-material/SentimentNeutralRounded";
import SentimentDissatisfiedRoundedIcon from "@mui/icons-material/SentimentDissatisfiedRounded";
import type { Sentiment } from "@/types";

const CONFIG: Record<Sentiment, { label: string; color: "success" | "default" | "error"; icon: JSX.Element }> = {
  positive: { label: "Positive", color: "success", icon: <SentimentSatisfiedAltRoundedIcon sx={{ fontSize: 16 }} /> },
  neutral: { label: "Neutral", color: "default", icon: <SentimentNeutralRoundedIcon sx={{ fontSize: 16 }} /> },
  negative: { label: "Negative", color: "error", icon: <SentimentDissatisfiedRoundedIcon sx={{ fontSize: 16 }} /> },
};

export default function SentimentBadge({ sentiment }: { sentiment: Sentiment | null }) {
  if (!sentiment) return <Chip size="small" label="Not set" variant="outlined" />;
  const cfg = CONFIG[sentiment];
  return <Chip size="small" label={cfg.label} color={cfg.color} icon={cfg.icon} variant="outlined" />;
}
