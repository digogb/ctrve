import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppRoutes from "./routes";
import { AuthContext } from "./features/auth/AuthContext";
import type { AuthContextValue } from "./features/auth/AuthContext";

function makeCtx(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    loginError: null,
    setLoginError: vi.fn(),
    ...overrides,
  };
}

describe("App", () => {
  it("exibe tela de login quando não autenticado (/login)", () => {
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <AuthContext.Provider value={makeCtx()}>
          <MemoryRouter initialEntries={["/login"]}>
            <AppRoutes />
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>
    );
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });
});
