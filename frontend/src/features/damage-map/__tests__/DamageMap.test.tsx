import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DamageMap from "../DamageMap";
import type { DamagePoint } from "../../../types/damage";

function mockSvgBoundingRect() {
  Element.prototype.getBoundingClientRect = vi.fn(() => ({
    x: 0,
    y: 0,
    width: 300,
    height: 270,
    top: 0,
    right: 300,
    bottom: 270,
    left: 0,
    toJSON: () => {},
  }));
}

describe("DamageMap", () => {
  beforeEach(() => {
    mockSvgBoundingRect();
  });

  it("renderiza 4 vistas SVG identificáveis", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);

    expect(screen.getByTestId("vehicle-view-topo")).toBeInTheDocument();
    expect(screen.getByTestId("vehicle-view-lateral_esquerda")).toBeInTheDocument();
    expect(screen.getByTestId("vehicle-view-lateral_direita")).toBeInTheDocument();
    expect(screen.getByTestId("vehicle-view-frontal_traseira")).toBeInTheDocument();
  });

  it("click em vista exibe seletor de tipo", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);

    const topoView = screen.getByTestId("vehicle-view-topo");
    const svg = topoView.querySelector("svg")!;
    fireEvent.click(svg, { clientX: 150, clientY: 135 });

    expect(screen.getByRole("group", { name: /tipo de avaria/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Risco" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Amassado" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Trincado" })).toBeInTheDocument();
  });

  it("selecionar tipo adiciona ponto ao array via onChange", () => {
    const onChange = vi.fn();
    render(<DamageMap value={[]} onChange={onChange} />);

    const topoView = screen.getByTestId("vehicle-view-topo");
    const svg = topoView.querySelector("svg")!;
    fireEvent.click(svg, { clientX: 150, clientY: 135 });

    const riscoBtn = screen.getByRole("button", { name: "Risco" });
    fireEvent.click(riscoBtn);

    expect(onChange).toHaveBeenCalledTimes(1);
    const newPoints = onChange.mock.calls[0][0];
    expect(newPoints).toHaveLength(1);
    expect(newPoints[0].vista).toBe("topo");
    expect(newPoints[0].tipo).toBe("risco");
    expect(newPoints[0].x).toBeCloseTo(50, 0);
    expect(newPoints[0].y).toBeCloseTo(50, 0);
  });

  it("click em ponto existente mostra opção remover, e remover remove o ponto", () => {
    const points: DamagePoint[] = [
      { x: 50, y: 50, vista: "topo", tipo: "risco" },
    ];
    const onChange = vi.fn();
    render(<DamageMap value={points} onChange={onChange} />);

    const pointEl = screen.getByTestId("damage-point-topo-0");
    fireEvent.click(pointEl);

    const removeBtn = screen.getByRole("button", { name: /remover/i });
    fireEvent.click(removeBtn);

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange.mock.calls[0][0]).toHaveLength(0);
  });

  it("modo readOnly exibe pontos sem click handlers", () => {
    const points: DamagePoint[] = [
      { x: 50, y: 50, vista: "lateral_esquerda", tipo: "amassado" },
    ];
    const onChange = vi.fn();
    render(<DamageMap value={points} onChange={onChange} readOnly />);

    expect(screen.getByTestId("damage-point-lateral_esquerda-0")).toBeInTheDocument();

    const svg = screen.getByTestId("vehicle-view-lateral_esquerda").querySelector("svg")!;
    fireEvent.click(svg, { clientX: 150, clientY: 135 });

    expect(screen.queryByRole("group", { name: /tipo de avaria/i })).not.toBeInTheDocument();
    expect(onChange).not.toHaveBeenCalled();
  });

  it("cancelar seletor de tipo remove ponto pendente", () => {
    render(<DamageMap value={[]} onChange={vi.fn()} />);

    const svg = screen.getByTestId("vehicle-view-topo").querySelector("svg")!;
    fireEvent.click(svg, { clientX: 150, clientY: 135 });

    expect(screen.getByRole("group", { name: /tipo de avaria/i })).toBeInTheDocument();

    const cancelBtn = screen.getByRole("button", { name: "Cancelar" });
    fireEvent.click(cancelBtn);

    expect(screen.queryByRole("group", { name: /tipo de avaria/i })).not.toBeInTheDocument();
  });

  it("renderiza pontos de múltiplas vistas corretamente", () => {
    const points: DamagePoint[] = [
      { x: 30, y: 40, vista: "topo", tipo: "risco" },
      { x: 60, y: 70, vista: "lateral_direita", tipo: "trincado" },
      { x: 50, y: 50, vista: "topo", tipo: "amassado" },
    ];
    render(<DamageMap value={points} onChange={vi.fn()} />);

    expect(screen.getByTestId("damage-point-topo-0")).toBeInTheDocument();
    expect(screen.getByTestId("damage-point-topo-1")).toBeInTheDocument();
    expect(screen.getByTestId("damage-point-lateral_direita-0")).toBeInTheDocument();
  });
});
