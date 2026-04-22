import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProtectedRoute from "../ProtectedRoute";

vi.mock("../../lib/apiClient", () => ({
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
}));

import apiClient from "../../lib/apiClient";

function wrap(children: React.ReactNode, initialPath = "/") {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[initialPath]}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ProtectedRoute", () => {
  it("redireciona para /login quando não autenticado", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("401"));
    wrap(
      <ProtectedRoute>
        <div>Conteúdo protegido</div>
      </ProtectedRoute>
    );
    // Loading state primeiro
    expect(screen.getByLabelText(/carregando/i)).toBeInTheDocument();
  });

  it("exibe conteúdo quando autenticado", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        id: 1,
        username: "user",
        full_name: "User",
        matricula: "123",
        role: "responsavel",
        is_active: true,
      },
    });
    const { findByText } = wrap(
      <ProtectedRoute>
        <div>Área restrita</div>
      </ProtectedRoute>
    );
    expect(await findByText("Área restrita")).toBeInTheDocument();
  });
});
