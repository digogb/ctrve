import { Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient from "../lib/apiClient";
import type { User } from "../types/user";

async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>("/v1/users/me");
  return data;
}

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { data: user, isLoading } = useQuery<User | undefined>({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) {
    return <div aria-label="Carregando...">Carregando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
