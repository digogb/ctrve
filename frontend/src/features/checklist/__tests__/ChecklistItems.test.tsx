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

  it("renderiza itens de Documentação/Equipamentos", () => {
    render(<Wrapper />);
    expect(screen.getByText("Documento Veicular")).toBeInTheDocument();
    expect(screen.getByText("Óleo de motor")).toBeInTheDocument();
  });

  it("renderiza itens de Condições do Veículo", () => {
    render(<Wrapper />);
    expect(screen.getByText("Luzes de Posição (faroletes)")).toBeInTheDocument();
    expect(screen.getByText("Limpadores de Para-brisa")).toBeInTheDocument();
  });

  it("permite selecionar OK no primeiro item", async () => {
    render(<Wrapper />);
    const okButtons = screen.getAllByText("✓ OK");
    expect(okButtons.length).toBeGreaterThan(0);
    await userEvent.click(okButtons[0]);
  });

  it("permite selecionar Não OK no primeiro item", async () => {
    render(<Wrapper />);
    const naoOkButtons = screen.getAllByText("✗ Não OK");
    expect(naoOkButtons.length).toBeGreaterThan(0);
    await userEvent.click(naoOkButtons[0]);
  });

  it("cada item tem botões OK e Não OK", () => {
    render(<Wrapper />);
    const okButtons = screen.getAllByText("✓ OK");
    const naoOkButtons = screen.getAllByText("✗ Não OK");
    expect(okButtons).toHaveLength(20);
    expect(naoOkButtons).toHaveLength(20);
  });

  it("exibe contador 0 / 20 verificados inicialmente", () => {
    render(<Wrapper />);
    expect(screen.getByText(/0 \/ 20 verificados/)).toBeInTheDocument();
  });

  it("exibe contador atualizado após selecionar um item", async () => {
    render(<Wrapper />);
    const okButtons = screen.getAllByText("✓ OK");
    await userEvent.click(okButtons[0]);
    expect(screen.getByText(/1 \/ 20 verificados/)).toBeInTheDocument();
  });
});
