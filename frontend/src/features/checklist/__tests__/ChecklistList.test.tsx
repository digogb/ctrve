import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChecklistList from "../ChecklistList";
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

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

import apiClient from "../../../lib/apiClient";

const MOCK_CHECKLIST: ChecklistResponse = {
  id: 1,
  placa: "ABC1D23",
  unidade: "SECLOG",
  subunidade: null,
  motorista: "João Silva",
  matricula_motorista: "123456",
  quilometragem_inicial: 10000,
  status: "entregue",
  is_locked: false,
  created_at: "2026-04-23T10:00:00Z",
};

function renderComponent() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ChecklistList />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ChecklistList", () => {
  it("renderiza formulário de busca com input e botão", () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [] });
    renderComponent();
    expect(screen.getByLabelText(/placa/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /buscar/i })).toBeInTheDocument();
  });

  it("exibe resultados com Nº de Controle, Placa, Data e Status", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [MOCK_CHECKLIST] });

    renderComponent();
    await userEvent.type(screen.getByLabelText(/placa/i), "ABC1D23");
    await userEvent.click(screen.getByRole("button", { name: /buscar/i }));

    await waitFor(() => {
      expect(screen.getByText("1")).toBeInTheDocument();
      expect(screen.getByText("ABC1D23")).toBeInTheDocument();
      expect(screen.getByText("Entregue")).toBeInTheDocument();
      expect(screen.getByText(/\d{2}\/\d{2}\/\d{4}/)).toBeInTheDocument();
    });
  });

  it("exibe MSG-009 quando busca não retorna resultados", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

    renderComponent();
    await userEvent.type(screen.getByLabelText(/placa/i), "ZZZ999");
    await userEvent.click(screen.getByRole("button", { name: /buscar/i }));

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        /nenhum checklist encontrado/i
      );
    });
  });

  it("não exibe MSG-009 sem busca prévia", () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [] });
    renderComponent();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("navega para /checklists/:id ao clicar em uma linha", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [MOCK_CHECKLIST] });

    renderComponent();
    await userEvent.type(screen.getByLabelText(/placa/i), "ABC1D23");
    await userEvent.click(screen.getByRole("button", { name: /buscar/i }));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /checklist 1/i })).toBeInTheDocument()
    );

    await userEvent.click(screen.getByRole("button", { name: /checklist 1/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/checklists/1");
  });

  it("exibe 'Buscando...' durante carregamento", async () => {
    let resolve: (val: { data: ChecklistResponse[] }) => void;
    const pending = new Promise<{ data: ChecklistResponse[] }>((res) => {
      resolve = res;
    });
    vi.mocked(apiClient.get).mockReturnValue(pending as never);

    renderComponent();

    expect(screen.getByText(/buscando/i)).toBeInTheDocument();
    resolve!({ data: [] });
    await waitFor(() =>
      expect(screen.queryByText(/buscando/i)).not.toBeInTheDocument()
    );
  });

  it("exibe 'Devolvido' para status devolvido", async () => {
    const devolvido: ChecklistResponse = { ...MOCK_CHECKLIST, status: "devolvido" };
    vi.mocked(apiClient.get).mockResolvedValue({ data: [devolvido] });

    renderComponent();
    await userEvent.type(screen.getByLabelText(/placa/i), "ABC1D23");
    await userEvent.click(screen.getByRole("button", { name: /buscar/i }));

    await waitFor(() => {
      expect(screen.getByText("Devolvido")).toBeInTheDocument();
    });
  });
});
