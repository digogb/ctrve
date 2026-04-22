import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";
import apiClient, { setAccessToken } from "../../lib/apiClient";
import { useQueryClient } from "@tanstack/react-query";

const loginSchema = z.object({
  username: z.string().min(1, "Informe o usuário"),
  password: z.string().min(1, "Informe a senha"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      const response = await apiClient.post<{ access_token: string }>(
        "/v1/auth/login",
        data
      );
      setAccessToken(response.data.access_token);
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        setServerError(
          "Usuário ou senha inválidos. Verifique suas credenciais e tente novamente."
        );
      } else {
        setServerError(
          "Erro de comunicação com o servidor. Tente novamente em instantes."
        );
      }
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>CTRVE</h1>
        <h2>Checklist de Transporte de Veículos</h2>

        {serverError && (
          <div role="alert" className="error-alert">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="form-field">
            <label htmlFor="username">Usuário</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              {...register("username")}
            />
            {errors.username && (
              <span className="field-error">{errors.username.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register("password")}
            />
            {errors.password && (
              <span className="field-error">{errors.password.message}</span>
            )}
          </div>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
