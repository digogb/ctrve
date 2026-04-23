import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import FuelLevel from "../FuelLevel";
import { checklistEntregaSchema, type ChecklistEntregaData } from "../checklistSchema";
import { CHECKLIST_ITEMS } from "../ChecklistItems";

function Wrapper() {
  const { control, formState: { errors } } = useForm<ChecklistEntregaData>({
    resolver: zodResolver(checklistEntregaSchema),
    defaultValues: {
      itens: CHECKLIST_ITEMS.map((i) => ({ nome: i.nome, status: undefined })),
    },
  });
  return <FuelLevel control={control} error={errors.nivel_combustivel} />;
}

describe("FuelLevel", () => {
  it("renderiza as 4 opções de combustível", () => {
    render(<Wrapper />);
    expect(screen.getByRole("radio", { name: "1/4" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "2/4" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "3/4" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "4/4" })).toBeInTheDocument();
  });

  it("seleção exclusiva — selecionar 3/4 desmarca os demais", async () => {
    render(<Wrapper />);
    const radio1 = screen.getByRole("radio", { name: "1/4" });
    const radio3 = screen.getByRole("radio", { name: "3/4" });

    await userEvent.click(radio1);
    expect(radio1).toBeChecked();

    await userEvent.click(radio3);
    expect(radio3).toBeChecked();
    expect(radio1).not.toBeChecked();
  });

  it("nenhuma opção selecionada por padrão", () => {
    render(<Wrapper />);
    const radios = screen.getAllByRole("radio");
    radios.forEach((r) => expect(r).not.toBeChecked());
  });
});
