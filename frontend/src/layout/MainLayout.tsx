import { Box, Toolbar } from "@mui/material";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import { useAppSelector } from "@/app/hooks";

export default function MainLayout() {
  const sidebarOpen = useAppSelector((s) => s.ui.sidebarOpen);

  return (
    <Box sx={{ display: "flex" }}>
      <Navbar />
      <Sidebar open={sidebarOpen} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          minHeight: "100vh",
          bgcolor: "background.default",
          transition: "margin 0.2s",
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
