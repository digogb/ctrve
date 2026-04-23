import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import ChecklistItems, { CHECKLIST_ITEMS } from "../ChecklistItems";
import { checklistEntregaSchema, type ChecklistEntregaData } from "../checklistSchema";

function Wrapper({ defaultValues }: { defaultValues?: Partial<ChecklistEntregaData> }) {
  const { control, formState: { errors } } = useForm<ChecklistEntregaData>({
    resolver: zodResolver(checklistEntregaSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((i) => ({ nome: i.nome, status: undefined })),
      ...defaultValues,
    },
  });
  return <ChecklistItems control={control} errors={errors} />;
}

describe("ChecklistItems", () => {
  it("renderiza os 20 itens", () => {
    render(<Wrapper />);
    for (const item of CHECKLIST_ITEMS) {
      expect(screen.getByText(item.nome)).toBeInTheDocument();
    }
  });

  it("renderiza 10 itens na coluna Documentação/Equipamentos", () => {
    render(<Wrapper />);
    expect(screen.getByText("Documentação/Equipamentos")).toBeInTheDocument();
    expect(screen.getByText("Documento Veicular")).toBeInTheDocument();
    expect(screen.getByText("Óleo de motor")).toBeInTheDocument();
  });

  it("renderiza 10 itens na coluna Condições do Veículo", () => {
    render(<Wrapper />);
    expect(screen.getByText("Condições do Veículo")).toBeInTheDocument();
    expect(screen.getByText("Luzes de Posição (faroletes)")).toBeInTheDocument();
    expect(screen.getByText("Limpadores de Para-brisa")).toBeInTheDocument();
  });

  it("permite selecionar OK no primeiro item", async () => {
    render(<Wrapper />);
    const radios = screen.getAllByRole("radio", { name: "OK" });
    await userEvent.click(radios[0]);
    expect(radios[0]).toBeChecked();
  });

  it("permite selecionar Não OK no primeiro item", async () => {
    render(<Wrapper />);
    const radios = screen.getAllByRole("radio", { name: "Não OK" });
    await userEvent.click(radios[0]);
    expect(radios[0]).toBeChecked();
  });

  it("cada item tem radio buttons OK e Não OK", () => {
    render(<Wrapper />);
    const okRadios = screen.getAllByRole("radio", { name: "OK" });
    const naoOkRadios = screen.getAllByRole("radio", { name: "Não OK" });
    expect(okRadios).toHaveLength(20);
    expect(naoOkRadios).toHaveLength(20);
  });
});
