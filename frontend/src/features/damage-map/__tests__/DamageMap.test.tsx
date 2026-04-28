import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DamageMap from "../DamageMap";
import type { DamagePoint } from "../../../types/damage";

// Mocka getBoundingClientRect para o container do mapa (300×300px)
function mockContainerRect() {
  Element.prototype.getBoundingClientRect = vi.fn(() => ({
    x: 0, y: 0, width: 300, height: 300,
    top: 0, right: 300, bottom: 300, left: 0,
    toJSON: () => {},
  }));
}

describe("DamageMap", () => {
  beforeEach(() => {
    mockContainerRect();
  });

  it("renderiza o container do mapa de avarias com a imagem", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);
    expect(screen.getByTestId("damage-map")).toBeInTheDocument();
    expect(screen.getByAltText(/mapa de avarias/i)).toBeInTheDocument();
  });

  it("click no mapa exibe seletor de tipo de avaria", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);
    const container = screen.getByTestId("damage-map").querySelector("div")!;
    // y=60 de 300 = 20% → topo
    fireEvent.click(container, { clientX: 150, clientY: 60 });
    expect(screen.getByRole("group", { name: /tipo de avaria/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Risco" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Amassado" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Trincado" })).toBeInTheDocument();
  });

  it("selecionar tipo adiciona ponto com vista=topo quando clique na metade superior", () => {
    const onChange = vi.fn();
    render(<DamageMap value={[]} onChange={onChange} />);
    const container = screen.getByTestId("damage-map").querySelector("div")!;
    // y=60 de 300 = 20% → topo
    fireEvent.click(container, { clientX: 150, clientY: 60 });
    fireEvent.click(screen.getByRole("button", { name: "Risco" }));

    expect(onChange).toHaveBeenCalledTimes(1);
    const [newPoints] = onChange.mock.calls[0];
    expect(newPoints).toHaveLength(1);
    expect(newPoints[0].vista).toBe("topo");
    expect(newPoints[0].tipo).toBe("risco");
    expect(newPoints[0].x).toBeCloseTo(50, 0);
    expect(newPoints[0].y).toBeCloseTo(20, 0);
  });

  it("selecionar tipo adiciona ponto com vista=lateral_esquerda quando clique na metade inferior", () => {
    const onChange = vi.fn();
    render(<DamageMap value={[]} onChange={onChange} />);
    const container = screen.getByTestId("damage-map").querySelector("div")!;
    // y=200 de 300 = 66.7% → lateral_esquerda
    fireEvent.click(container, { clientX: 150, clientY: 200 });
    fireEvent.click(screen.getByRole("button", { name: "Amassado" }));

    const [newPoints] = onChange.mock.calls[0];
    expect(newPoints[0].vista).toBe("lateral_esquerda");
    expect(newPoints[0].tipo).toBe("amassado");
  });

  it("click em ponto existente mostra botão remover e remove o ponto", () => {
    const points: DamagePoint[] = [
      { x: 50, y: 20, vista: "topo", tipo: "risco" },
    ];
    const onChange = vi.fn();
    render(<DamageMap value={points} onChange={onChange} />);

    fireEvent.click(screen.getByTestId("damage-point-topo-0"));
    fireEvent.click(screen.getByRole("button", { name: /remover/i }));

    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("modo readOnly não abre seletor de tipo ao clicar", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} readOnly />);
    const container = screen.getByTestId("damage-map").querySelector("div")!;
    fireEvent.click(container, { clientX: 150, clientY: 60 });
    expect(screen.queryByRole("group", { name: /tipo de avaria/i })).not.toBeInTheDocument();
  });

  it("modo readOnly exibe pontos existentes", () => {
    const points: DamagePoint[] = [
      { x: 50, y: 60, vista: "lateral_esquerda", tipo: "amassado" },
    ];
    render(<DamageMap value={points} onChange={vi.fn()} readOnly />);
    expect(screen.getByTestId("damage-point-lateral_esquerda-0")).toBeInTheDocument();
  });

  it("cancelar seletor de tipo descarta o ponto pendente", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);
    const container = screen.getByTestId("damage-map").querySelector("div")!;
    fireEvent.click(container, { clientX: 150, clientY: 60 });
    expect(screen.getByRole("group", { name: /tipo de avaria/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("group", { name: /tipo de avaria/i })).not.toBeInTheDocument();
  });

  it("renderiza pontos de múltiplas vistas com índice global", () => {
    const points: DamagePoint[] = [
      { x: 30, y: 20, vista: "topo", tipo: "risco" },
      { x: 60, y: 65, vista: "lateral_esquerda", tipo: "trincado" },
      { x: 50, y: 15, vista: "topo", tipo: "amassado" },
    ];
    render(<DamageMap value={points} onChange={vi.fn()} />);
    // índice global: 0, 1, 2
    expect(screen.getByTestId("damage-point-topo-0")).toBeInTheDocument();
    expect(screen.getByTestId("damage-point-lateral_esquerda-1")).toBeInTheDocument();
    expect(screen.getByTestId("damage-point-topo-2")).toBeInTheDocument();
  });

  it("exibe legenda com os 3 tipos de avaria", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);
    expect(screen.getByText("Risco")).toBeInTheDocument();
    expect(screen.getByText("Amassado")).toBeInTheDocument();
    expect(screen.getByText("Trincado")).toBeInTheDocument();
  });
});
