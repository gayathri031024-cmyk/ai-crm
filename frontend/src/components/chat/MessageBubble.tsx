import { Box, Paper, Typography, Chip } from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import BuildRoundedIcon from "@mui/icons-material/BuildRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import type { ChatMessage } from "@/types";
import { formatTime } from "@/utils/formatters";

interface MessageBubbleProps {
  message: ChatMessage;
  toolSuccess?: { toolName: string; data: Record<string, unknown> } | null;
}

export default function MessageBubble({ message, toolSuccess }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";

  if (isTool) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", my: 1 }}>
        <Chip
          size="small"
          icon={<BuildRoundedIcon sx={{ fontSize: 14 }} />}
          label={`Used tool: ${message.tool_name ?? "unknown"}`}
          variant="outlined"
          sx={{ fontSize: 12, color: "text.secondary" }}
        />
      </Box>
    );
  }

  if (toolSuccess) {
    return (
      <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 1.5 }}>
        <Paper
          elevation={0}
          sx={{
            maxWidth: "80%",
            px: 2,
            py: 1.5,
            bgcolor: "#ECFDF5",
            border: "1px solid #A7F3D0",
            borderRadius: 2.5,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
            <CheckCircleRoundedIcon sx={{ color: "#059669", fontSize: 20, mt: 0.2 }} />
            <Box
              sx={{
                "& p": { m: 0, mb: 0.5 },
                "& p:last-child": { mb: 0 },
                fontSize: 14.5,
                color: "#065F46",
              }}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </Box>
          </Box>
          <Typography variant="caption" sx={{ display: "block", mt: 0.5, ml: 3.5, color: "#059669" }}>
            {formatTime(message.created_at)}
          </Typography>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", mb: 1.5 }}>
      <Paper
        elevation={0}
        sx={{
          maxWidth: "72%",
          px: 2,
          py: 1.25,
          bgcolor: isUser ? "primary.main" : "#F1F5F9",
          color: isUser ? "#fff" : "text.primary",
          borderRadius: 2.5,
          borderTopRightRadius: isUser ? 4 : 20,
          borderTopLeftRadius: isUser ? 20 : 4,
        }}
      >
        <Box
          sx={{
            "& p": { m: 0, mb: 0.5 },
            "& p:last-child": { mb: 0 },
            "& ul, & ol": { m: 0, pl: 2.5 },
            "& code": {
              bgcolor: isUser ? "rgba(255,255,255,0.15)" : "rgba(15,23,42,0.06)",
              px: 0.5,
              borderRadius: 0.5,
              fontSize: "0.85em",
            },
            fontSize: 14.5,
          }}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </Box>
        <Typography
          variant="caption"
          sx={{ display: "block", mt: 0.5, opacity: 0.7, textAlign: isUser ? "right" : "left" }}
        >
          {formatTime(message.created_at)}
        </Typography>
      </Paper>
    </Box>
  );
}
