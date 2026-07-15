import { useState } from "react";
import { Box, Button, TextField } from "@mui/material";

type ChatInputProps = {
  onSend: (text: string) => void;
  disabled?: boolean;
};

export default function ChatInput({
  onSend,
  disabled = false,
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    const text = message.trim();
    if (!text) return;

    onSend(text);
    setMessage("");
  };

  return (
    <Box sx={{ display: "flex", gap: 1, p: 2 }}>
      <TextField
        fullWidth
        value={message}
        placeholder="Type a message..."
        disabled={disabled}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
      />
      <Button variant="contained" onClick={handleSend} disabled={disabled}>
        Send
      </Button>
    </Box>
  );
}