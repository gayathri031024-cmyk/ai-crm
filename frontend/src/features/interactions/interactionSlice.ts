import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { interactionApi, InteractionCreatePayload, InteractionListParams, InteractionUpdatePayload } from "@/api/interactionApi";
import { extractErrorMessage } from "@/api/client";
import type { DashboardSummary, Interaction, PaginationMeta } from "@/types";

interface InteractionState {
  items: Interaction[];
  meta: PaginationMeta | null;
  summary: DashboardSummary | null;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: InteractionState = {
  items: [],
  meta: null,
  summary: null,
  status: "idle",
  error: null,
};

export const fetchInteractions = createAsyncThunk(
  "interactions/fetchAll",
  async (params: InteractionListParams | undefined, { rejectWithValue }) => {
    try {
      return await interactionApi.list(params);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload: InteractionCreatePayload, { rejectWithValue }) => {
    try {
      return await interactionApi.create(payload);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const updateInteraction = createAsyncThunk(
  "interactions/update",
  async ({ id, payload }: { id: string; payload: InteractionUpdatePayload }, { rejectWithValue }) => {
    try {
      return await interactionApi.update(id, payload);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const fetchDashboardSummary = createAsyncThunk(
  "interactions/summary",
  async (mineOnly: boolean | undefined, { rejectWithValue }) => {
    try {
      return await interactionApi.dashboardSummary(mineOnly);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

const interactionSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload.items;
        state.meta = action.payload.meta;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.items.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      })
      .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
        state.summary = action.payload;
      });
  },
});

export default interactionSlice.reducer;
