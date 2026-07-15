import { useEffect, useRef } from "react";
import { Box, Paper, Typography, Divider } from "@mui/material";
import SmartToyRoundedIcon from "@mui/icons-material/SmartToyRounded";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { appendUserMessage, sendChatMessage } from "@/features/chat/chatSlice";
import { pushToast } from "@/features/ui/uiSlice";

export default function ChatWindow() {
  const dispatch = useAppDispatch();
  const { messages, isTyping, conversationId } = useAppSelector((s) => s.chat);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async (text: string) => {
    dispatch(appendUserMessage(text));
    const result = await dispatch(sendChatMessage({ message: text, conversationId }));
    if (sendChatMessage.rejected.match(result)) {
      dispatch(pushToast("The assistant couldn't respond. Please try again.", "error"));
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{ border: "1px solid #E2E8F0", display: "flex", flexDirection: "column", height: "72vh" }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, px: 2, py: 1.5 }}>
        <SmartToyRoundedIcon color="primary" />
        <Typography variant="subtitle1" fontWeight={600}>
          CRM Assistant
        </Typography>
      </Box>
      <Divider />

      <Box sx={{ flex: 1, overflowY: "auto", px: 2, py: 2 }}>
        {messages.length === 0 && (
          <Box sx={{ textAlign: "center", color: "text.secondary", mt: 6 }}>
            <Typography variant="body2">
              Try: "Log a visit with Dr. Mehta today, discussed Cardiozen, positive sentiment"
            </Typography>
          </Box>
        )}
        {messages.map((m, idx) => {
          const prev = messages[idx - 1];
          const toolSuccess =
            m.role === "assistant" &&
            prev?.role === "tool" &&
            prev.tool_name === "log_interaction" &&
            (prev.tool_output as any)?.status === "ok"
              ? { toolName: prev.tool_name as string, data: (prev.tool_output as any).data }
              : null;
          return <MessageBubble key={m.id} message={m} toolSuccess={toolSuccess} />;
        })}
        {isTyping && <TypingIndicator />}
        <div ref={bottomRef} />
      </Box>

      <ChatInput onSend={handleSend} disabled={isTyping} />
    </Paper>
  );
}
