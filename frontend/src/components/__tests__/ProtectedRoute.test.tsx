import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ProtectedRoute from "../ProtectedRoute";
import { AuthContext } from "../../features/auth/AuthContext";
import type { AuthContextValue } from "../../features/auth/AuthContext";
import type { User } from "../../types/user";

const mockUser: User = {
  id: 1,
  username: "user",
  full_name: "User",
  matricula: "123456",
  role: "responsavel",
  is_active: true,
};

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

function wrap(children: React.ReactNode, ctx: Partial<AuthContextValue> = {}) {
  return render(
    <AuthContext.Provider value={makeCtx(ctx)}>
      <MemoryRouter>{children}</MemoryRouter>
    </AuthContext.Provider>
  );
}

describe("ProtectedRoute", () => {
  it("exibe spinner enquanto carregando", () => {
    wrap(<ProtectedRoute><div>Conteúdo</div></ProtectedRoute>, { isLoading: true });
    expect(screen.getByLabelText(/carregando/i)).toBeInTheDocument();
  });

  it("redireciona para /login quando não autenticado", () => {
    wrap(
      <ProtectedRoute><div>Conteúdo protegido</div></ProtectedRoute>,
      { user: null, isLoading: false }
    );
    expect(screen.queryByText("Conteúdo protegido")).not.toBeInTheDocument();
  });

  it("exibe conteúdo quando autenticado", () => {
    wrap(
      <ProtectedRoute><div>Área restrita</div></ProtectedRoute>,
      { user: mockUser, isAuthenticated: true }
    );
    expect(screen.getByText("Área restrita")).toBeInTheDocument();
  });
});
