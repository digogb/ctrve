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
      <section className="checklist-items">
        <h3>Verificar Itens do Veículo</h3>
        <div className="checklist-columns">
          <div className="checklist-column">
            <h4>Documentação/Equipamentos</h4>
            {esquerda.map((item) => {
              const saved = savedItems.find((s) => s.nome === item.nome);
              return (
                <p key={item.nome} className="checklist-item-readonly">
                  {item.nome}: <strong>{statusText(saved?.status)}</strong>
                </p>
              );
            })}
          </div>
          <div className="checklist-column">
            <h4>Condições do Veículo</h4>
            {direita.map((item) => {
              const saved = savedItems.find((s) => s.nome === item.nome);
              return (
                <p key={item.nome} className="checklist-item-readonly">
                  {item.nome}: <strong>{statusText(saved?.status)}</strong>
                </p>
              );
            })}
          </div>
        </div>
      </section>
    );
  }

  const { control, errors } = props;

  return (
    <section className="checklist-items">
      <h3>Verificar Itens do Veículo</h3>
      <div className="checklist-columns">
        <div className="checklist-column">
          <h4>Documentação/Equipamentos</h4>
          {esquerda.map((item) => {
            const index = CHECKLIST_ITEMS.indexOf(item);
            const fieldError = errors.itens?.[index]?.status;
            return (
              <Controller
                key={item.nome}
                name={`itens.${index}.status`}
                control={control}
                render={({ field }) => (
                  <fieldset className="checklist-item">
                    <legend>{item.nome}</legend>
                    <label>
                      <input
                        type="radio"
                        id={`item-${index}-ok`}
                        name={field.name}
                        value="ok"
                        checked={field.value === "ok"}
                        onChange={() => field.onChange("ok")}
                      />
                      OK
                    </label>
                    <label>
                      <input
                        type="radio"
                        id={`item-${index}-nao_ok`}
                        name={field.name}
                        value="nao_ok"
                        checked={field.value === "nao_ok"}
                        onChange={() => field.onChange("nao_ok")}
                      />
                      Não OK
                    </label>
                    {fieldError && (
                      <span className="field-error" role="alert">
                        {fieldError.message}
                      </span>
                    )}
                  </fieldset>
                )}
              />
            );
          })}
        </div>

        <div className="checklist-column">
          <h4>Condições do Veículo</h4>
          {direita.map((item) => {
            const index = CHECKLIST_ITEMS.indexOf(item);
            const fieldError = errors.itens?.[index]?.status;
            return (
              <Controller
                key={item.nome}
                name={`itens.${index}.status`}
                control={control}
                render={({ field }) => (
                  <fieldset className="checklist-item">
                    <legend>{item.nome}</legend>
                    <label>
                      <input
                        type="radio"
                        id={`item-${index}-ok`}
                        name={field.name}
                        value="ok"
                        checked={field.value === "ok"}
                        onChange={() => field.onChange("ok")}
                      />
                      OK
                    </label>
                    <label>
                      <input
                        type="radio"
                        id={`item-${index}-nao_ok`}
                        name={field.name}
                        value="nao_ok"
                        checked={field.value === "nao_ok"}
                        onChange={() => field.onChange("nao_ok")}
                      />
                      Não OK
                    </label>
                    {fieldError && (
                      <span className="field-error" role="alert">
                        {fieldError.message}
                      </span>
                    )}
                  </fieldset>
                )}
              />
            );
          })}
        </div>
      </div>
    </section>
  );
}
