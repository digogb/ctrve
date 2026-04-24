import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChecklistView from "../ChecklistView";
import type { ChecklistResponse } from "../../../types/checklist";

vi.mock("react-signature-canvas", () => {
  const { forwardRef, useImperativeHandle } = require("react");
  return {
    default: forwardRef(function MockSignatureCanvas(
      props: { canvasProps?: Record<string, unknown>; onEnd?: () => void },
      ref: React.Ref<unknown>,
    ) {
      useImperativeHandle(ref, () => ({
        clear: vi.fn(),
        isEmpty: vi.fn(() => true),
        toDataURL: vi.fn(() => "data:image/png;base64,mock"),
      }));
      return <canvas data-testid="signature-canvas" {...props.canvasProps} />;
    }),
  };
});

vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn(() => false),
}));

import apiClient from "../../../lib/apiClient";

const BASE_CHECKLIST: ChecklistResponse = {
  id: 1,
  placa: "ABC1D23",
  unidade: "SECLOG",
  subunidade: null,
  motorista: "João Silva",
  matricula_motorista: "123456",
  quilometragem_inicial: 10000,
  status: "entregue",
  is_locked: false,
  itens: null,
  nivel_combustivel: null,
  data_entrega: null,
  avarias: null,
  assinatura_responsavel: null,
  assinatura_motorista: null,
  quilometragem_final: null,
  data_devolucao: null,
  itens_devolucao: null,
  nivel_combustivel_devolucao: null,
  assinatura_responsavel_devolucao: null,
  assinatura_motorista_devolucao: null,
  created_at: "2026-04-23T10:00:00Z",
};

function renderAt(id: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/checklists/${id}`]}>
        <Routes>
          <Route path="/checklists/:id" element={<ChecklistView />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ChecklistView", () => {
  it("exibe informações gerais do checklist", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("ABC1D23")).toBeInTheDocument();
      expect(screen.getByText("João Silva")).toBeInTheDocument();
      expect(screen.getByText("SECLOG")).toBeInTheDocument();
    });
  });

  it("exibe formulário editável quando não bloqueado", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /salvar/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/data e horário/i)).toBeInTheDocument();
    });
  });

  it("botão Salvar fica desabilitado", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /salvar/i })).toBeDisabled();
    });
  });

  it("exibe view read-only quando status devolvido", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [
        { nome: "Documento Veicular", status: "ok" },
        { nome: "Chave de Roda", status: "nao_ok" },
      ],
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [
        { nome: "Documento Veicular", status: "ok" },
        { nome: "Chave de Roda", status: "ok" },
      ],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /salvar/i })).not.toBeInTheDocument();
      expect(screen.getByText("3/4")).toBeInTheDocument();
      expect(screen.getByText("2/4")).toBeInTheDocument();
      expect(screen.getByText("Checklist de Entrega")).toBeInTheDocument();
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
    });
  });

  it("exibe loading enquanto carrega", () => {
    let resolve: (val: { data: ChecklistResponse }) => void;
    const pending = new Promise<{ data: ChecklistResponse }>((res) => {
      resolve = res;
    });
    vi.mocked(apiClient.get).mockReturnValue(pending as never);
    renderAt("1");

    expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    resolve!({ data: BASE_CHECKLIST });
  });

  it("exibe mapa de avarias no modo editável", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByTestId("damage-map")).toBeInTheDocument();
    });
  });

  it("exibe mapa de avarias readOnly quando locked com avarias", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      avarias: [{ x: 50, y: 50, vista: "topo", tipo: "risco" }],
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByTestId("damage-map")).toBeInTheDocument();
      expect(screen.getByTestId("damage-point-topo-0")).toBeInTheDocument();
    });
  });

  it("não exibe mapa de avarias readOnly quando locked sem avarias", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      avarias: null,
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.queryByTestId("damage-map")).not.toBeInTheDocument();
    });
  });

  it("exibe formulário com os 20 itens do checklist", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Documento Veicular")).toBeInTheDocument();
      expect(screen.getByText("Limpadores de Para-brisa")).toBeInTheDocument();
    });
  });

  it("exibe seção de assinaturas no modo editável", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Assinaturas")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Responsável")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Motorista")).toBeInTheDocument();
    });
  });

  it("modo readOnly com assinaturas exibe imagens", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      assinatura_responsavel: "data:image/png;base64,abc123",
      assinatura_motorista: "data:image/png;base64,def456",
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Assinaturas")).toBeInTheDocument();
      const imgs = screen.getAllByRole("img");
      const sigImgs = imgs.filter(
        (img) =>
          img.getAttribute("alt") === "Assinatura do Responsável" ||
          img.getAttribute("alt") === "Assinatura do Motorista",
      );
      expect(sigImgs).toHaveLength(2);
    });
  });

  // ── Story 4.1: Modo Devolução ──────────────────────────────────────────────

  it("checklist locked+entregue exibe formulário de devolução com 20 itens", async () => {
    const devolucao: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [
        { nome: "Documento Veicular", status: "ok" },
        { nome: "Chave de Roda", status: "nao_ok" },
      ],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucao });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
      expect(screen.getByLabelText(/quilometragem final/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/data e horário da devolução/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /salvar/i })).toBeDisabled();
    });
  });

  it("checklist locked+entregue NÃO exibe DamageMap no formulário de devolução", async () => {
    const devolucao: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      avarias: [{ x: 50, y: 50, vista: "topo", tipo: "risco" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucao });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
      expect(screen.getByTestId("damage-map")).toBeInTheDocument();
    });
    const devolucaoForm = screen.getByText("Checklist de Devolução").closest("section, [class]")?.parentElement;
    const damageMapInDevolucao = devolucaoForm?.querySelector('[data-testid="damage-map"]');
    expect(damageMapInDevolucao).toBeNull();
  });

  it("checklist locked+entregue exibe dados da entrega read-only", async () => {
    const devolucao: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucao });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Entrega")).toBeInTheDocument();
      const entregaSection = screen.getByLabelText("Checklist de entrega (somente leitura)");
      expect(entregaSection).toBeInTheDocument();
      expect(entregaSection).toHaveTextContent("3/4");
    });
  });

  it("checklist devolvido exibe tudo read-only (entrega + devolução)", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Entrega")).toBeInTheDocument();
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
      expect(screen.getByText("12000 km")).toBeInTheDocument();
      expect(screen.getByLabelText("Checklist de entrega (somente leitura)")).toBeInTheDocument();
      expect(screen.getByLabelText("Checklist de devolução (somente leitura)")).toBeInTheDocument();
      expect(screen.queryByRole("button", { name: /salvar/i })).not.toBeInTheDocument();
    });
  });

  it("modo readOnly sem assinaturas não exibe seção de assinaturas", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      assinatura_responsavel: null,
      assinatura_motorista: null,
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
      assinatura_responsavel_devolucao: null,
      assinatura_motorista_devolucao: null,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Entrega")).toBeInTheDocument();
    });
    expect(screen.queryByText("Assinaturas")).not.toBeInTheDocument();
    expect(screen.queryByText("Assinaturas da Devolução")).not.toBeInTheDocument();
  });

  // ── Story 4.2: Assinaturas na Devolução ───────────────────────────────────

  it("checklist locked+entregue exibe seção de assinaturas da devolução", async () => {
    const devolucao: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucao });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Responsável")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Motorista")).toBeInTheDocument();
    });
  });

  it("checklist locked+entregue exibe botões Limpar para assinaturas da devolução", async () => {
    const devolucao: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucao });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument();
    });
    const limparButtons = screen.getAllByRole("button", { name: /limpar/i });
    expect(limparButtons.length).toBeGreaterThanOrEqual(2);
  });

  it("checklist devolvido COM assinaturas de devolução exibe imagens", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
      assinatura_responsavel_devolucao: "data:image/png;base64,devresp",
      assinatura_motorista_devolucao: "data:image/png;base64,devmot",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument();
      const imgs = screen.getAllByRole("img");
      const devSigImgs = imgs.filter(
        (img) =>
          img.getAttribute("alt") === "Assinatura do Responsável (Devolução)" ||
          img.getAttribute("alt") === "Assinatura do Motorista (Devolução)",
      );
      expect(devSigImgs).toHaveLength(2);
    });
  });

  it("checklist devolvido SEM assinaturas de devolução não exibe seção", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      assinatura_responsavel: null,
      assinatura_motorista: null,
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
      assinatura_responsavel_devolucao: null,
      assinatura_motorista_devolucao: null,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
    });
    expect(screen.queryByText("Assinaturas da Devolução")).not.toBeInTheDocument();
  });
});
