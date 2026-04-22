# Deferred Work

## Deferred from: code review of 1-2-cadastro-de-usuario (2026-04-22)

- `RequireRole` pode disparar segundo fetch de `/me` independente do `ProtectedRoute` se os dois não compartilharem o mesmo queryKey React Query — verificar implementação do `ProtectedRoute` para confirmar se usa `queryKey: ["me"]` e staleTime compatível antes de decidir se é necessário extrair o fetch para um contexto compartilhado.

## Deferred from: code review of 2-1-criar-novo-checklist (2026-04-22)

- `data_entrega` ausente do `ChecklistResponse` — campo é sempre `None` nesta story; adicionar ao schema quando stories futuras passarem a gravá-lo (Epic 4/5).
- Normalização uppercase da placa (`placa_upper`) não enforçada em nível de BD — inserções externas (migrações, admin, fixtures) que gravem em minúsculo bypassam RN-008 silenciosamente; adicionar constraint `CHECK` ou `@field_validator` no model quando houver janela de refactor.
- `ChecklistError` (e `UserError`) não chamam `super().__init__()` — padrão pré-existente introduzido na story 1.2; corrigir em refactor cross-story de exceções antes de integrar middleware de logging.
