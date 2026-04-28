import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import RequireRole from "../RequireRole";
import type { User } from "../../types/user";

vi.mock("../../lib/apiClient", () => ({
  default: { get: vi.fn() },
  isAxiosError: vi.fn((err: unknown) => err instanceof Error && "response" in err),
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

import apiClient from "../../lib/apiClient";

const RESPONSAVEL: User = {
  id: 1,
  username: "resp",
  full_name: "Ana Lima",
  matricula: "111111",
  role: "responsavel",
  is_active: true,
};

const MOTORISTA: User = { ...RESPONSAVEL, id: 2, role: "motorista" };

function renderWith(requiredRole: "responsavel" | "motorista") {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/protegido"]}>
        <Routes>
          <Route
            path="/protegido"
            element={
              <RequireRole role={requiredRole}>
                <div>Conteúdo protegido</div>
              </RequireRole>
            }
          />
          <Route path="/" element={<div>Home pública</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("RequireRole — CT-001 / RN-001 (controle de acesso por perfil)", () => {
  it("exibe 'Carregando...' enquanto a query está pendente", () => {
    vi.mocked(apiClient.get).mockReturnValue(new Promise(() => {})); // never resolves
    renderWith("responsavel");
    const loadingEl = screen.getByText(/carregando/i);
    expect(loadingEl).toBeInTheDocument();
    expect(loadingEl.closest("[aria-busy]")).toHaveAttribute("aria-busy", "true");
  });

  it("renderiza children quando usuário tem o perfil exigido (responsavel)", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: RESPONSAVEL });
    renderWith("responsavel");
    await waitFor(() => {
      expect(screen.getByText("Conteúdo protegido")).toBeInTheDocument();
    });
  });

  it("renderiza children quando usuário tem o perfil exigido (motorista)", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: MOTORISTA });
    renderWith("motorista");
    await waitFor(() => {
      expect(screen.getByText("Conteúdo protegido")).toBeInTheDocument();
    });
  });

  it("redireciona para '/' quando usuário tem perfil diferente do exigido", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: MOTORISTA });
    renderWith("responsavel"); // motorista tenta acessar rota de responsavel
    await waitFor(() => {
      expect(screen.getByText("Home pública")).toBeInTheDocument();
    });
    expect(screen.queryByText("Conteúdo protegido")).not.toBeInTheDocument();
  });

  it("redireciona para '/' quando fetchMe retorna null (401)", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: null });
    renderWith("responsavel");
    await waitFor(() => {
      expect(screen.getByText("Home pública")).toBeInTheDocument();
    });
  });
});
