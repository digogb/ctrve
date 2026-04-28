import { describe, it, expect, vi } from "vitest";
import { render, screen, renderHook } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext, AuthProvider, useAuthContext } from "../AuthContext";
import type { AuthContextValue } from "../AuthContext";

vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn().mockReturnValue(new Promise(() => {})),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn(() => false),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => vi.fn() };
});

const mockCtx: AuthContextValue = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: vi.fn(),
  logout: vi.fn(),
  loginError: null,
  setLoginError: vi.fn(),
};

describe("useAuthContext — RN-001 (contexto de autenticação)", () => {
  it("lança erro quando chamado fora de AuthProvider", () => {
    const { result } = renderHook(() => {
      try {
        return useAuthContext();
      } catch (e) {
        return e as Error;
      }
    });
    expect(result.current).toBeInstanceOf(Error);
    expect((result.current as Error).message).toMatch(/AuthProvider/i);
  });

  it("retorna o contexto quando chamado dentro de AuthContext.Provider", () => {
    const { result } = renderHook(() => useAuthContext(), {
      wrapper: ({ children }) => (
        <AuthContext.Provider value={mockCtx}>{children}</AuthContext.Provider>
      ),
    });
    expect(result.current).toBe(mockCtx);
    expect(result.current.isAuthenticated).toBe(false);
  });
});

describe("AuthProvider — integração com useAuth", () => {
  it("renderiza children e fornece contexto não-nulo", () => {
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <AuthProvider>
            <span>filho</span>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText("filho")).toBeInTheDocument();
  });
});
