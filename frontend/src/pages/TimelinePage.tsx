import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  MenuItem,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
} from "@mui/material";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import TimelineList from "@/components/timeline/TimelineList";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import LogInteractionForm from "@/components/forms/LogInteractionForm";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { fetchInteractions } from "@/features/interactions/interactionSlice";
import { fetchHcps } from "@/features/hcp/hcpSlice";
import { INTERACTION_TYPES, SENTIMENTS } from "@/components/forms/logInteractionSchema";
import { titleCase } from "@/utils/formatters";
import type { Interaction } from "@/types";

const PAGE_SIZE = 10;

export default function TimelinePage() {
  const dispatch = useAppDispatch();
  const { items, meta, status } = useAppSelector((s) => s.interactions);
  const hcps = useAppSelector((s) => s.hcps.items);

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [sentiment, setSentiment] = useState("");
  const [editingInteraction, setEditingInteraction] = useState<Interaction | null>(null);

  useEffect(() => {
    dispatch(fetchHcps({ page_size: 100 }));
  }, [dispatch]);

  useEffect(() => {
    const handle = setTimeout(() => {
      dispatch(
        fetchInteractions({
          page,
          page_size: PAGE_SIZE,
          search: search || undefined,
          interaction_type: (type || undefined) as any,
          sentiment: (sentiment || undefined) as any,
          sort_by: "visit_date",
          sort_dir: "desc",
        })
      );
    }, 300);
    return () => clearTimeout(handle);
  }, [dispatch, page, search, type, sentiment]);

  const hcpsById = useMemo(() => Object.fromEntries(hcps.map((h) => [h.id, h])), [hcps]);

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 0.5 }}>
        Interaction Timeline
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Chronological history of every logged interaction.
      </Typography>

      <Paper elevation={0} sx={{ p: 2.5, border: "1px solid #E2E8F0", mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              size="small"
              label="Search summary or notes"
              value={search}
              onChange={(e) => {
                setPage(1);
                setSearch(e.target.value);
              }}
            />
          </Grid>
          <Grid item xs={6} md={3.5}>
            <TextField
              select
              fullWidth
              size="small"
              label="Interaction Type"
              value={type}
              onChange={(e) => {
                setPage(1);
                setType(e.target.value);
              }}
            >
              <MenuItem value="">All types</MenuItem>
              {INTERACTION_TYPES.map((t) => (
                <MenuItem key={t} value={t}>
                  {titleCase(t)}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={6} md={3.5}>
            <TextField
              select
              fullWidth
              size="small"
              label="Sentiment"
              value={sentiment}
              onChange={(e) => {
                setPage(1);
                setSentiment(e.target.value);
              }}
            >
              <MenuItem value="">All sentiments</MenuItem>
              {SENTIMENTS.map((s) => (
                <MenuItem key={s} value={s}>
                  {titleCase(s)}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {status === "loading" ? (
        <LoadingSpinner label="Loading interactions…" />
      ) : (
        <TimelineList interactions={items} hcpsById={hcpsById} onEdit={setEditingInteraction} />
      )}

      {meta && meta.total_pages > 1 && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Pagination count={meta.total_pages} page={page} onChange={(_, p) => setPage(p)} color="primary" />
        </Box>
      )}

      <Dialog open={!!editingInteraction} onClose={() => setEditingInteraction(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          Edit Interaction
          <IconButton onClick={() => setEditingInteraction(null)}>
            <CloseRoundedIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {editingInteraction && (
            <LogInteractionForm
              editingInteraction={editingInteraction}
              onDone={() => setEditingInteraction(null)}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
