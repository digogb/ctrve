import { describe, it, expect, vi, beforeEach } from "vitest";
import MockAdapter from "axios-mock-adapter";
import axios from "axios";

// Importa o módulo real (não mockado) para testar os interceptors
import apiClient, {
  setAccessToken,
  clearAccessToken,
  getAccessToken,
} from "../apiClient";

const mockAxios = new MockAdapter(apiClient);

beforeEach(() => {
  clearAccessToken();
  mockAxios.reset();
  vi.restoreAllMocks();
});

describe("token management (RN-001 — segurança)", () => {
  it("getAccessToken retorna null por padrão", () => {
    expect(getAccessToken()).toBeNull();
  });

  it("setAccessToken armazena token em memória", () => {
    setAccessToken("meu-token");
    expect(getAccessToken()).toBe("meu-token");
  });

  it("clearAccessToken limpa o token", () => {
    setAccessToken("meu-token");
    clearAccessToken();
    expect(getAccessToken()).toBeNull();
  });

  it("token nunca vai para localStorage (RN-001 — sem token em storage)", () => {
    setAccessToken("secreto");
    expect(localStorage.getItem("token")).toBeNull();
    expect(sessionStorage.getItem("token")).toBeNull();
  });
});

describe("request interceptor — Authorization header", () => {
  it("adiciona header Authorization quando token presente", async () => {
    setAccessToken("access-token-123");
    mockAxios.onGet("/v1/test").reply(200, { ok: true });

    const response = await apiClient.get("/v1/test");
    expect(response.config.headers?.Authorization).toBe(
      "Bearer access-token-123"
    );
  });

  it("não adiciona Authorization quando sem token", async () => {
    mockAxios.onGet("/v1/test").reply(200, { ok: true });

    const response = await apiClient.get("/v1/test");
    expect(response.config.headers?.Authorization).toBeUndefined();
  });
});

describe("response interceptor — refresh em 401 (RN-002)", () => {
  it("request normal (não 401) retorna resposta sem chamar refresh", async () => {
    mockAxios.onGet("/v1/ok").reply(200, { data: "ok" });

    const response = await apiClient.get("/v1/ok");
    expect(response.status).toBe(200);
    expect(response.data).toEqual({ data: "ok" });
  });

  it("401 com _retry=true não tenta refresh (evita loop)", async () => {
    // Simula request que já passou por retry — deve rejeitar direto
    mockAxios.onGet("/v1/loop").reply((config) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (config as any)._retry = true;
      return [401, { detail: "MSG-002" }];
    });
    await expect(apiClient.get("/v1/loop")).rejects.toMatchObject({
      response: { status: 401 },
    });
  });

  it("401 sem _retry tenta refresh e repete request com novo token", async () => {
    const mockAxiosGlobal = new MockAdapter(axios);
    let callCount = 0;
    mockAxios.onGet("/v1/protegido").reply(() => {
      callCount++;
      if (callCount === 1) return [401, { detail: "MSG-002" }];
      return [200, { data: "secreto" }];
    });
    mockAxiosGlobal
      .onPost("/api/v1/auth/refresh")
      .reply(200, { access_token: "novo-token" });

    const response = await apiClient.get("/v1/protegido");
    expect(response.data).toEqual({ data: "secreto" });
    expect(getAccessToken()).toBe("novo-token");
    mockAxiosGlobal.restore();
  });

  it("refresh falha sem sessão prévia — não dispara session-expired", async () => {
    const mockAxiosGlobal = new MockAdapter(axios);
    const eventSpy = vi.fn();
    window.addEventListener("session-expired", eventSpy);

    mockAxios.onGet("/v1/protegido").reply(401, { detail: "MSG-002" });
    mockAxiosGlobal.onPost("/api/v1/auth/refresh").reply(401, {});

    await expect(apiClient.get("/v1/protegido")).rejects.toBeDefined();
    expect(eventSpy).not.toHaveBeenCalled();

    window.removeEventListener("session-expired", eventSpy);
    mockAxiosGlobal.restore();
  });

  it("refresh falha com sessão ativa — dispara evento session-expired (RN-002)", async () => {
    setAccessToken("token-ativo");
    const mockAxiosGlobal = new MockAdapter(axios);
    const eventSpy = vi.fn();
    window.addEventListener("session-expired", eventSpy);

    mockAxios.onGet("/v1/protegido").reply(401, { detail: "MSG-002" });
    mockAxiosGlobal.onPost("/api/v1/auth/refresh").reply(401, {});

    await expect(apiClient.get("/v1/protegido")).rejects.toBeDefined();
    expect(eventSpy).toHaveBeenCalledTimes(1);
    expect(getAccessToken()).toBeNull();

    window.removeEventListener("session-expired", eventSpy);
    mockAxiosGlobal.restore();
  });
});
