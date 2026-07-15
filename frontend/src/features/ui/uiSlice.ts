import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type InteractionMode = "form" | "chat";

interface Toast {
  id: string;
  message: string;
  severity: "success" | "error" | "info" | "warning";
}

interface UiState {
  sidebarOpen: boolean;
  interactionMode: InteractionMode;
  toasts: Toast[];
}

const initialState: UiState = {
  sidebarOpen: true,
  interactionMode: "form",
  toasts: [],
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setInteractionMode(state, action: PayloadAction<InteractionMode>) {
      state.interactionMode = action.payload;
    },
    pushToast: {
      reducer(state, action: PayloadAction<Toast>) {
        state.toasts.push(action.payload);
      },
      prepare(message: string, severity: Toast["severity"] = "info") {
        return { payload: { id: crypto.randomUUID(), message, severity } };
      },
    },
    dismissToast(state, action: PayloadAction<string>) {
      state.toasts = state.toasts.filter((t) => t.id !== action.payload);
    },
  },
});

export const { toggleSidebar, setInteractionMode, pushToast, dismissToast } = uiSlice.actions;
export default uiSlice.reducer;
