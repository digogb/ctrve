import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import apiClient from "../../lib/apiClient";
import { checklistInfoSchema, type ChecklistInfoData } from "./checklistSchema";
import type { ChecklistResponse } from "../../types/checklist";

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

  // P-3: exibe MSG-005 ao tentar submeter com campos obrigatórios vazios
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
      const response = await apiClient.post<ChecklistResponse>(
        "/v1/checklists",
        data
      );
      navigate(`/checklists/${response.data.id}`);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const { detail, message, fields } = err.response.data ?? {};
        if (detail === "MSG-005") {
          setServerError(
            message ?? "Os seguintes campos obrigatórios não foram preenchidos. Preencha-os para continuar."
          );
        } else if (detail === "MSG-008") {
          setServerError(message ?? "Já existe uma entrega aberta para este veículo.");
        } else if (detail === "MSG-006" && fields?.includes("placa")) {
          setError("placa", {
            message: "Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234).",
          });
        } else if (detail === "MSG-007") {
          setError("matricula_motorista", {
            message: "O campo Matrícula aceita apenas valores numéricos.",
          });
        } else {
          setServerError("Erro ao criar checklist. Tente novamente.");
        }
      } else {
        setServerError("Erro de comunicação com o servidor.");
      }
    }
  };

  return (
    <div className="checklist-container">
      <h2>Novo Checklist de Entrega</h2>
      <h3>Informações Gerais</h3>

      {serverError && (
        <div role="alert" className="error-alert">
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit, onInvalid)} noValidate>
        {/* P-1: Nº de Controle auto-gerado — somente leitura antes da criação */}
        <div className="form-field">
          <label htmlFor="numero_controle">Nº de Controle</label>
          <input
            id="numero_controle"
            type="text"
            value="Gerado automaticamente"
            readOnly
            disabled
            className="field-readonly"
          />
        </div>

        <div className="form-field">
          <label htmlFor="placa">Placa</label>
          <input id="placa" type="text" {...register("placa")} />
          {errors.placa && (
            <span className="field-error">{errors.placa.message}</span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="unidade">Unidade</label>
          <input id="unidade" type="text" {...register("unidade")} />
          {errors.unidade && (
            <span className="field-error">{errors.unidade.message}</span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="subunidade">Subunidade</label>
          <input id="subunidade" type="text" {...register("subunidade")} />
        </div>

        <div className="form-field">
          <label htmlFor="motorista">Motorista</label>
          <input id="motorista" type="text" {...register("motorista")} />
          {errors.motorista && (
            <span className="field-error">{errors.motorista.message}</span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="matricula_motorista">Matrícula</label>
          <input
            id="matricula_motorista"
            type="text"
            {...register("matricula_motorista")}
          />
          {errors.matricula_motorista && (
            <span className="field-error">
              {errors.matricula_motorista.message}
            </span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="quilometragem_inicial">Quilometragem Inicial</label>
          <input
            id="quilometragem_inicial"
            type="number"
            step="0.1"
            min="0"
            {...register("quilometragem_inicial")}
          />
          {errors.quilometragem_inicial && (
            <span className="field-error">
              {errors.quilometragem_inicial.message}
            </span>
          )}
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Criando..." : "Criar Checklist"}
        </button>
      </form>
    </div>
  );
}
