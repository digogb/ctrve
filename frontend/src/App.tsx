import { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppRoutes from "./routes";
import { AuthProvider, useAuthContext } from "./features/auth/AuthContext";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

function SessionGuard() {
  const { logout } = useAuthContext();

  useEffect(() => {
    const handler = () =>
      logout(
        "Sua sessão expirou por inatividade. Realize o login novamente para continuar."
      );
    window.addEventListener("session-expired", handler);
    return () => window.removeEventListener("session-expired", handler);
  }, [logout]);

  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <SessionGuard />
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
