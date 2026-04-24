import { useCallback, useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import apiClient, { clearAccessToken, setAccessToken, isAxiosError } from "../../lib/apiClient";
import type { User } from "../../types/user";

const ME_QUERY_KEY = ["me"] as const;
const INACTIVITY_MS = 30 * 60 * 1000;
const ACTIVITY_EVENTS = ["mousemove", "keydown", "click", "scroll", "touchstart"] as const;

async function fetchMe(): Promise<User | null> {
  try {
    const { data } = await apiClient.get<User>("/v1/users/me");
    return data;
  } catch (err) {
    if (isAxiosError(err) && err.response?.status === 401) {
      return null;
    }
    throw err;
  }
}

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [loginError, setLoginError] = useState<string | null>(null);

  const { data: user = null, isLoading } = useQuery<User | null>({
    queryKey: ME_QUERY_KEY,
    queryFn: fetchMe,
    retry: false,
    staleTime: Infinity,
  });

  const logout = useCallback(
    (message?: string) => {
      clearAccessToken();
      queryClient.cancelQueries({ queryKey: ME_QUERY_KEY });
      queryClient.setQueryData(ME_QUERY_KEY, null);
      navigate("/login", message ? { state: { msg: message } } : undefined);
    },
    [queryClient, navigate]
  );

  const login = useCallback(
    async (username: string, password: string): Promise<boolean> => {
      setLoginError(null);
      try {
        const { data } = await apiClient.post<{ access_token: string }>(
          "/v1/auth/login",
          { username, password }
        );
        setAccessToken(data.access_token);
        await queryClient.invalidateQueries({ queryKey: ME_QUERY_KEY });
        return true;
      } catch (err) {
        if (isAxiosError(err) && err.response?.status === 401) {
          setLoginError(
            "Usuário ou senha inválidos. Verifique suas credenciais e tente novamente."
          );
        } else {
          setLoginError(
            "Erro de comunicação com o servidor. Tente novamente em instantes."
          );
        }
        return false;
      }
    },
    [queryClient]
  );

  useEffect(() => {
    if (!user) return;

    let timer: ReturnType<typeof setTimeout>;
    const resetTimer = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        logout(
          "Sua sessão expirou por inatividade. Realize o login novamente para continuar."
        );
      }, INACTIVITY_MS);
    };

    ACTIVITY_EVENTS.forEach((e) =>
      window.addEventListener(e, resetTimer, { passive: true })
    );
    resetTimer();

    return () => {
      clearTimeout(timer);
      ACTIVITY_EVENTS.forEach((e) => window.removeEventListener(e, resetTimer));
    };
  }, [user, logout]);

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
