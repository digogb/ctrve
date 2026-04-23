import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import { checklistEntregaSchema, type ChecklistEntregaData } from "./checklistSchema";
import { CHECKLIST_ITEMS } from "./ChecklistItems";
import ChecklistItems from "./ChecklistItems";
import FuelLevel from "./FuelLevel";
import DamageMap from "../damage-map/DamageMap";

export default function ChecklistView() {
  const { id } = useParams<{ id: string }>();

  const { data: checklist, isLoading, isError } = useQuery<ChecklistResponse>({
    queryKey: ["checklists", id ?? ""],
    queryFn: () => {
      if (!id) throw new Error("ID inválido");
      return apiClient.get<ChecklistResponse>(`/v1/checklists/${id}`).then((r) => r.data);
    },
    enabled: !!id,
    retry: false,
  });

  const { control, register, reset, formState: { errors } } = useForm<ChecklistEntregaData>({
    resolver: zodResolver(checklistEntregaSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((item) => ({ nome: item.nome, status: undefined })),
      nivel_combustivel: undefined,
      data_entrega: "",
      avarias: [],
    },
  });

  useEffect(() => {
    if (checklist) {
      reset({
        itens: CHECKLIST_ITEMS.map((item) => ({
          nome: item.nome,
          status:
            checklist.itens?.find((i) => i.nome === item.nome)?.status ?? undefined,
        })),
        nivel_combustivel: checklist.nivel_combustivel ?? undefined,
        data_entrega: checklist.data_entrega
          ? checklist.data_entrega.slice(0, 16)
          : "",
        avarias: checklist.avarias ?? [],
      });
    }
  }, [checklist, reset]);

  if (!id) return <p role="alert">ID do checklist inválido.</p>;
  if (isLoading) return <p aria-live="polite">Carregando...</p>;
  if (isError) return <p role="alert">Erro ao carregar checklist. Tente novamente.</p>;
  if (!checklist) return <p role="alert">Checklist não encontrado.</p>;

  return (
    <div className="checklist-view">
      <h1>Checklist de Entrega — Nº {checklist.id}</h1>

      <section className="info-gerais">
        <h2>Informações Gerais</h2>
        <dl>
          <dt>Placa</dt>
          <dd>{checklist.placa}</dd>
          <dt>Unidade</dt>
          <dd>{checklist.unidade}</dd>
          {checklist.subunidade && (
            <>
              <dt>Subunidade</dt>
              <dd>{checklist.subunidade}</dd>
            </>
          )}
          <dt>Motorista</dt>
          <dd>{checklist.motorista}</dd>
          <dt>Matrícula</dt>
          <dd>{checklist.matricula_motorista}</dd>
          <dt>Quilometragem Inicial</dt>
          <dd>{checklist.quilometragem_inicial} km</dd>
        </dl>
      </section>

      {checklist.is_locked ? (
        <section
          className="checklist-readonly"
          aria-label="Checklist de entrega (somente leitura)"
        >
          <h2>Checklist de Entrega</h2>
          <ChecklistItems readOnly savedItems={checklist.itens ?? []} />
          {checklist.nivel_combustivel && (
            <p>
              Nível de Combustível: <strong>{checklist.nivel_combustivel}</strong>
            </p>
          )}
          {checklist.data_entrega && (
            <p>
              Data da Entrega:{" "}
              <strong>
                {new Intl.DateTimeFormat("pt-BR", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                }).format(new Date(checklist.data_entrega))}
              </strong>
            </p>
          )}
          {checklist.status !== "devolvido" && checklist.avarias && checklist.avarias.length > 0 && (
            <DamageMap value={checklist.avarias} readOnly onChange={() => {}} />
          )}
        </section>
      ) : (
        <form className="checklist-form" noValidate>
          <h2>Checklist de Entrega</h2>

          <div className="form-field">
            <label htmlFor="data_entrega">Data e Horário da Entrega</label>
            <input
              id="data_entrega"
              type="datetime-local"
              {...register("data_entrega")}
            />
            {errors.data_entrega && (
              <span className="field-error" role="alert">
                {errors.data_entrega.message}
              </span>
            )}
          </div>

          <ChecklistItems control={control} errors={errors} />
          <FuelLevel control={control} error={errors.nivel_combustivel} />

          {checklist.status !== "devolvido" && (
            <Controller
              name="avarias"
              control={control}
              render={({ field }) => (
                <DamageMap value={field.value} onChange={field.onChange} />
              )}
            />
          )}

          <button
            type="button"
            disabled
            title="Salvar será implementado na Story 5.1"
            className="btn-save-disabled"
          >
            Salvar
          </button>
        </form>
      )}
    </div>
  );
}
