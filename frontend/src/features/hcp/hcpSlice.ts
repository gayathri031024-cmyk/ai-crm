import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { hcpApi, HCPListParams } from "@/api/hcpApi";
import { extractErrorMessage } from "@/api/client";
import type { HCP, PaginationMeta } from "@/types";

interface HcpState {
  items: HCP[];
  meta: PaginationMeta | null;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: HcpState = {
  items: [],
  meta: null,
  status: "idle",
  error: null,
};

export const fetchHcps = createAsyncThunk(
  "hcps/fetchAll",
  async (params: HCPListParams | undefined, { rejectWithValue }) => {
    try {
      return await hcpApi.list(params);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

const hcpSlice = createSlice({
  name: "hcps",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload.items;
        state.meta = action.payload.meta;
      })
      .addCase(fetchHcps.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      });
  },
});

export default hcpSlice.reducer;
