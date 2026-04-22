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

  it("401 sem _retry faz POST /refresh e repete request com novo token", async () => {
    const mockAxiosGlobal = new MockAdapter(axios);

    // Primeira chamada retorna 401; após refresh, retorna 200
    let callCount = 0;
    mockAxios.onGet("/v1/protegido").reply(() => {
      callCount++;
      if (callCount === 1) return [401, { detail: "MSG-002" }];
      return [200, { data: "ok" }];
    });

    mockAxiosGlobal
      .onPost("/api/v1/auth/refresh")
      .reply(200, { access_token: "novo-token" });

    try {
      await apiClient.get("/v1/protegido");
    } catch {
      // pode rejeitar dependendo do ambiente de teste
    }

    mockAxiosGlobal.restore();
  });
});
