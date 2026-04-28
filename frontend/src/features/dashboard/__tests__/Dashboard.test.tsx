import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Dashboard from "../Dashboard";
import { AuthContext } from "../../auth/AuthContext";
import type { AuthContextValue } from "../../auth/AuthContext";
import type { User } from "../../../types/user";
import type { ChecklistResponse } from "../../../types/checklist";

vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn(() => false),
}));

import apiClient from "../../../lib/apiClient";

const USER: User = {
  id: 1,
  username: "ana.lima",
  full_name: "Ana Lima",
  matricula: "111111",
  role: "responsavel",
  is_active: true,
};

function makeAuthCtx(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: USER,
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    loginError: null,
    setLoginError: vi.fn(),
    ...overrides,
  };
}

function makeChecklist(overrides: Partial<ChecklistResponse> = {}): ChecklistResponse {
  return {
    id: 1,
    placa: "ABC1D23",
    unidade: "SECLOG",
    subunidade: null,
    motorista: "João",
    matricula_motorista: "222222",
    quilometragem_inicial: 10000,
    status: "entregue",
    is_locked: true,
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
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

function renderDashboard(authCtx?: Partial<AuthContextValue>, checklists: ChecklistResponse[] = []) {
  vi.mocked(apiClient.get).mockResolvedValue({ data: checklists });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <AuthContext.Provider value={makeAuthCtx(authCtx)}>
        <MemoryRouter>
          <Dashboard />
        </MemoryRouter>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

beforeEach(() => vi.clearAllMocks());

describe("Dashboard — saudação e data (RN-001)", () => {
  it("exibe saudação com primeiro nome do usuário", async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Olá, Ana");
    });
  });

  it("exibe 'Olá' quando user é null", async () => {
    renderDashboard({ user: null, isAuthenticated: false });
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Olá");
    });
  });
});

describe("Dashboard — cards de estatísticas (RN-004, RN-009)", () => {
  it("exibe zero em todos os contadores quando não há checklists", async () => {
    renderDashboard({}, []);
    await waitFor(() => {
      const cards = screen.getAllByText("0");
      expect(cards.length).toBeGreaterThanOrEqual(3);
    });
  });

  it("conta corretamente checklists 'em preenchimento' (is_locked=false)", async () => {
    const checklists = [
      makeChecklist({ id: 1, is_locked: false }),
      makeChecklist({ id: 2, is_locked: true }),
      makeChecklist({ id: 3, is_locked: false }),
    ];
    renderDashboard({}, checklists);
    // emPreenchimento=2 (único "2" na tela)
    await waitFor(() => expect(screen.getByText("2")).toBeInTheDocument());
    // total=3 aparece duas vezes (esteMes e total geral) — confirma via label
    const totalCard = (await screen.findByText("Total geral")).closest("div");
    expect(totalCard).toHaveTextContent("3");
  });

  it("exibe total geral correto", async () => {
    const checklists = [makeChecklist({ id: 1 }), makeChecklist({ id: 2 }), makeChecklist({ id: 3 })];
    renderDashboard({}, checklists);
    await waitFor(() => {
      const totalCard = screen.getByText("Total geral").closest("div");
      expect(totalCard).toHaveTextContent("3");
    });
  });
});

describe("Dashboard — ações rápidas (US-003, US-004)", () => {
  it("renderiza link 'Novo Checklist' apontando para /checklists/new", async () => {
    renderDashboard();
    await waitFor(() => {
      const link = screen.getByRole("link", { name: /novo checklist/i });
      expect(link).toHaveAttribute("href", "/checklists/new");
    });
  });

  it("renderiza link 'Buscar por Placa' apontando para /checklists", async () => {
    renderDashboard();
    await waitFor(() => {
      const link = screen.getByRole("link", { name: /buscar por placa/i });
      expect(link).toHaveAttribute("href", "/checklists");
    });
  });
});

describe("Dashboard — checklists recentes (RN-009)", () => {
  it("não exibe seção 'Recentes' quando não há checklists", async () => {
    renderDashboard({}, []);
    await waitFor(() => {
      expect(screen.queryByText(/recentes/i)).not.toBeInTheDocument();
    });
  });

  it("exibe até 3 checklists recentes com placa e status", async () => {
    const checklists = [
      makeChecklist({ id: 1, placa: "AAA0001", status: "entregue", created_at: "2026-04-25T10:00:00Z" }),
      makeChecklist({ id: 2, placa: "BBB0002", status: "devolvido", created_at: "2026-04-26T10:00:00Z" }),
      makeChecklist({ id: 3, placa: "CCC0003", status: "entregue", created_at: "2026-04-27T10:00:00Z" }),
      makeChecklist({ id: 4, placa: "DDD0004", status: "devolvido", created_at: "2026-04-28T10:00:00Z" }),
    ];
    renderDashboard({}, checklists);
    await waitFor(() => {
      expect(screen.getByText(/recentes/i)).toBeInTheDocument();
    });
    // só os 3 mais recentes (IDs 4, 3, 2 pela ordenação decrescente)
    expect(screen.getByText("DDD0004")).toBeInTheDocument();
    expect(screen.getByText("CCC0003")).toBeInTheDocument();
    expect(screen.getByText("BBB0002")).toBeInTheDocument();
    expect(screen.queryByText("AAA0001")).not.toBeInTheDocument();
  });

  it("exibe badge 'Entregue' para status=entregue", async () => {
    renderDashboard({}, [makeChecklist({ status: "entregue" })]);
    await waitFor(() => {
      expect(screen.getByText("Entregue")).toBeInTheDocument();
    });
  });

  it("exibe badge 'Devolvido' para status=devolvido", async () => {
    renderDashboard({}, [makeChecklist({ status: "devolvido" })]);
    await waitFor(() => {
      expect(screen.getByText("Devolvido")).toBeInTheDocument();
    });
  });
});
