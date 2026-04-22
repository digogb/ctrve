import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import apiClient from "../../lib/apiClient";
import { registerSchema, type RegisterFormData } from "./registerSchema";

export default function RegisterForm() {
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    setSuccessMessage(null);
    const { confirmPassword, ...payload } = data;
    try {
      await apiClient.post("/v1/users", payload);
      setSuccessMessage("Usuário cadastrado com sucesso.");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const { detail, fields } = err.response.data ?? {};
        if (detail === "MSG-003" && fields?.includes("matricula")) {
          setError("matricula", {
            message: "A matrícula informada já está cadastrada no sistema.",
          });
        } else if (detail === "MSG-004") {
          setError("password", {
            message:
              "A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número.",
          });
        } else {
          setServerError("Erro ao cadastrar usuário. Tente novamente.");
        }
      } else {
        setServerError("Erro de comunicação com o servidor.");
      }
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h2>Cadastrar Usuário</h2>

        {successMessage && (
          <div role="status" className="success-alert">
            {successMessage}
          </div>
        )}

        {serverError && (
          <div role="alert" className="error-alert">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="form-field">
            <label htmlFor="full_name">Nome Completo</label>
            <input id="full_name" type="text" {...register("full_name")} />
            {errors.full_name && (
              <span className="field-error">{errors.full_name.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="matricula">Matrícula</label>
            <input id="matricula" type="text" {...register("matricula")} />
            {errors.matricula && (
              <span className="field-error">{errors.matricula.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="username">Usuário</label>
            <input id="username" type="text" {...register("username")} />
            {errors.username && (
              <span className="field-error">{errors.username.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="role">Perfil</label>
            <select id="role" {...register("role")}>
              <option value="">Selecione...</option>
              <option value="responsavel">Responsável</option>
              <option value="motorista">Motorista</option>
            </select>
            {errors.role && (
              <span className="field-error">{errors.role.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="password">Senha</label>
            <input id="password" type="password" {...register("password")} />
            {errors.password && (
              <span className="field-error">{errors.password.message}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="confirmPassword">Confirmar Senha</label>
            <input
              id="confirmPassword"
              type="password"
              {...register("confirmPassword")}
            />
            {errors.confirmPassword && (
              <span className="field-error">
                {errors.confirmPassword.message}
              </span>
            )}
          </div>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Cadastrando..." : "Cadastrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
