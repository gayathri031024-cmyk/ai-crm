import { Box, keyframes } from "@mui/material";

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
`;

export default function TypingIndicator() {
  return (
    <Box sx={{ display: "flex", gap: 0.5, alignItems: "center", px: 1.5, py: 1 }}>
      {[0, 1, 2].map((i) => (
        <Box
          key={i}
          sx={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            bgcolor: "primary.main",
            animation: `${bounce} 1.2s infinite ease-in-out`,
            animationDelay: `${i * 0.15}s`,
          }}
        />
      ))}
    </Box>
  );
}
