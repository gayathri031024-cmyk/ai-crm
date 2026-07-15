import { Snackbar, Alert } from "@mui/material";
import AppRoutes from "@/routes/AppRoutes";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { dismissToast } from "@/features/ui/uiSlice";

export default function App() {
  const toasts = useAppSelector((s) => s.ui.toasts);
  const dispatch = useAppDispatch();

  return (
    <>
      <AppRoutes />
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open
          autoHideDuration={4000}
          onClose={() => dispatch(dismissToast(toast.id))}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        >
          <Alert
            severity={toast.severity}
            variant="filled"
            onClose={() => dispatch(dismissToast(toast.id))}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
}
