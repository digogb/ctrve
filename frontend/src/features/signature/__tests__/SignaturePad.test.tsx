import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import SignaturePad from "../SignaturePad";

const mockClear = vi.fn();
const mockIsEmpty = vi.fn(() => false);
const mockToDataURL = vi.fn(() => "data:image/png;base64,mockdata");
const mockFromDataURL = vi.fn();

vi.mock("react-signature-canvas", () => {
  const { forwardRef, useImperativeHandle } = require("react");
  return {
    default: forwardRef(function MockSignatureCanvas(
      props: { canvasProps?: Record<string, unknown>; onEnd?: () => void },
      ref: React.Ref<unknown>,
    ) {
      useImperativeHandle(ref, () => ({
        clear: mockClear,
        isEmpty: mockIsEmpty,
        toDataURL: mockToDataURL,
        fromDataURL: mockFromDataURL,
      }));
      return (
        <canvas
          data-testid="signature-canvas"
          {...props.canvasProps}
          onClick={props.onEnd}
        />
      );
    }),
  };
});

const VALID_SIGNATURE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==";

describe("SignaturePad", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsEmpty.mockReturnValue(false);
  });

  it("renderiza canvas com label no modo editável", () => {
    render(
      <SignaturePad value={null} onChange={vi.fn()} label="Assinatura do Responsável" />,
    );

    expect(screen.getByText("Assinatura do Responsável")).toBeInTheDocument();
    expect(screen.getByTestId("signature-canvas")).toBeInTheDocument();
    expect(screen.getByTestId("signature-pad")).toBeInTheDocument();
  });

  it("botão Limpar visível em modo editável", () => {
    render(
      <SignaturePad value={null} onChange={vi.fn()} label="Assinatura do Motorista" />,
    );

    expect(screen.getByRole("button", { name: /limpar/i })).toBeInTheDocument();
  });

  it("botão Limpar chama clear e onChange(null)", () => {
    const onChange = vi.fn();
    render(
      <SignaturePad value={VALID_SIGNATURE} onChange={onChange} label="Assinatura" />,
    );

    fireEvent.click(screen.getByRole("button", { name: /limpar/i }));

    expect(mockClear).toHaveBeenCalled();
    expect(onChange).toHaveBeenCalledWith(null);
  });

  it("modo readOnly com value renderiza img com src correto", () => {
    render(
      <SignaturePad
        value={VALID_SIGNATURE}
        onChange={vi.fn()}
        label="Assinatura do Responsável"
        readOnly
      />,
    );

    const img = screen.getByRole("img", { name: "Assinatura do Responsável" });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", VALID_SIGNATURE);
    expect(screen.getByTestId("signature-readonly")).toBeInTheDocument();
  });

  it("modo readOnly sem value não renderiza nada", () => {
    const { container } = render(
      <SignaturePad
        value={null}
        onChange={vi.fn()}
        label="Assinatura do Motorista"
        readOnly
      />,
    );

    expect(container.innerHTML).toBe("");
  });

  it("botão Limpar ausente em modo readOnly", () => {
    render(
      <SignaturePad
        value={VALID_SIGNATURE}
        onChange={vi.fn()}
        label="Assinatura"
        readOnly
      />,
    );

    expect(screen.queryByRole("button", { name: /limpar/i })).not.toBeInTheDocument();
  });

  it("onEnd do canvas chama onChange com data URL", () => {
    const onChange = vi.fn();
    render(
      <SignaturePad value={null} onChange={onChange} label="Assinatura" />,
    );

    fireEvent.click(screen.getByTestId("signature-canvas"));

    expect(mockToDataURL).toHaveBeenCalledWith("image/png");
    expect(onChange).toHaveBeenCalledWith("data:image/png;base64,mockdata");
  });

  it("useEffect limpa canvas quando value muda para null", () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <SignaturePad value={VALID_SIGNATURE} onChange={onChange} label="Assinatura" />,
    );

    mockClear.mockClear();

    rerender(
      <SignaturePad value={null} onChange={onChange} label="Assinatura" />,
    );

    expect(mockClear).toHaveBeenCalled();
  });
});
