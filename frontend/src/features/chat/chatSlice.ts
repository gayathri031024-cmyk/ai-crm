import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { chatApi } from "@/api/chatApi";
import { extractErrorMessage } from "@/api/client";
import type { ChatMessage } from "@/types";

interface ChatState {
  conversationId: string | null;
  messages: ChatMessage[];
  isTyping: boolean;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: ChatState = {
  conversationId: null,
  messages: [],
  isTyping: false,
  status: "idle",
  error: null,
};

export const sendChatMessage = createAsyncThunk(
  "chat/send",
  async ({ message, conversationId }: { message: string; conversationId: string | null }, { rejectWithValue }) => {
    try {
      return await chatApi.sendMessage(message, conversationId);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const loadConversation = createAsyncThunk(
  "chat/loadConversation",
  async (id: string, { rejectWithValue }) => {
    try {
      return await chatApi.conversation(id);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    appendUserMessage(state, action) {
      state.messages.push({
        id: crypto.randomUUID(),
        role: "user",
        content: action.payload as string,
        tool_name: null,
        tool_output: null,
        model_used: null,
        created_at: new Date().toISOString(),
      });
    },
    resetConversation(state) {
      state.conversationId = null;
      state.messages = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.isTyping = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isTyping = false;
        state.conversationId = action.payload.conversation_id;
        // Replace optimistic user message + append server-confirmed turn (user + assistant + any tool msgs)
        state.messages.pop();
        state.messages.push(...action.payload.messages);
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isTyping = false;
        state.error = action.payload as string;
      })
      .addCase(loadConversation.fulfilled, (state, action) => {
        state.conversationId = action.payload.id;
        state.messages = action.payload.messages;
      });
  },
});

export const { appendUserMessage, resetConversation } = chatSlice.actions;
export default chatSlice.reducer;
