import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { useAuthContext } from "./AuthContext";

const loginSchema = z.object({
  username: z.string().min(1, "Informe o usuário"),
  password: z.string().min(1, "Informe a senha"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loginError } = useAuthContext();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const sessionMsg = (location.state as { msg?: string } | null)?.msg ?? null;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    const ok = await login(data.username, data.password);
    if (ok) {
      setSuccessMsg("Login realizado com sucesso.");
      setTimeout(() => navigate("/"), 1000);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>CTRVE</h1>
        <h2>Checklist de Transporte de Veículos</h2>

        {sessionMsg && (
          <div role="alert" className="error-alert">
            {sessionMsg}
          </div>
        )}

        {successMsg && (
          <div role="status" className="success-alert">
            {successMsg}
          </div>
        )}

        {loginError && !successMsg && (
          <div role="alert" className="error-alert">
            {loginError}
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
