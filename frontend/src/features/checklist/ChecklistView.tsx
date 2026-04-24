import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import {
  checklistEntregaSchema,
  checklistDevolucaoSchema,
  type ChecklistEntregaData,
  type ChecklistDevolucaoData,
} from "./checklistSchema";
import { CHECKLIST_ITEMS } from "./ChecklistItems";
import ChecklistItems from "./ChecklistItems";
import FuelLevel from "./FuelLevel";
import DamageMap from "../damage-map/DamageMap";
import SignaturePad from "../signature/SignaturePad";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function EntregaReadOnly({ checklist }: { checklist: ChecklistResponse }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Checklist de Entrega</CardTitle>
      </CardHeader>
      <CardContent aria-label="Checklist de entrega (somente leitura)">
        <ChecklistItems readOnly savedItems={checklist.itens ?? []} />
        {checklist.nivel_combustivel && (
          <p className="mt-4 text-sm">
            Nível de Combustível: <strong>{checklist.nivel_combustivel}</strong>
          </p>
        )}
        {checklist.data_entrega && (
          <p className="mt-2 text-sm">
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
        {checklist.avarias && checklist.avarias.length > 0 && (
          <div className="mt-6">
            <DamageMap value={checklist.avarias} readOnly onChange={() => {}} />
          </div>
        )}
        {(checklist.assinatura_responsavel || checklist.assinatura_motorista) && (
          <div className="mt-6 space-y-4">
            <h3 className="text-lg font-semibold">Assinaturas</h3>
            <SignaturePad
              readOnly
              value={checklist.assinatura_responsavel}
              onChange={() => {}}
              label="Assinatura do Responsável"
            />
            <SignaturePad
              readOnly
              value={checklist.assinatura_motorista}
              onChange={() => {}}
              label="Assinatura do Motorista"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DevolucaoReadOnly({ checklist }: { checklist: ChecklistResponse }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Checklist de Devolução</CardTitle>
      </CardHeader>
      <CardContent aria-label="Checklist de devolução (somente leitura)">
        {checklist.quilometragem_final != null && (
          <p className="text-sm">
            Quilometragem Final: <strong>{checklist.quilometragem_final} km</strong>
          </p>
        )}
        {checklist.data_devolucao && (
          <p className="mt-2 text-sm">
            Data da Devolução:{" "}
            <strong>
              {new Intl.DateTimeFormat("pt-BR", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              }).format(new Date(checklist.data_devolucao))}
            </strong>
          </p>
        )}
        <div className="mt-4">
          <ChecklistItems readOnly savedItems={checklist.itens_devolucao ?? []} />
        </div>
        {checklist.nivel_combustivel_devolucao && (
          <p className="mt-4 text-sm">
            Nível de Combustível: <strong>{checklist.nivel_combustivel_devolucao}</strong>
          </p>
        )}
        {(checklist.assinatura_responsavel_devolucao || checklist.assinatura_motorista_devolucao) && (
          <div className="mt-6 space-y-4">
            <h3 className="text-lg font-semibold">Assinaturas da Devolução</h3>
            <SignaturePad
              readOnly
              value={checklist.assinatura_responsavel_devolucao}
              onChange={() => {}}
              label="Assinatura do Responsável (Devolução)"
            />
            <SignaturePad
              readOnly
              value={checklist.assinatura_motorista_devolucao}
              onChange={() => {}}
              label="Assinatura do Motorista (Devolução)"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DevolucaoForm({ checklist }: { checklist: ChecklistResponse }) {
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { control, register, reset, handleSubmit, setError, formState: { errors } } = useForm<ChecklistDevolucaoData>({
    resolver: zodResolver(checklistDevolucaoSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((item) => ({ nome: item.nome, status: undefined })),
      nivel_combustivel: undefined,
      quilometragem_final: undefined,
      data_devolucao: "",
      assinatura_responsavel: null,
      assinatura_motorista: null,
    },
  });

  useEffect(() => {
    if (checklist.itens_devolucao) {
      reset({
        itens: CHECKLIST_ITEMS.map((item) => ({
          nome: item.nome,
          status:
            checklist.itens_devolucao?.find((i) => i.nome === item.nome)?.status ?? undefined,
        })),
        nivel_combustivel: checklist.nivel_combustivel_devolucao ?? undefined,
        quilometragem_final: checklist.quilometragem_final ?? undefined,
        data_devolucao: checklist.data_devolucao
          ? checklist.data_devolucao.slice(0, 16)
          : "",
        assinatura_responsavel: checklist.assinatura_responsavel_devolucao ?? null,
        assinatura_motorista: checklist.assinatura_motorista_devolucao ?? null,
      });
    }
  }, [checklist, reset]);

  const onSubmit = (data: ChecklistDevolucaoData) => {
    setSubmitError(null);

    if (data.quilometragem_final < checklist.quilometragem_inicial) {
      setError("quilometragem_final", {
        message: `A Quilometragem Final (${data.quilometragem_final}) não pode ser inferior à Quilometragem Inicial (${checklist.quilometragem_inicial}).`,
      });
      return;
    }

    if (checklist.data_entrega && data.data_devolucao < checklist.data_entrega) {
      setError("data_devolucao", {
        message: "A Data de Devolução não pode ser anterior à Data de Entrega.",
      });
      return;
    }

    void apiClient
      .patch(`/v1/checklists/${checklist.id}/devolucao`, data)
      .catch(() => setSubmitError("Erro ao salvar devolução. Tente novamente."));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Checklist de Devolução</CardTitle>
      </CardHeader>
      <CardContent>
        <form noValidate onSubmit={handleSubmit(onSubmit)}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="quilometragem_final">Quilometragem Final</Label>
              <Input
                id="quilometragem_final"
                type="number"
                step="0.1"
                {...register("quilometragem_final")}
              />
              {errors.quilometragem_final && (
                <p className="text-sm text-danger" role="alert">{errors.quilometragem_final.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="data_devolucao">Data e Horário da Devolução</Label>
              <Input
                id="data_devolucao"
                type="datetime-local"
                {...register("data_devolucao")}
              />
              {errors.data_devolucao && (
                <p className="text-sm text-danger" role="alert">{errors.data_devolucao.message}</p>
              )}
            </div>
          </div>

          <ChecklistItems control={control} errors={errors} />
          <FuelLevel control={control} error={errors.nivel_combustivel} />

          <div className="mt-6 space-y-4">
            <h3 className="text-lg font-semibold">Assinaturas da Devolução</h3>
            <Controller
              name="assinatura_responsavel"
              control={control}
              render={({ field }) => (
                <SignaturePad
                  value={field.value}
                  onChange={field.onChange}
                  label="Assinatura do Responsável"
                />
              )}
            />
            <Controller
              name="assinatura_motorista"
              control={control}
              render={({ field }) => (
                <SignaturePad
                  value={field.value}
                  onChange={field.onChange}
                  label="Assinatura do Motorista"
                />
              )}
            />
          </div>

          {submitError && (
            <p className="mt-4 text-sm text-danger" role="alert">{submitError}</p>
          )}

          <Button
            type="button"
            disabled
            title="Salvar será implementado na Story 5.1"
            className="mt-6 w-full"
          >
            Salvar
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

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

  const entregaForm = useForm<ChecklistEntregaData>({
    resolver: zodResolver(checklistEntregaSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((item) => ({ nome: item.nome, status: undefined })),
      nivel_combustivel: undefined,
      data_entrega: "",
      avarias: [],
      assinatura_responsavel: null,
      assinatura_motorista: null,
    },
  });

  useEffect(() => {
    if (checklist && !checklist.is_locked) {
      entregaForm.reset({
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
        assinatura_responsavel: checklist.assinatura_responsavel ?? null,
        assinatura_motorista: checklist.assinatura_motorista ?? null,
      });
    }
  }, [checklist, entregaForm.reset]);

  if (!id) return <p role="alert" className="p-4 text-danger">ID do checklist inválido.</p>;
  if (isLoading) return <p aria-live="polite" className="p-4 text-muted">Carregando...</p>;
  if (isError) return <p role="alert" className="p-4 text-danger">Erro ao carregar checklist. Tente novamente.</p>;
  if (!checklist) return <p role="alert" className="p-4 text-danger">Checklist não encontrado.</p>;

  const isFillingEntrega = !checklist.is_locked;
  const isFillingDevolucao = checklist.is_locked && checklist.status === "entregue";
  const isFullyCompleted = checklist.is_locked && checklist.status === "devolvido";

  const title = isFillingDevolucao || isFullyCompleted
    ? `Checklist — Nº ${checklist.id}`
    : `Checklist de Entrega — Nº ${checklist.id}`;

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-4">
      <h1 className="text-2xl font-bold">{title}</h1>

      <Card>
        <CardHeader>
          <CardTitle>Informações Gerais</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-muted">Placa</dt>
              <dd className="font-medium">{checklist.placa}</dd>
            </div>
            <div>
              <dt className="text-muted">Unidade</dt>
              <dd className="font-medium">{checklist.unidade}</dd>
            </div>
            {checklist.subunidade && (
              <div>
                <dt className="text-muted">Subunidade</dt>
                <dd className="font-medium">{checklist.subunidade}</dd>
              </div>
            )}
            <div>
              <dt className="text-muted">Motorista</dt>
              <dd className="font-medium">{checklist.motorista}</dd>
            </div>
            <div>
              <dt className="text-muted">Matrícula</dt>
              <dd className="font-medium">{checklist.matricula_motorista}</dd>
            </div>
            <div>
              <dt className="text-muted">Quilometragem</dt>
              <dd className="font-medium">{checklist.quilometragem_inicial} km</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      {isFillingEntrega && (
        <Card>
          <CardHeader>
            <CardTitle>Checklist de Entrega</CardTitle>
          </CardHeader>
          <CardContent>
            <form noValidate>
              <div className="space-y-2">
                <Label htmlFor="data_entrega">Data e Horário da Entrega</Label>
                <Input
                  id="data_entrega"
                  type="datetime-local"
                  {...entregaForm.register("data_entrega")}
                />
                {entregaForm.formState.errors.data_entrega && (
                  <p className="text-sm text-danger" role="alert">{entregaForm.formState.errors.data_entrega.message}</p>
                )}
              </div>

              <ChecklistItems control={entregaForm.control} errors={entregaForm.formState.errors} />
              <FuelLevel control={entregaForm.control} error={entregaForm.formState.errors.nivel_combustivel} />

              <div className="mt-6">
                <Controller
                  name="avarias"
                  control={entregaForm.control}
                  render={({ field }) => (
                    <DamageMap value={field.value} onChange={field.onChange} />
                  )}
                />
              </div>

              <div className="mt-6 space-y-4">
                <h3 className="text-lg font-semibold">Assinaturas</h3>
                <Controller
                  name="assinatura_responsavel"
                  control={entregaForm.control}
                  render={({ field }) => (
                    <SignaturePad
                      value={field.value}
                      onChange={field.onChange}
                      label="Assinatura do Responsável"
                    />
                  )}
                />
                <Controller
                  name="assinatura_motorista"
                  control={entregaForm.control}
                  render={({ field }) => (
                    <SignaturePad
                      value={field.value}
                      onChange={field.onChange}
                      label="Assinatura do Motorista"
                    />
                  )}
                />
              </div>

              <Button
                type="button"
                disabled
                title="Salvar será implementado na Story 5.1"
                className="mt-6 w-full"
              >
                Salvar
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {(isFillingDevolucao || isFullyCompleted) && (
        <EntregaReadOnly checklist={checklist} />
      )}

      {isFillingDevolucao && <DevolucaoForm checklist={checklist} />}

      {isFullyCompleted && <DevolucaoReadOnly checklist={checklist} />}
    </div>
  );
}
