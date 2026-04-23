import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import LoginForm from "../LoginForm";
import { AuthContext } from "../AuthContext";
import type { AuthContextValue } from "../AuthContext";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function makeCtx(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn().mockResolvedValue(true),
    logout: vi.fn(),
    loginError: null,
    setLoginError: vi.fn(),
    ...overrides,
  };
}

function renderLoginForm(
  ctx: Partial<AuthContextValue> = {},
  initialPath: { pathname: string; state?: unknown } = { pathname: "/login" }
) {
  return render(
    <AuthContext.Provider value={makeCtx(ctx)}>
      <MemoryRouter initialEntries={[initialPath]}>
        <LoginForm />
      </MemoryRouter>
    </AuthContext.Provider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.useRealTimers();
});

describe("LoginForm", () => {
  it("renderiza campos de usuário e senha", () => {
    renderLoginForm();
    expect(screen.getByLabelText(/usuário/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("login bem-sucedido exibe MSG-024 e redireciona para /", async () => {
    const loginMock = vi.fn().mockResolvedValue(true);
    renderLoginForm({ login: loginMock });

    await userEvent.type(screen.getByLabelText(/usuário/i), "testuser");
    await userEvent.type(screen.getByLabelText(/senha/i), "Senha123");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent(/login realizado com sucesso/i)
    );
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/"), { timeout: 2000 });
  }, 3000);

  it("exibe loginError do contexto como MSG-001", () => {
    renderLoginForm({
      loginError:
        "Usuário ou senha inválidos. Verifique suas credenciais e tente novamente.",
    });
    expect(screen.getByRole("alert")).toHaveTextContent(/usuário ou senha inválidos/i);
  });

  it("exibe mensagem de sessão expirada da location.state (MSG-002)", () => {
    const MSG =
      "Sua sessão expirou por inatividade. Realize o login novamente para continuar.";
    renderLoginForm({}, { pathname: "/login", state: { msg: MSG } });
    expect(screen.getByRole("alert")).toHaveTextContent(/sessão expirou/i);
  });

  it("botão fica desabilitado durante o submit", async () => {
    let resolveLogin!: (v: boolean) => void;
    const loginMock = vi.fn().mockReturnValue(
      new Promise<boolean>((r) => { resolveLogin = r; })
    );

    renderLoginForm({ login: loginMock });
    await userEvent.type(screen.getByLabelText(/usuário/i), "u");
    await userEvent.type(screen.getByLabelText(/senha/i), "p");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    expect(screen.getByRole("button", { name: /entrando/i })).toBeDisabled();
    resolveLogin(false);
  });
});
