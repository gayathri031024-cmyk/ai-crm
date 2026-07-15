import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { authApi, LoginPayload, RegisterPayload } from "@/api/authApi";
import { extractErrorMessage } from "@/api/client";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

function loadUser(): User | null {
  try {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

const initialState: AuthState = {
  user: loadUser(),
  accessToken: localStorage.getItem("access_token"),
  status: "idle",
  error: null,
};

export const login = createAsyncThunk("auth/login", async (payload: LoginPayload, { rejectWithValue }) => {
  try {
    return await authApi.login(payload);
  } catch (err) {
    return rejectWithValue(extractErrorMessage(err));
  }
});

export const register = createAsyncThunk(
  "auth/register",
  async (payload: RegisterPayload, { rejectWithValue }) => {
    try {
      return await authApi.register(payload);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const fetchCurrentUser = createAsyncThunk("auth/me", async (_: void, { rejectWithValue }) => {
  try {
    return await authApi.me();
  } catch (err) {
    return rejectWithValue(extractErrorMessage(err));
  }
});

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.accessToken = null;
      state.status = "idle";
      state.error = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        localStorage.setItem("user", JSON.stringify(action.payload));
      })

      .addMatcher(
        (action): action is PayloadAction<{
          access_token: string;
          refresh_token: string;
          user: User;
        }> =>
          action.type === login.fulfilled.type ||
          action.type === register.fulfilled.type,
        (state, action) => {
          state.status = "succeeded";
          state.user = action.payload.user;
          state.accessToken = action.payload.access_token;

          localStorage.setItem("access_token", action.payload.access_token);
          localStorage.setItem("refresh_token", action.payload.refresh_token);
          localStorage.setItem("user", JSON.stringify(action.payload.user));
        }
      )

      .addMatcher(
        (action) =>
          action.type === login.pending.type ||
          action.type === register.pending.type,
        (state) => {
          state.status = "loading";
          state.error = null;
        }
      )

      .addMatcher(
        (action) =>
          action.type === login.rejected.type ||
          action.type === register.rejected.type,
        (state, action) => {
          state.status = "failed";
          state.error =
            (action as PayloadAction<string>).payload ??
            "Authentication failed";
        }
      );
  },
});

export const { logout, clearAuthError } = authSlice.actions;
export default authSlice.reducer;