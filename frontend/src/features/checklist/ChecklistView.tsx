import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import apiClient, { isAxiosError } from "../../lib/apiClient";
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
import ObservationsField from "./ObservationsField";
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
        {checklist.observacoes && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold">Observações</h3>
            <p className="mt-2 text-sm whitespace-pre-wrap">{checklist.observacoes}</p>
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
        {checklist.observacoes_devolucao && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold">Observações da Devolução</h3>
            <p className="mt-2 text-sm whitespace-pre-wrap">{checklist.observacoes_devolucao}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DevolucaoForm({ checklist }: { checklist: ChecklistResponse }) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { control, register, reset, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm<ChecklistDevolucaoData>({
    resolver: zodResolver(checklistDevolucaoSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((item) => ({ nome: item.nome, status: undefined })),
      nivel_combustivel: undefined,
      quilometragem_final: undefined,
      data_devolucao: "",
      assinatura_responsavel: null,
      assinatura_motorista: null,
      observacoes: null,
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
        observacoes: checklist.observacoes_devolucao ?? null,
      });
    }
  }, [checklist, reset]);

  const onSubmit = async (data: ChecklistDevolucaoData) => {
    setSubmitError(null);

    if (data.quilometragem_final < checklist.quilometragem_inicial) {
      setError("quilometragem_final", {
        message: `A Quilometragem Final (${data.quilometragem_final}) não pode ser inferior à Quilometragem Inicial (${checklist.quilometragem_inicial}).`,
      });
      return;
    }

    if (checklist.data_entrega && new Date(data.data_devolucao) < new Date(checklist.data_entrega)) {
      setError("data_devolucao", {
        message: "A Data de Devolução não pode ser anterior à Data de Entrega.",
      });
      return;
    }

    if (!window.confirm("Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados.")) {
      return;
    }

    try {
      await apiClient.patch(`/v1/checklists/${checklist.id}/devolucao`, data);
      window.alert("Checklist salvo com sucesso.");
      queryClient.invalidateQueries({ queryKey: ["checklists", String(checklist.id)] });
    } catch (error) {
      if (isAxiosError(error) && error.response?.data?.detail && typeof error.response.data.detail === "string") {
        setSubmitError(error.response.data.detail);
      } else {
        setSubmitError("Erro ao salvar devolução. Tente novamente.");
      }
    }
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
                <>
                  <SignaturePad
                    value={field.value}
                    onChange={field.onChange}
                    label="Assinatura do Responsável"
                  />
                  {errors.assinatura_responsavel && (
                    <p className="text-sm text-danger" role="alert">{errors.assinatura_responsavel.message}</p>
                  )}
                </>
              )}
            />
            <Controller
              name="assinatura_motorista"
              control={control}
              render={({ field }) => (
                <>
                  <SignaturePad
                    value={field.value}
                    onChange={field.onChange}
                    label="Assinatura do Motorista"
                  />
                  {errors.assinatura_motorista && (
                    <p className="text-sm text-danger" role="alert">{errors.assinatura_motorista.message}</p>
                  )}
                </>
              )}
            />
          </div>

          <ObservationsField register={register("observacoes")} label="Observações da Devolução" />

          {submitError && (
            <p className="mt-4 text-sm text-danger" role="alert">{submitError}</p>
          )}

          <Button
            type="submit"
            disabled={isSubmitting}
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
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

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
      observacoes: null,
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
        observacoes: checklist.observacoes ?? null,
      });
    }
  }, [checklist, entregaForm.reset]);

  const onEntregaSubmit = async (data: ChecklistEntregaData) => {
    setSubmitError(null);
    if (!window.confirm("Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados.")) {
      return;
    }
    try {
      await apiClient.patch(`/v1/checklists/${id}/entrega`, data);
      window.alert("Checklist salvo com sucesso.");
      queryClient.invalidateQueries({ queryKey: ["checklists", id ?? ""] });
    } catch (error) {
      if (isAxiosError(error) && error.response?.data?.detail && typeof error.response.data.detail === "string") {
        setSubmitError(error.response.data.detail);
      } else {
        setSubmitError("Erro ao salvar checklist. Tente novamente.");
      }
    }
  };

  const entregaErrors = entregaForm.formState.errors;
  const isEntregaSubmitting = entregaForm.formState.isSubmitting;

  const onDownloadPdf = async () => {
    setIsDownloadingPdf(true);
    let url: string | null = null;
    let link: HTMLAnchorElement | null = null;
    try {
      const response = await apiClient.get(`/v1/checklists/${id}/pdf`, {
        responseType: "blob",
      });
      url = window.URL.createObjectURL(new Blob([response.data]));
      link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `checklist-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      window.alert("PDF gerado com sucesso.");
    } catch (error) {
      if (isAxiosError(error) && error.response?.data) {
        try {
          const text = await (error.response.data as Blob).text();
          const json = JSON.parse(text);
          window.alert(json.message || json.detail || "Erro ao gerar PDF.");
        } catch {
          window.alert("Erro ao gerar PDF. Tente novamente.");
        }
      } else {
        window.alert("Erro ao gerar PDF. Tente novamente.");
      }
    } finally {
      link?.remove();
      if (url) window.URL.revokeObjectURL(url);
      setIsDownloadingPdf(false);
    }
  };

  const onCancel = async () => {
    if (!window.confirm("Deseja cancelar o preenchimento? Todos os dados informados serão descartados.")) {
      return;
    }
    setIsCancelling(true);
    try {
      await apiClient.delete(`/v1/checklists/${id}`);
      navigate("/");
    } catch (error) {
      if (isAxiosError(error) && error.response) {
        const data = error.response.data as { message?: string; detail?: string } | undefined;
        window.alert(data?.message || data?.detail || "Erro ao cancelar checklist.");
      } else {
        navigate("/");
      }
    } finally {
      setIsCancelling(false);
    }
  };

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

      {checklist.is_locked && (
        <Button
          type="button"
          variant="outline"
          onClick={onDownloadPdf}
          disabled={isDownloadingPdf}
        >
          {isDownloadingPdf ? "Gerando PDF..." : "Gerar PDF"}
        </Button>
      )}

      {isFillingEntrega && (
        <Card>
          <CardHeader>
            <CardTitle>Checklist de Entrega</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={entregaForm.handleSubmit(onEntregaSubmit)}>
              <div className="space-y-2">
                <Label htmlFor="data_entrega">Data e Horário da Entrega</Label>
                <Input
                  id="data_entrega"
                  type="datetime-local"
                  {...entregaForm.register("data_entrega")}
                />
                {entregaErrors.data_entrega && (
                  <p className="text-sm text-danger" role="alert">{entregaErrors.data_entrega.message}</p>
                )}
              </div>

              <ChecklistItems control={entregaForm.control} errors={entregaErrors} />
              <FuelLevel control={entregaForm.control} error={entregaErrors.nivel_combustivel} />

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
                    <>
                      <SignaturePad
                        value={field.value}
                        onChange={field.onChange}
                        label="Assinatura do Responsável"
                      />
                      {entregaErrors.assinatura_responsavel && (
                        <p className="text-sm text-danger" role="alert">
                          {entregaErrors.assinatura_responsavel.message}
                        </p>
                      )}
                    </>
                  )}
                />
                <Controller
                  name="assinatura_motorista"
                  control={entregaForm.control}
                  render={({ field }) => (
                    <>
                      <SignaturePad
                        value={field.value}
                        onChange={field.onChange}
                        label="Assinatura do Motorista"
                      />
                      {entregaErrors.assinatura_motorista && (
                        <p className="text-sm text-danger" role="alert">
                          {entregaErrors.assinatura_motorista.message}
                        </p>
                      )}
                    </>
                  )}
                />
              </div>

              <ObservationsField register={entregaForm.register("observacoes")} />

              {submitError && (
                <p className="mt-4 text-sm text-danger" role="alert">{submitError}</p>
              )}

              <div className="mt-6 flex gap-3">
                <Button type="submit" disabled={isEntregaSubmitting} className="flex-1">
                  Salvar
                </Button>
                <Button type="button" variant="outline" onClick={onCancel} disabled={isEntregaSubmitting || isCancelling}>
                  {isCancelling ? "Cancelando..." : "Cancelar"}
                </Button>
              </div>
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
