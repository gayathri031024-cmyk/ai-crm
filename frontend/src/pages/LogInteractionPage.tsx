
import { Box, Typography, Grid } from "@mui/material";
import LogInteractionForm from "@/components/forms/LogInteractionForm";
import ChatWindow from "@/components/chat/ChatWindow";

export default function LogInteractionPage() {
  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 0.5 }}>
        Log Interaction
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Use the structured form, or just describe it to the assistant.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7} lg={8}>
          <LogInteractionForm />
        </Grid>
        <Grid item xs={12} md={5} lg={4}>
          <ChatWindow />
        </Grid>
      </Grid>
    </Box>
  );
}