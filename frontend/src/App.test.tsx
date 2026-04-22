import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppRoutes from "./routes";

vi.mock("./lib/apiClient", () => ({
  default: {
    post: vi.fn(),
    get: vi.fn().mockRejectedValue(new Error("401")),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
}));

describe("App", () => {
  it("exibe tela de login quando não autenticado (/login)", () => {
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/login"]}>
          <AppRoutes />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });
});
