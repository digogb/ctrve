import { Navigate } from "react-router-dom";
import { useAuthContext } from "../features/auth/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuthContext();

  if (isLoading) {
    return <div aria-label="Carregando...">Carregando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
