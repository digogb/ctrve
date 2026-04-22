import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import RegisterForm from "../RegisterForm";

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

import apiClient from "../../../lib/apiClient";

function renderForm() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

async function fillForm(overrides: Record<string, string> = {}) {
  const defaults = {
    full_name: "João Silva",
    matricula: "123456",
    username: "joao",
    password: "Senha123",
    confirmPassword: "Senha123",
  };
  const values = { ...defaults, ...overrides };

  await userEvent.clear(screen.getByLabelText(/nome completo/i));
  await userEvent.type(screen.getByLabelText(/nome completo/i), values.full_name);

  await userEvent.clear(screen.getByLabelText(/^matrícula/i));
  await userEvent.type(screen.getByLabelText(/^matrícula/i), values.matricula);

  await userEvent.clear(screen.getByLabelText(/^usuário/i));
  await userEvent.type(screen.getByLabelText(/^usuário/i), values.username);

  await userEvent.selectOptions(screen.getByLabelText(/perfil/i), "motorista");

  await userEvent.clear(screen.getByLabelText(/^senha$/i));
  await userEvent.type(screen.getByLabelText(/^senha$/i), values.password);

  await userEvent.clear(screen.getByLabelText(/confirmar senha/i));
  await userEvent.type(screen.getByLabelText(/confirmar senha/i), values.confirmPassword);
}

beforeEach(() => vi.clearAllMocks());

describe("RegisterForm", () => {
  it("renderiza todos os campos obrigatórios", () => {
    renderForm();
    expect(screen.getByLabelText(/nome completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^matrícula/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^usuário/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/perfil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^senha$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirmar senha/i)).toBeInTheDocument();
  });

  it("cadastro bem-sucedido exibe MSG-023", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { id: 1 } });
    renderForm();
    await fillForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        /usuário cadastrado com sucesso/i
      );
    });
  });

  it("matrícula duplicada exibe MSG-003 no campo matrícula", async () => {
    const err = Object.assign(new axios.AxiosError(), {
      response: {
        status: 400,
        data: { detail: "MSG-003", message: "Matrícula duplicada", fields: ["matricula"] },
      },
    });
    vi.mocked(apiClient.post).mockRejectedValueOnce(err);
    renderForm();
    await fillForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => {
      expect(screen.getByText(/matrícula informada já está cadastrada/i)).toBeInTheDocument();
    });
  });

  it("senha sem maiúscula — Zod bloqueia antes de submeter (RN-004)", async () => {
    renderForm();
    await fillForm({ password: "senha123", confirmPassword: "senha123" });
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => {
      expect(screen.getByText(/letra maiúscula/i)).toBeInTheDocument();
    });
    expect(apiClient.post).not.toHaveBeenCalled();
  });

  it("confirmação de senha diferente — Zod bloqueia", async () => {
    renderForm();
    await fillForm({ confirmPassword: "OutraSenha123" });
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => {
      expect(screen.getByText(/senhas não coincidem/i)).toBeInTheDocument();
    });
    expect(apiClient.post).not.toHaveBeenCalled();
  });
});
