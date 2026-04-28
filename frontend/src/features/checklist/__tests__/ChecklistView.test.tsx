import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
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
        fromDataURL: vi.fn(),
      }));
      return <canvas data-testid="signature-canvas" {...props.canvasProps} />;
    }),
  };
});

vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    delete: vi.fn(),
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn(() => false),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import apiClient, { isAxiosError } from "../../../lib/apiClient";
import { toast } from "sonner";

const MOCK_SIG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";

const ALL_ITEM_NAMES = [
  "Documento Veicular", "Chave de Roda", "Macaco", "Triângulo de Sinalização",
  "Estepe", "Extintor de Incêndio", "Cintos de Segurança", "Luzes de Freios",
  "Nível de água (aditivo)", "Óleo de motor",
  "Luzes de Posição (faroletes)", "Faróis (alto e baixo)", "Luzes de Seta (pisca-alerta)",
  "Luz de Placa", "Luz de Ré", "Ar Condicionado", "Buzina",
  "Rádio/Multimídia", "Fluidos de Freios", "Limpadores de Para-brisa",
];

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
  observacoes: null,
  observacoes_devolucao: null,
  created_at: "2026-04-23T10:00:00Z",
};

const FILLED_ENTREGA_CHECKLIST: ChecklistResponse = {
  ...BASE_CHECKLIST,
  is_locked: false,
  itens: ALL_ITEM_NAMES.map((nome) => ({ nome, status: "ok" as const })),
  nivel_combustivel: "3/4",
  data_entrega: "2026-04-23T14:00:00Z",
  assinatura_responsavel: null,
  assinatura_motorista: null,
};

const COMPLETE_DEVOLUCAO_CHECKLIST: ChecklistResponse = {
  ...BASE_CHECKLIST,
  is_locked: true,
  status: "entregue",
  quilometragem_inicial: 10000,
  nivel_combustivel: "3/4",
  data_entrega: "2026-04-20T10:00:00Z",
  itens: ALL_ITEM_NAMES.map((nome) => ({ nome, status: "ok" as const })),
  itens_devolucao: ALL_ITEM_NAMES.map((nome) => ({ nome, status: "ok" as const })),
  nivel_combustivel_devolucao: "2/4",
  quilometragem_final: 12000,
  data_devolucao: "2026-04-23T18:00:00Z",
  assinatura_responsavel_devolucao: null,
  assinatura_motorista_devolucao: null,
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

async function navigateEntregaToStep2() {
  await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
  fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
  await waitFor(() => expect(screen.getByLabelText(/data e horário da entrega/i)).toBeInTheDocument());
}

async function navigateEntregaToStep3() {
  await navigateEntregaToStep2();
  fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
  await waitFor(() => expect(screen.getByRole("heading", { name: /assinaturas/i, level: 3 })).toBeInTheDocument());
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
      expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /próximo/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
    });
  });

  it("botão Próximo está habilitado no formulário de entrega (etapa 1)", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /próximo/i })).not.toBeDisabled();
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
    vi.mocked(apiClient.get).mockResolvedValue({ data: FILLED_ENTREGA_CHECKLIST });
    renderAt("1");
    await navigateEntregaToStep2();

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
    vi.mocked(apiClient.get).mockResolvedValue({ data: FILLED_ENTREGA_CHECKLIST });
    renderAt("1");
    await navigateEntregaToStep3();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /assinaturas/i, level: 3 })).toBeInTheDocument();
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
      expect(screen.getAllByText("Assinaturas")[0]).toBeInTheDocument();
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
      expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /próximo/i })).not.toBeDisabled();
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
    vi.mocked(apiClient.get).mockResolvedValue({ data: COMPLETE_DEVOLUCAO_CHECKLIST });
    renderAt("1");

    await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByLabelText(/quilometragem final/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));

    await waitFor(() => {
      expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Responsável")).toBeInTheDocument();
      expect(screen.getByText("Assinatura do Motorista")).toBeInTheDocument();
    });
  });

  it("checklist locked+entregue exibe botões Limpar para assinaturas da devolução", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: COMPLETE_DEVOLUCAO_CHECKLIST });
    renderAt("1");

    await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByLabelText(/quilometragem final/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));

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

  // ── Story 4.3: Registrar Observações (RN-020) ─────────────────────────────

  it("formulário de entrega exibe campo de observações", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: FILLED_ENTREGA_CHECKLIST });
    renderAt("1");
    await navigateEntregaToStep2();

    await waitFor(() => {
      expect(screen.getByLabelText("Observações")).toBeInTheDocument();
    });
  });

  it("formulário de devolução exibe campo de observações da devolução", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: COMPLETE_DEVOLUCAO_CHECKLIST });
    renderAt("1");

    await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));

    await waitFor(() => {
      expect(screen.getByLabelText("Observações da Devolução")).toBeInTheDocument();
    });
  });

  it("EntregaReadOnly COM observacoes exibe seção", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      observacoes: "Pneu careca no eixo traseiro",
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Observações")).toBeInTheDocument();
      expect(screen.getByText("Pneu careca no eixo traseiro")).toBeInTheDocument();
    });
  });

  it("EntregaReadOnly SEM observacoes não exibe seção", async () => {
    const devolvido: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "devolvido",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      observacoes: null,
      quilometragem_final: 12000,
      data_devolucao: "2026-04-23T18:00:00Z",
      itens_devolucao: [{ nome: "Estepe", status: "ok" }],
      nivel_combustivel_devolucao: "2/4",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Entrega")).toBeInTheDocument();
    });
    const entregaSection = screen.getByLabelText("Checklist de entrega (somente leitura)");
    expect(entregaSection).not.toHaveTextContent("Observações");
  });

  it("DevolucaoReadOnly COM observacoes_devolucao exibe seção", async () => {
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
      observacoes_devolucao: "Retrovisor danificado",
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Observações da Devolução")).toBeInTheDocument();
      expect(screen.getByText("Retrovisor danificado")).toBeInTheDocument();
    });
  });

  it("DevolucaoReadOnly SEM observacoes_devolucao não exibe seção", async () => {
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
      observacoes_devolucao: null,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("Checklist de Devolução")).toBeInTheDocument();
    });
    const devolucaoSection = screen.getByLabelText("Checklist de devolução (somente leitura)");
    expect(devolucaoSection).not.toHaveTextContent("Observações da Devolução");
  });

  // ── Story 5.1: Salvar Checklist ───────────────────────────────────────────

  it("T6.1 — botão Próximo habilitado no formulário de entrega (etapa 1)", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      const btn = screen.getByRole("button", { name: /próximo/i });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toBeDisabled();
    });
  });

  it("T6.2 — botão Próximo habilitado no formulário de devolução (etapa 1)", async () => {
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
      const btn = screen.getByRole("button", { name: /próximo/i });
      expect(btn).toBeInTheDocument();
      expect(btn).not.toBeDisabled();
    });
  });

  it("T6.3 — submit com assinaturas faltando exibe erro de validação", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: FILLED_ENTREGA_CHECKLIST });
    renderAt("1");
    await navigateEntregaToStep3();

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/assinatura do responsável é obrigatória/i)
      ).toBeInTheDocument();
    });
  });

  it("T6.4 — submit bem-sucedido na entrega chama apiClient.patch", async () => {
    const filledChecklist: ChecklistResponse = {
      ...FILLED_ENTREGA_CHECKLIST,
      assinatura_responsavel: MOCK_SIG,
      assinatura_motorista: MOCK_SIG,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: filledChecklist });
    vi.mocked(apiClient.patch).mockResolvedValue({ data: { ...filledChecklist, is_locked: true } });
    renderAt("1");
    await navigateEntregaToStep3();

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /confirmar/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    await waitFor(() => {
      expect(apiClient.patch).toHaveBeenCalledWith(
        "/v1/checklists/1/entrega",
        expect.objectContaining({ assinatura_responsavel: MOCK_SIG })
      );
    });
  });

  it("T6.5 — submit bem-sucedido na devolução chama apiClient.patch", async () => {
    const devolucaoChecklist: ChecklistResponse = {
      ...COMPLETE_DEVOLUCAO_CHECKLIST,
      assinatura_responsavel_devolucao: MOCK_SIG,
      assinatura_motorista_devolucao: MOCK_SIG,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucaoChecklist });
    vi.mocked(apiClient.patch).mockResolvedValue({ data: { ...devolucaoChecklist, status: "devolvido" } });
    renderAt("1");

    await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByLabelText(/quilometragem final/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /confirmar/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    await waitFor(() => {
      expect(apiClient.patch).toHaveBeenCalledWith(
        "/v1/checklists/1/devolucao",
        expect.objectContaining({ assinatura_responsavel: MOCK_SIG })
      );
    });
  });

  it("T6.6 — Dialog de confirmação é exibido antes do PATCH na entrega", async () => {
    const filledChecklist: ChecklistResponse = {
      ...FILLED_ENTREGA_CHECKLIST,
      assinatura_responsavel: MOCK_SIG,
      assinatura_motorista: MOCK_SIG,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: filledChecklist });
    renderAt("1");
    await navigateEntregaToStep3();

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(screen.getByText(/salvar checklist\?/i)).toBeInTheDocument();
    });
    expect(apiClient.patch).not.toHaveBeenCalled();
  });

  it("T6.7 — erro do backend (400) exibe mensagem do detail na entrega", async () => {
    const filledChecklist: ChecklistResponse = {
      ...FILLED_ENTREGA_CHECKLIST,
      assinatura_responsavel: MOCK_SIG,
      assinatura_motorista: MOCK_SIG,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: filledChecklist });
    const axiosErr = { response: { data: { detail: "MSG-026" } } };
    vi.mocked(apiClient.patch).mockRejectedValue(axiosErr);
    vi.mocked(isAxiosError).mockReturnValue(true);
    renderAt("1");
    await navigateEntregaToStep3();

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /confirmar/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    await waitFor(() => {
      expect(screen.getByText("MSG-026")).toBeInTheDocument();
    });
  });

  // ── Story 5.2: Gerar e Compartilhar PDF ──────────────────────────────────

  it("T7.1 — botão Gerar PDF visível quando checklist está locked", async () => {
    const locked: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /gerar pdf/i })).toBeInTheDocument();
    });
  });

  it("T7.2 — botão Gerar PDF não visível quando checklist não está locked", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByText("ABC1D23")).toBeInTheDocument();
    });
    expect(screen.queryByRole("button", { name: /gerar pdf/i })).not.toBeInTheDocument();
  });

  it("T7.3 — clique no botão Gerar PDF chama endpoint com responseType blob", async () => {
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
    const pdfBlob = new Blob(["%PDF-1.4 mock"], { type: "application/pdf" });
    vi.mocked(apiClient.get).mockImplementation((url: string, config?: Record<string, unknown>) => {
      if (config?.responseType === "blob") {
        return Promise.resolve({ data: pdfBlob });
      }
      return Promise.resolve({ data: devolvido });
    });
    const createObjectURL = vi.fn(() => "blob:mock-url");
    const revokeObjectURL = vi.fn();
    window.URL.createObjectURL = createObjectURL;
    window.URL.revokeObjectURL = revokeObjectURL;
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /gerar pdf/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /gerar pdf/i }));

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith(
        "/v1/checklists/1/pdf",
        { responseType: "blob" },
      );
      expect(toast.success).toHaveBeenCalledWith("PDF gerado com sucesso.");
      expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock-url");
    });
  });

  it("T7.4 — erro ao gerar PDF exibe alerta ao usuário", async () => {
    const locked: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue",
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
    };
    const errorBlob = new Blob([JSON.stringify({ detail: "MSG-019" })], { type: "application/json" });
    vi.mocked(apiClient.get).mockImplementation((url: string, config?: Record<string, unknown>) => {
      if (config?.responseType === "blob") {
        return Promise.reject({ response: { data: errorBlob } });
      }
      return Promise.resolve({ data: locked });
    });
    vi.mocked(isAxiosError).mockReturnValue(true);
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /gerar pdf/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /gerar pdf/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("MSG-019");
    });
  });

  it("T6.8 — erro do backend (400) exibe mensagem do detail na devolução", async () => {
    const devolucaoChecklist: ChecklistResponse = {
      ...COMPLETE_DEVOLUCAO_CHECKLIST,
      assinatura_responsavel_devolucao: MOCK_SIG,
      assinatura_motorista_devolucao: MOCK_SIG,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolucaoChecklist });
    const axiosErr = { response: { data: { detail: "Erro de negócio específico." } } };
    vi.mocked(apiClient.patch).mockRejectedValue(axiosErr);
    vi.mocked(isAxiosError).mockReturnValue(true);
    renderAt("1");

    await waitFor(() => expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByLabelText(/quilometragem final/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));
    await waitFor(() => expect(screen.getByText("Assinaturas da Devolução")).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: /salvar checklist/i }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /confirmar/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    await waitFor(() => {
      expect(screen.getByText("Erro de negócio específico.")).toBeInTheDocument();
    });
  });

  // ── Story 6.3: Navegação entre etapas ────────────────────────────────────

  it("S6.3 — Próximo → sem itens marcados exibe erro e não avança para etapa 2", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");

    await waitFor(() => expect(screen.getByRole("button", { name: /próximo/i })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /próximo/i }));

    await waitFor(() => {
      expect(screen.getByText(/todos os itens devem ser verificados/i)).toBeInTheDocument();
    });
    // Should still be in step 1
    expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
    expect(screen.queryByLabelText(/data e horário da entrega/i)).not.toBeInTheDocument();
  });

  it("S6.3 — ← Voltar na etapa 2 retorna à etapa 1 com dados preservados", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: FILLED_ENTREGA_CHECKLIST });
    renderAt("1");
    await navigateEntregaToStep2();

    const voltarButtons = screen.getAllByRole("button", { name: /voltar/i });
    fireEvent.click(voltarButtons[voltarButtons.length - 1]);

    await waitFor(() => {
      expect(screen.getAllByText("✓ OK")[0]).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /próximo/i })).toBeInTheDocument();
    });
  });

  it("exibe botão Cancelar quando checklist não está salvo", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
    });
  });

  it("não exibe botão Cancelar quando checklist está salvo", async () => {
    const locked = { ...BASE_CHECKLIST, is_locked: true };
    vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
    renderAt("1");
    await waitFor(() => {
      expect(screen.getByText(/checklist de entrega/i)).toBeInTheDocument();
    });
    expect(screen.queryByRole("button", { name: /cancelar/i })).not.toBeInTheDocument();
  });

  it("clique em Cancelar com confirmação chama DELETE", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    vi.mocked(apiClient.delete).mockResolvedValue({});

    renderAt("1");
    await waitFor(() => screen.getByRole("button", { name: /cancelar/i }));
    fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));

    await waitFor(() => expect(screen.getByText(/cancelar checklist\?/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /descartar/i }));

    await waitFor(() => {
      expect(apiClient.delete).toHaveBeenCalledWith("/v1/checklists/1");
    });
  });

  it("clique em Cancelar com negação não chama DELETE", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });

    renderAt("1");
    await waitFor(() => screen.getByRole("button", { name: /cancelar/i }));
    fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /continuar editando/i })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /continuar editando/i }));

    expect(apiClient.delete).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument());
  });

  it("exibe botão Voltar quando checklist não está salvo", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    renderAt("1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
    });
  });

  it("exibe botão Voltar quando checklist está em modo read-only", async () => {
    const devolvido = { ...BASE_CHECKLIST, is_locked: true, status: "devolvido" as const };
    vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
    renderAt("1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
    });
  });

  it("exibe botão Voltar quando checklist está preenchendo devolução (AC-1)", async () => {
    const fillingDevolucao = { ...BASE_CHECKLIST, is_locked: true, status: "entregue" as const };
    vi.mocked(apiClient.get).mockResolvedValue({ data: fillingDevolucao });
    renderAt("1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
    });
  });

  it("Voltar sem alterações no form navega sem confirm", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    const confirmSpy = vi.spyOn(window, "confirm");

    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/", "/checklists/1"]} initialIndex={1}>
          <Routes>
            <Route path="/" element={<div data-testid="home">Home</div>} />
            <Route path="/checklists/:id" element={<ChecklistView />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => screen.getByRole("button", { name: /voltar/i }));
    fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

    expect(confirmSpy).not.toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.getByTestId("home")).toBeInTheDocument();
    });
  });

  it("Voltar com form sujo exibe MSG-021", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    vi.spyOn(window, "confirm").mockReturnValueOnce(false);
    renderAt("1");

    await waitFor(() => screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getAllByText("✓ OK")[0]);

    fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

    expect(window.confirm).toHaveBeenCalledWith(
      "Existem dados não salvos neste formulário. Deseja sair sem salvar?"
    );
  });

  it("Voltar com negação não navega e permanece na tela", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    vi.spyOn(window, "confirm").mockReturnValueOnce(false);

    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/", "/checklists/1"]} initialIndex={1}>
          <Routes>
            <Route path="/" element={<div data-testid="home">Home</div>} />
            <Route path="/checklists/:id" element={<ChecklistView />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

    expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
    expect(screen.queryByTestId("home")).not.toBeInTheDocument();
  });

  it("Voltar com form devolução sujo exibe MSG-021 (AC-6)", async () => {
    const fillingDevolucao = {
      ...BASE_CHECKLIST,
      is_locked: true,
      status: "entregue" as const,
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: ALL_ITEM_NAMES.map((nome) => ({ nome, status: "ok" as const })),
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: fillingDevolucao });
    vi.spyOn(window, "confirm").mockReturnValueOnce(false);
    renderAt("1");

    // DevolucaoForm step 1: click OK on first item to make form dirty
    await waitFor(() => screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getAllByText("✓ OK")[0]);

    fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalledWith(
        "Existem dados não salvos neste formulário. Deseja sair sem salvar?"
      );
    });
  });

  it("Voltar com confirmação navega para tela anterior", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
    vi.spyOn(window, "confirm").mockReturnValueOnce(true);

    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/", "/checklists/1"]} initialIndex={1}>
          <Routes>
            <Route path="/" element={<div data-testid="home">Home</div>} />
            <Route path="/checklists/:id" element={<ChecklistView />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getAllByText("✓ OK")[0]);
    fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

    await waitFor(() => {
      expect(screen.getByTestId("home")).toBeInTheDocument();
    });
  });
});
