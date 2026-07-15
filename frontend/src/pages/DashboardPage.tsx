import { useEffect } from "react";
import { Box, Typography, Grid, Paper } from "@mui/material";
import SummaryCards from "@/components/dashboard/SummaryCards";
import TimelineList from "@/components/timeline/TimelineList";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { fetchDashboardSummary, fetchInteractions } from "@/features/interactions/interactionSlice";
import { fetchHcps } from "@/features/hcp/hcpSlice";
import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { summary, items, status } = useAppSelector((s) => s.interactions);
  const hcps = useAppSelector((s) => s.hcps.items);
  const user = useAppSelector((s) => s.auth.user);

  useEffect(() => {
    dispatch(fetchDashboardSummary(true));
    dispatch(fetchInteractions({ page: 1, page_size: 5, sort_by: "visit_date", sort_dir: "desc" }));
    dispatch(fetchHcps({ page_size: 100 }));
  }, [dispatch]);

  const hcpsById = Object.fromEntries(hcps.map((h) => [h.id, h]));

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 0.5 }}>
        Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Here's what's happening across your HCP relationships today.
      </Typography>

      <SummaryCards summary={summary} />

      <Grid container spacing={2.5} sx={{ mt: 0.5 }}>
        <Grid item xs={12}>
          <Paper elevation={0} sx={{ p: 3, border: "1px solid #E2E8F0" }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Typography variant="h6">Recent Interactions</Typography>
              <Typography
                variant="body2"
                color="primary"
                sx={{ cursor: "pointer" }}
                onClick={() => navigate("/timeline")}
              >
                View all →
              </Typography>
            </Box>
            {status === "loading" ? (
              <LoadingSpinner label="Loading recent interactions…" />
            ) : (
              <TimelineList interactions={items} hcpsById={hcpsById} onEdit={() => navigate("/timeline")} />
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
