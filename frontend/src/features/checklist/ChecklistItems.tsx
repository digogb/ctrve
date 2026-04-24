import { Controller, type Control, type FieldErrors } from "react-hook-form";
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

  const { control, errors } = props;

  const renderColumn = (items: typeof CHECKLIST_ITEMS, title: string) => (
    <div>
      <h4 className="mb-2 text-sm font-medium text-muted">{title}</h4>
      <div className="space-y-2">
        {items.map((item) => {
          const index = CHECKLIST_ITEMS.indexOf(item);
          const fieldError = errors.itens?.[index]?.status;
          return (
            <Controller
              key={item.nome}
              name={`itens.${index}.status`}
              control={control}
              render={({ field }) => (
                <fieldset className="rounded-md border px-3 py-2">
                  <legend className="text-sm font-medium">{item.nome}</legend>
                  <div className="mt-1 flex gap-4">
                    <label className="flex items-center gap-1.5 text-sm">
                      <input
                        type="radio"
                        id={`item-${index}-ok`}
                        name={field.name}
                        value="ok"
                        checked={field.value === "ok"}
                        onChange={() => field.onChange("ok")}
                        className="accent-success"
                      />
                      OK
                    </label>
                    <label className="flex items-center gap-1.5 text-sm">
                      <input
                        type="radio"
                        id={`item-${index}-nao_ok`}
                        name={field.name}
                        value="nao_ok"
                        checked={field.value === "nao_ok"}
                        onChange={() => field.onChange("nao_ok")}
                        className="accent-danger"
                      />
                      Não OK
                    </label>
                  </div>
                  {fieldError && (
                    <p className="mt-1 text-xs text-danger" role="alert">{fieldError.message}</p>
                  )}
                </fieldset>
              )}
            />
          );
        })}
      </div>
    </div>
  );

  return (
    <section className="mt-6">
      <h3 className="mb-3 text-lg font-semibold">Verificar Itens do Veículo</h3>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {renderColumn(esquerda, "Documentação/Equipamentos")}
        {renderColumn(direita, "Condições do Veículo")}
      </div>
    </section>
  );
}
