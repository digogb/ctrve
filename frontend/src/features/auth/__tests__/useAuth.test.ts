import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import type { ReactNode } from "react";
import React from "react";
import { useAuth } from "../useAuth";
import type { User } from "../../../types/user";

vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn((err: unknown) => !!err && typeof err === "object" && "response" in err),
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

import apiClient, { setAccessToken, clearAccessToken } from "../../../lib/apiClient";

const USER: User = {
  id: 1,
  username: "resp",
  full_name: "Ana Lima",
  matricula: "111111",
  role: "responsavel",
  is_active: true,
};

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: 0 } } });
  return function Wrapper({ children }: { children: ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: qc },
      React.createElement(MemoryRouter, null, children)
    );
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(apiClient.get).mockResolvedValue({ data: null });
});

afterEach(() => {
  vi.useRealTimers();
});

describe("useAuth — fetchMe (RN-001, RN-002)", () => {
  it("retorna user=null e isLoading=true no estado inicial", () => {
    vi.mocked(apiClient.get).mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    expect(result.current.isLoading).toBe(true);
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("popula user após fetchMe bem-sucedido", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: USER });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.user).toEqual(USER);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it("retorna user=null quando fetchMe recebe 401", async () => {
    const err = Object.assign(new Error("Unauthorized"), {
      response: { status: 401 },
    });
    vi.mocked(apiClient.get).mockRejectedValueOnce(err);
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.user).toBeNull();
  });
});

describe("useAuth — login (RN-001)", () => {
  it("retorna true e chama setAccessToken quando login bem-sucedido", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { access_token: "tok-abc" } });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.login("user", "pass");
    });
    expect(success!).toBe(true);
    expect(setAccessToken).toHaveBeenCalledWith("tok-abc");
    expect(result.current.loginError).toBeNull();
  });

  it("retorna false e define MSG-001 quando credenciais inválidas (401)", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const err = Object.assign(new Error("Unauthorized"), {
      response: { status: 401 },
    });
    vi.mocked(apiClient.post).mockRejectedValueOnce(err);
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.login("user", "errada");
    });
    expect(success!).toBe(false);
    expect(result.current.loginError).toMatch(/usuário ou senha inválidos/i);
  });

  it("retorna false e define erro genérico quando servidor indisponível", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const err = Object.assign(new Error("Network"), {
      response: { status: 503 },
    });
    vi.mocked(apiClient.post).mockRejectedValueOnce(err);
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.login("user", "pass");
    });
    expect(success!).toBe(false);
    expect(result.current.loginError).toMatch(/erro de comunicação/i);
  });
});

describe("useAuth — logout (RN-002)", () => {
  it("chama clearAccessToken e navega para /login", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => result.current.logout());
    expect(clearAccessToken).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/login", undefined);
  });

  it("navega com state.msg quando logout é chamado com mensagem (MSG-002)", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => result.current.logout("Sua sessão expirou por inatividade."));
    expect(mockNavigate).toHaveBeenCalledWith("/login", {
      state: { msg: "Sua sessão expirou por inatividade." },
    });
  });
});

describe("useAuth — inatividade (RN-002)", () => {
  it("registra event listeners de atividade quando usuário está autenticado", async () => {
    const addEventSpy = vi.spyOn(window, "addEventListener");
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: USER });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.user).toEqual(USER));

    const activityEvents = ["mousemove", "keydown", "click", "scroll", "touchstart"];
    activityEvents.forEach((event) => {
      expect(addEventSpy).toHaveBeenCalledWith(event, expect.any(Function), { passive: true });
    });
    addEventSpy.mockRestore();
  });

  it("remove event listeners ao desmontar quando usuário está autenticado", async () => {
    const removeEventSpy = vi.spyOn(window, "removeEventListener");
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: USER });
    const { result, unmount } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.user).toEqual(USER));

    unmount();

    const activityEvents = ["mousemove", "keydown", "click", "scroll", "touchstart"];
    activityEvents.forEach((event) => {
      expect(removeEventSpy).toHaveBeenCalledWith(event, expect.any(Function));
    });
    removeEventSpy.mockRestore();
  });

  it("não registra event listeners quando user é null", async () => {
    const addEventSpy = vi.spyOn(window, "addEventListener");
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    const activityEvents = ["mousemove", "keydown", "click", "scroll", "touchstart"];
    activityEvents.forEach((event) => {
      expect(addEventSpy).not.toHaveBeenCalledWith(event, expect.any(Function), { passive: true });
    });
    addEventSpy.mockRestore();
  });
});

describe("useAuth — setLoginError (RN-001)", () => {
  it("setLoginError atualiza o estado de loginError", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: null });
    const { result } = renderHook(() => useAuth(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => result.current.setLoginError("erro manual"));
    expect(result.current.loginError).toBe("erro manual");

    act(() => result.current.setLoginError(null));
    expect(result.current.loginError).toBeNull();
  });
});
