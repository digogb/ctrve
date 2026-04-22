# Deferred Work

## Deferred from: code review of 1-2-cadastro-de-usuario (2026-04-22)

- `RequireRole` pode disparar segundo fetch de `/me` independente do `ProtectedRoute` se os dois não compartilharem o mesmo queryKey React Query — verificar implementação do `ProtectedRoute` para confirmar se usa `queryKey: ["me"]` e staleTime compatível antes de decidir se é necessário extrair o fetch para um contexto compartilhado.
