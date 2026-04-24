import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import apiClient from "../../lib/apiClient";
import { registerSchema, type RegisterFormData } from "./registerSchema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function RegisterForm() {
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const redirectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (redirectTimer.current) clearTimeout(redirectTimer.current);
    };
  }, []);

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
      setSuccessMessage("Usuário cadastrado com sucesso");
      redirectTimer.current = setTimeout(() => navigate("/login"), 2000);
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
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Cadastrar Usuário</CardTitle>
        </CardHeader>
        <CardContent>
          {successMessage && (
            <div role="status" className="mb-4 rounded-md border border-success/30 bg-success/10 px-3 py-2 text-sm text-success">
              {successMessage}
            </div>
          )}

          {serverError && (
            <div role="alert" className="mb-4 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="full_name">Nome Completo</Label>
              <Input id="full_name" type="text" {...register("full_name")} />
              {errors.full_name && (
                <p className="text-sm text-danger">{errors.full_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="matricula">Matrícula</Label>
              <Input id="matricula" type="text" {...register("matricula")} />
              {errors.matricula && (
                <p className="text-sm text-danger">{errors.matricula.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input id="username" type="text" {...register("username")} />
              {errors.username && (
                <p className="text-sm text-danger">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Perfil</Label>
              <select
                id="role"
                {...register("role")}
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              >
                <option value="">Selecione...</option>
                <option value="responsavel">Responsável</option>
                <option value="motorista">Motorista</option>
              </select>
              {errors.role && (
                <p className="text-sm text-danger">{errors.role.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && (
                <p className="text-sm text-danger">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmar Senha</Label>
              <Input id="confirmPassword" type="password" {...register("confirmPassword")} />
              {errors.confirmPassword && (
                <p className="text-sm text-danger">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Cadastrando..." : "Cadastrar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
