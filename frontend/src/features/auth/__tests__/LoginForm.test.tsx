import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import LoginForm from "../LoginForm";

function makeAxiosError(status: number) {
  return Object.assign(new axios.AxiosError("Request failed"), {
    response: { status, data: { detail: `MSG-00${status === 401 ? 1 : 0}` } },
  });
}

vi.mock("../../../lib/apiClient", () => ({
  default: {
    post: vi.fn(),
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

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

import apiClient, { setAccessToken } from "../../../lib/apiClient";

function renderLoginForm() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <LoginForm />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("LoginForm", () => {
  it("renderiza campos de usuário e senha", () => {
    renderLoginForm();
    expect(screen.getByLabelText(/usuário/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("login bem-sucedido redireciona para /", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { access_token: "fake-token" },
    });

    renderLoginForm();
    await userEvent.type(screen.getByLabelText(/usuário/i), "testuser");
    await userEvent.type(screen.getByLabelText(/senha/i), "Senha123");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() => {
      expect(setAccessToken).toHaveBeenCalledWith("fake-token");
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });

  it("credenciais inválidas exibe MSG-001 sem indicar campo específico", async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce(makeAxiosError(401));

    renderLoginForm();
    await userEvent.type(screen.getByLabelText(/usuário/i), "errado");
    await userEvent.type(screen.getByLabelText(/senha/i), "errada");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toHaveTextContent(/usuário ou senha inválidos/i);
      expect(alert).not.toHaveTextContent(/usuário/i.source.includes("campo"));
    });
  });

  it("erro de rede exibe mensagem de servidor indisponível", async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce(new Error("Network Error"));

    renderLoginForm();
    await userEvent.type(screen.getByLabelText(/usuário/i), "u");
    await userEvent.type(screen.getByLabelText(/senha/i), "p");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/erro de comunicação/i);
    });
  });

  it("botão fica desabilitado durante o submit", async () => {
    let resolve: (v: unknown) => void;
    vi.mocked(apiClient.post).mockReturnValueOnce(
      new Promise((r) => { resolve = r; })
    );

    renderLoginForm();
    await userEvent.type(screen.getByLabelText(/usuário/i), "u");
    await userEvent.type(screen.getByLabelText(/senha/i), "p");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    expect(screen.getByRole("button", { name: /entrando/i })).toBeDisabled();
    resolve!({ data: { access_token: "t" } });
  });
});
