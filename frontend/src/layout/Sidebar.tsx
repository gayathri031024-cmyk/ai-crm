import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar, Box, Typography } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import EditNoteRoundedIcon from "@mui/icons-material/EditNoteRounded";
import ChatBubbleRoundedIcon from "@mui/icons-material/ChatBubbleRounded";
import TimelineRoundedIcon from "@mui/icons-material/TimelineRounded";

const DRAWER_WIDTH = 240;

const NAV_ITEMS = [
  { label: "Dashboard", path: "/dashboard", icon: <DashboardRoundedIcon /> },
  { label: "Log Interaction", path: "/log-interaction", icon: <EditNoteRoundedIcon /> },
  { label: "Timeline", path: "/timeline", icon: <TimelineRoundedIcon /> },
];

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: open ? DRAWER_WIDTH : 0,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          borderRight: "1px solid #E2E8F0",
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" fontWeight={700} color="primary">
          AI-First CRM
        </Typography>
      </Toolbar>
      <Box sx={{ overflow: "auto", mt: 1 }}>
        <List>
          {NAV_ITEMS.map((item) => (
            <ListItemButton
              key={item.path}
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                mx: 1,
                borderRadius: 2,
                "&.Mui-selected": { bgcolor: "primary.main", color: "#fff" },
                "&.Mui-selected:hover": { bgcolor: "primary.dark" },
                "&.Mui-selected .MuiListItemIcon-root": { color: "#fff" },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}
