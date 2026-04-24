import { Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient, { isAxiosError } from "../lib/apiClient";
import type { User, UserRole } from "../types/user";

async function fetchMe(): Promise<User | null> {
  try {
    const { data } = await apiClient.get<User>("/v1/users/me");
    return data;
  } catch (err) {
    if (isAxiosError(err) && err.response?.status === 401) return null;
    throw err;
  }
}

interface RequireRoleProps {
  role: UserRole;
  children: React.ReactNode;
}

export default function RequireRole({ role, children }: RequireRoleProps) {
  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <div className="flex min-h-screen items-center justify-center text-muted" aria-busy="true">Carregando...</div>;
  if (!user || user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}
