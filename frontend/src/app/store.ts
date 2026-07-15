import { configureStore } from "@reduxjs/toolkit";
import authReducer from "@/features/auth/authSlice";
import interactionReducer from "@/features/interactions/interactionSlice";
import hcpReducer from "@/features/hcp/hcpSlice";
import chatReducer from "@/features/chat/chatSlice";
import uiReducer from "@/features/ui/uiSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    interactions: interactionReducer,
    hcps: hcpReducer,
    chat: chatReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
