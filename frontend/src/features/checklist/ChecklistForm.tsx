import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import apiClient from "../../lib/apiClient";
import { checklistInfoSchema, type ChecklistInfoData } from "./checklistSchema";
import type { ChecklistResponse } from "../../types/checklist";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const REQUIRED_FIELD_LABELS: Partial<Record<keyof ChecklistInfoData, string>> = {
  placa: "Placa",
  unidade: "Unidade",
  motorista: "Motorista",
  matricula_motorista: "Matrícula",
};

export default function ChecklistForm() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<ChecklistInfoData>({
    resolver: zodResolver(checklistInfoSchema),
  });

  const onInvalid = () => {
    const missing = (
      Object.entries(errors) as [keyof ChecklistInfoData, { type?: string } | undefined][]
    )
      .filter(([key, err]) => err?.type === "too_small" && key in REQUIRED_FIELD_LABELS)
      .map(([key]) => REQUIRED_FIELD_LABELS[key]!);
    if (missing.length > 0) {
      setServerError(
        `Os seguintes campos obrigatórios não foram preenchidos: ${missing.join(", ")}. Preencha-os para continuar.`
      );
    }
  };

  const onSubmit = async (data: ChecklistInfoData) => {
    setServerError(null);
    try {
      const response = await apiClient.post<ChecklistResponse>("/v1/checklists", data);
      navigate(`/checklists/${response.data.id}`);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const { detail, message, fields } = err.response.data ?? {};
        if (detail === "MSG-005") {
          setServerError(message ?? "Os seguintes campos obrigatórios não foram preenchidos. Preencha-os para continuar.");
        } else if (detail === "MSG-008") {
          setServerError(message ?? "Já existe uma entrega aberta para este veículo.");
        } else if (detail === "MSG-006" && fields?.includes("placa")) {
          setError("placa", { message: "Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234)." });
        } else if (detail === "MSG-007") {
          setError("matricula_motorista", { message: "O campo Matrícula aceita apenas valores numéricos." });
        } else {
          setServerError("Erro ao criar checklist. Tente novamente.");
        }
      } else {
        setServerError("Erro de comunicação com o servidor.");
      }
    }
  };

  return (
    <div className="mx-auto max-w-lg p-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Novo Checklist de Entrega</CardTitle>
          <CardDescription>Informações Gerais</CardDescription>
        </CardHeader>
        <CardContent>
          {serverError && (
            <div role="alert" className="mb-4 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit, onInvalid)} noValidate className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="numero_controle">Nº de Controle</Label>
              <Input id="numero_controle" type="text" value="Gerado automaticamente" readOnly disabled />
            </div>

            <div className="space-y-2">
              <Label htmlFor="placa">Placa</Label>
              <Input id="placa" type="text" {...register("placa")} />
              {errors.placa && <p className="text-sm text-danger">{errors.placa.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="unidade">Unidade</Label>
              <Input id="unidade" type="text" {...register("unidade")} />
              {errors.unidade && <p className="text-sm text-danger">{errors.unidade.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="subunidade">Subunidade</Label>
              <Input id="subunidade" type="text" {...register("subunidade")} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="motorista">Motorista</Label>
              <Input id="motorista" type="text" {...register("motorista")} />
              {errors.motorista && <p className="text-sm text-danger">{errors.motorista.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="matricula_motorista">Matrícula</Label>
              <Input id="matricula_motorista" type="text" {...register("matricula_motorista")} />
              {errors.matricula_motorista && <p className="text-sm text-danger">{errors.matricula_motorista.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="quilometragem_inicial">Quilometragem Inicial</Label>
              <Input id="quilometragem_inicial" type="number" step="0.1" min="0" {...register("quilometragem_inicial")} />
              {errors.quilometragem_inicial && <p className="text-sm text-danger">{errors.quilometragem_inicial.message}</p>}
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Criando..." : "Criar Checklist"}
            </Button>
            <Button type="button" variant="outline" className="mt-2 w-full" onClick={() => navigate("/")} disabled={isSubmitting}>
              Cancelar
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
