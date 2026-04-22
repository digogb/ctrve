import { useEffect } from "react";
import { BrowserRouter, useNavigate } from "react-router-dom";
import { QueryClient, QueryClientProvider, useQueryClient } from "@tanstack/react-query";
import { clearAccessToken } from "./lib/apiClient";
import AppRoutes from "./routes";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

function SessionGuard() {
  const navigate = useNavigate();
  const qc = useQueryClient();

  useEffect(() => {
    const handler = () => {
      clearAccessToken();
      qc.clear();
      navigate("/login");
    };
    window.addEventListener("session-expired", handler);
    return () => window.removeEventListener("session-expired", handler);
  }, [navigate, qc]);

  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SessionGuard />
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
