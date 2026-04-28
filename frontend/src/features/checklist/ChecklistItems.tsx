import { Controller, useWatch, type Control, type FieldErrors } from "react-hook-form";
import type { ChecklistEntregaData } from "./checklistSchema";
import type { ChecklistItemData } from "../../types/checklist";

export const CHECKLIST_ITEMS: { nome: string; coluna: "esquerda" | "direita" }[] = [
  { nome: "Documento Veicular", coluna: "esquerda" },
  { nome: "Chave de Roda", coluna: "esquerda" },
  { nome: "Macaco", coluna: "esquerda" },
  { nome: "Triângulo de Sinalização", coluna: "esquerda" },
  { nome: "Estepe", coluna: "esquerda" },
  { nome: "Extintor de Incêndio", coluna: "esquerda" },
  { nome: "Cintos de Segurança", coluna: "esquerda" },
  { nome: "Luzes de Freios", coluna: "esquerda" },
  { nome: "Nível de água (aditivo)", coluna: "esquerda" },
  { nome: "Óleo de motor", coluna: "esquerda" },
  { nome: "Luzes de Posição (faroletes)", coluna: "direita" },
  { nome: "Faróis (alto e baixo)", coluna: "direita" },
  { nome: "Luzes de Seta (pisca-alerta)", coluna: "direita" },
  { nome: "Luz de Placa", coluna: "direita" },
  { nome: "Luz de Ré", coluna: "direita" },
  { nome: "Ar Condicionado", coluna: "direita" },
  { nome: "Buzina", coluna: "direita" },
  { nome: "Rádio/Multimídia", coluna: "direita" },
  { nome: "Fluidos de Freios", coluna: "direita" },
  { nome: "Limpadores de Para-brisa", coluna: "direita" },
];

function statusText(status: string | null | undefined): string {
  if (status === "ok") return "OK";
  if (status === "nao_ok") return "Não OK";
  return "—";
}

interface ChecklistItemsEditProps {
  readOnly?: false;
  control: Control<ChecklistEntregaData>;
  errors: FieldErrors<ChecklistEntregaData>;
  savedItems?: never;
}

interface ChecklistItemsReadOnlyProps {
  readOnly: true;
  savedItems: ChecklistItemData[];
  control?: never;
  errors?: never;
}

type ChecklistItemsProps = ChecklistItemsEditProps | ChecklistItemsReadOnlyProps;

function ChecklistItemsEdit({
  control,
  errors,
}: {
  control: Control<ChecklistEntregaData>;
  errors: FieldErrors<ChecklistEntregaData>;
}) {
  const watchedItems = useWatch({ control, name: "itens" });
  const total = CHECKLIST_ITEMS.length;
  const verificados =
    watchedItems?.filter((i) => i.status === "ok" || i.status === "nao_ok").length ?? 0;

  return (
    <section className="mt-6">
      <div className="flex items-center justify-between mb-3">
        <span className="text-lg font-semibold">Itens de Verificação</span>
        <span className="text-sm text-muted">
          {verificados} / {total} verificados
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {CHECKLIST_ITEMS.map((item, index) => {
          return (
            <Controller
              key={item.nome}
              name={`itens.${index}.status`}
              control={control}
              render={({ field }) => {
                const isOk = field.value === "ok";
                const isNaoOk = field.value === "nao_ok";
                const cardClass = isOk
                  ? "bg-green-50 border-green-400"
                  : isNaoOk
                  ? "bg-red-50 border-red-400"
                  : "bg-white border-gray-200";
                return (
                  <div>
                    <div
                      className={`rounded-xl border px-4 py-3 flex items-center justify-between min-h-[52px] transition-colors ${cardClass}`}
                    >
                      <span className="text-sm font-medium mr-2">{item.nome}</span>
                      <div className="flex gap-1.5 shrink-0">
                        <button
                          type="button"
                          onClick={() => field.onChange("ok")}
                          aria-label={`Marcar ${item.nome} como OK`}
                          aria-pressed={isOk}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                            isOk
                              ? "bg-green-600 text-white"
                              : "bg-white border border-gray-200 text-gray-500"
                          }`}
                        >
                          ✓ OK
                        </button>
                        <button
                          type="button"
                          onClick={() => field.onChange("nao_ok")}
                          aria-label={`Marcar ${item.nome} como Não OK`}
                          aria-pressed={isNaoOk}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                            isNaoOk
                              ? "bg-red-600 text-white"
                              : "bg-white border border-gray-200 text-gray-500"
                          }`}
                        >
                          ✗ Não OK
                        </button>
                      </div>
                    </div>
                    {errors.itens?.[index]?.status && (
                      <p className="mt-1 text-xs text-danger" role="alert">
                        {errors.itens[index].status?.message}
                      </p>
                    )}
                  </div>
                );
              }}
            />
          );
        })}
      </div>
    </section>
  );
}

export default function ChecklistItems(props: ChecklistItemsProps) {
  const esquerda = CHECKLIST_ITEMS.filter((i) => i.coluna === "esquerda");
  const direita = CHECKLIST_ITEMS.filter((i) => i.coluna === "direita");

  if (props.readOnly) {
    const { savedItems } = props;
    return (
      <section className="mt-6">
        <h3 className="mb-3 text-lg font-semibold">Verificar Itens do Veículo</h3>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <h4 className="mb-2 text-sm font-medium text-muted">Documentação/Equipamentos</h4>
            <ul className="space-y-1">
              {esquerda.map((item) => {
                const saved = savedItems.find((s) => s.nome === item.nome);
                return (
                  <li key={item.nome} className="flex items-center justify-between rounded px-2 py-1 text-sm odd:bg-surface">
                    <span>{item.nome}</span>
                    <span className={`font-medium ${saved?.status === "ok" ? "text-success" : saved?.status === "nao_ok" ? "text-danger" : "text-muted"}`}>
                      {statusText(saved?.status)}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
          <div>
            <h4 className="mb-2 text-sm font-medium text-muted">Condições do Veículo</h4>
            <ul className="space-y-1">
              {direita.map((item) => {
                const saved = savedItems.find((s) => s.nome === item.nome);
                return (
                  <li key={item.nome} className="flex items-center justify-between rounded px-2 py-1 text-sm odd:bg-surface">
                    <span>{item.nome}</span>
                    <span className={`font-medium ${saved?.status === "ok" ? "text-success" : saved?.status === "nao_ok" ? "text-danger" : "text-muted"}`}>
                      {statusText(saved?.status)}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </section>
    );
  }

  return <ChecklistItemsEdit control={props.control} errors={props.errors} />;
}
