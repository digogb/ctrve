import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import ChecklistForm from "../ChecklistForm";

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
        <ChecklistForm />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

async function fillValidForm() {
  await userEvent.type(screen.getByLabelText(/^placa$/i), "ABC1D23");
  await userEvent.type(screen.getByLabelText(/^unidade$/i), "SECLOG");
  await userEvent.type(screen.getByLabelText(/^motorista$/i), "João Silva");
  await userEvent.type(screen.getByLabelText(/^matrícula$/i), "123456");
  await userEvent.type(screen.getByLabelText(/quilometragem/i), "50000");
}

beforeEach(() => vi.clearAllMocks());

describe("ChecklistForm — Informações Gerais", () => {
  it("renderiza os campos obrigatórios", () => {
    renderForm();
    expect(screen.getByLabelText(/^placa$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^unidade$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^motorista$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^matrícula$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quilometragem/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/subunidade/i)).toBeInTheDocument();
  });

  it("placa inválida é bloqueada pelo Zod com MSG-006", async () => {
    renderForm();
    await userEvent.type(screen.getByLabelText(/^placa$/i), "12345");
    await userEvent.type(screen.getByLabelText(/^unidade$/i), "SECLOG");
    await userEvent.type(screen.getByLabelText(/^motorista$/i), "Motorista");
    await userEvent.type(screen.getByLabelText(/^matrícula$/i), "111111");
    await userEvent.type(screen.getByLabelText(/quilometragem/i), "50000");
    await userEvent.click(screen.getByRole("button", { name: /criar/i }));

    await waitFor(() => {
      expect(screen.getByText(/formato de placa inválido/i)).toBeInTheDocument();
    });
    expect(apiClient.post).not.toHaveBeenCalled();
  });

  it("matrícula não numérica é bloqueada pelo Zod com MSG-007", async () => {
    renderForm();
    await userEvent.type(screen.getByLabelText(/^placa$/i), "ABC1D23");
    await userEvent.type(screen.getByLabelText(/^unidade$/i), "SECLOG");
    await userEvent.type(screen.getByLabelText(/^motorista$/i), "Motorista");
    await userEvent.type(screen.getByLabelText(/^matrícula$/i), "ABC123");
    await userEvent.type(screen.getByLabelText(/quilometragem/i), "50000");
    await userEvent.click(screen.getByRole("button", { name: /criar/i }));

    await waitFor(() => {
      expect(screen.getByText(/apenas valores numéricos/i)).toBeInTheDocument();
    });
    expect(apiClient.post).not.toHaveBeenCalled();
  });

  it("submit bem-sucedido redireciona para /checklists/{id}", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { id: 42, placa: "ABC1D23", status: "entregue" },
    });
    renderForm();
    await fillValidForm();
    await userEvent.click(screen.getByRole("button", { name: /criar/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/checklists/42");
    });
  });

  it("exibe botão Cancelar no formulário de criação", () => {
    renderForm();
    expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
  });

  it("clique em Cancelar navega para / sem window.confirm (AC-8)", async () => {
    const confirmSpy = vi.spyOn(window, "confirm");
    renderForm();
    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/");
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it("erro MSG-008 exibe alerta de entrega duplicada", async () => {
    const err = Object.assign(new axios.AxiosError(), {
      response: {
        status: 400,
        data: {
          detail: "MSG-008",
          message: "Já existe um checklist de entrega aberto para o veículo de placa ABC1D23.",
          fields: ["placa"],
        },
      },
    });
    vi.mocked(apiClient.post).mockRejectedValueOnce(err);
    renderForm();
    await fillValidForm();
    await userEvent.click(screen.getByRole("button", { name: /criar/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/checklist de entrega aberto/i);
    });
  });
});
