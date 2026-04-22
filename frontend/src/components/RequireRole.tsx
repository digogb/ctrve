import { Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient from "../lib/apiClient";
import type { User, UserRole } from "../types/user";

async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>("/v1/users/me");
  return data;
}

interface RequireRoleProps {
  role: UserRole;
  children: React.ReactNode;
}

export default function RequireRole({ role, children }: RequireRoleProps) {
  const { data: user, isLoading } = useQuery<User | undefined>({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return null;
  if (!user || user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}
