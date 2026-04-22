import { useState, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import apiClient, { clearAccessToken, setAccessToken } from "../../lib/apiClient";
import type { User } from "../../types/user";

async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>("/v1/users/me");
  return data;
}

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [loginError, setLoginError] = useState<string | null>(null);

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
    staleTime: Infinity,
    initialData: null,
  });

  const login = useCallback(
    async (username: string, password: string) => {
      setLoginError(null);
      const { data } = await apiClient.post<{ access_token: string }>(
        "/v1/auth/login",
        { username, password }
      );
      setAccessToken(data.access_token);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/");
    },
    [queryClient, navigate]
  );

  const logout = useCallback(() => {
    clearAccessToken();
    queryClient.clear();
    navigate("/login");
  }, [queryClient, navigate]);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    loginError,
    setLoginError,
  };
}
