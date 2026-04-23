import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChecklistView from "../ChecklistView";
import type { ChecklistResponse } from "../../../types/checklist";

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

  it("exibe view read-only quando is_locked = true", async () => {
    const locked: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [
        { nome: "Documento Veicular", status: "ok" },
        { nome: "Chave de Roda", status: "nao_ok" },
      ],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
    renderAt("1");

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /salvar/i })).not.toBeInTheDocument();
      expect(screen.getByText("3/4")).toBeInTheDocument();
      expect(screen.getByText("Documento Veicular:")).toBeInTheDocument();
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
    const locked: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      avarias: [{ x: 50, y: 50, vista: "topo", tipo: "risco" }],
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
    renderAt("1");

    await waitFor(() => {
      expect(screen.getByTestId("damage-map")).toBeInTheDocument();
      expect(screen.getByTestId("damage-point-topo-0")).toBeInTheDocument();
    });
  });

  it("não exibe mapa de avarias readOnly quando locked sem avarias", async () => {
    const locked: ChecklistResponse = {
      ...BASE_CHECKLIST,
      is_locked: true,
      nivel_combustivel: "3/4",
      data_entrega: "2026-04-23T14:00:00Z",
      itens: [{ nome: "Documento Veicular", status: "ok" }],
      avarias: null,
    };
    vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
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
});
