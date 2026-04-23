# Deferred Work

## Deferred from: code review of 1-2-cadastro-de-usuario (2026-04-22)

- `RequireRole` pode disparar segundo fetch de `/me` independente do `ProtectedRoute` se os dois não compartilharem o mesmo queryKey React Query — verificar implementação do `ProtectedRoute` para confirmar se usa `queryKey: ["me"]` e staleTime compatível antes de decidir se é necessário extrair o fetch para um contexto compartilhado.

## Deferred from: code review of 2-1-criar-novo-checklist (2026-04-22)

- `data_entrega` ausente do `ChecklistResponse` — campo é sempre `None` nesta story; adicionar ao schema quando stories futuras passarem a gravá-lo (Epic 4/5).
- Normalização uppercase da placa (`placa_upper`) não enforçada em nível de BD — inserções externas (migrações, admin, fixtures) que gravem em minúsculo bypassam RN-008 silenciosamente; adicionar constraint `CHECK` ou `@field_validator` no model quando houver janela de refactor.
- `ChecklistError` (e `UserError`) não chamam `super().__init__()` — padrão pré-existente introduzido na story 1.2; corrigir em refactor cross-story de exceções antes de integrar middleware de logging.

## Deferred from: code review of 3-1-preencher-checklist-de-entrega (2026-04-23)

- Concurrent PATCH sem controle de concorrência — last-write-wins silencioso; implementar campo `version` ou `updated_at` + HTTP 409 para conflito de versão em Story 5.1 ou story dedicada.
- `update_entrega` não faz transição de `status` nem seta `is_locked`; mecanismo de lock implementado em Story 5.1 (salvar checklist).
- MSG-012 hardcoded como "Informe a data e o horário da entrega." — placeholder `{entrega/devolução}` necessário ao reutilizar o schema na devolução (Story 4.x); parametrizar antes de Story 4.

## Deferred from: code review of 2-2-buscar-checklist-por-placa (2026-04-23)

- Resultado sem paginação/LIMIT no endpoint `GET /checklists` — toda tabela materializada em memória quando sem filtro; implementar cursor/offset quando volume de dados crescer.
- Visibilidade cross-unit — motorista autenticado acessa checklists de todas as unidades sem restrição de escopo; avaliar se controle multi-tenant é necessário como requisito de negócio.
- `placa=""` (string vazia via query param) silenciosamente ignora o filtro e retorna todos os registros — mesma semântica que omitir o parâmetro, mas pode confundir clientes da API; considerar validação explícita (400 ou normalizar para None).
- Teste MSG-009 (`exibe MSG-009 quando busca não retorna resultados`) não verifica explicitamente que o indicador de loading sumiu antes da asserção — padrão herdado dos testes existentes, reavaliar ao padronizar waitFor em toda a suite.

## Deferred from: code review of 3-2-registrar-avarias-no-mapa-do-veiculo (2026-04-23)

- Touch/mobile: SVG click handler da DamageMap usa apenas `MouseEvent` sem `onTouchStart`/`onPointerDown` — cross-cutting UX; avaliar junto com estratégia de responsividade mobile do projeto.
- Acessibilidade: pontos de avaria no SVG sem `tabIndex`, `role="button"`, `aria-label` ou `onKeyDown` — cross-cutting a11y; tratar em story dedicada de acessibilidade.
- `readOnly` DamageMap requer prop `onChange` obrigatória (noop `() => {}`) — code smell; refatorar para discriminated union quando interface evoluir.
- Avarias invisíveis quando `status === "devolvido"` — RN-014 diz mapa não aparece na devolução, mas avarias da entrega ficam invisíveis após devolução; decidir em Story 4.x se devem ser exibidas read-only.
- `avarias: []` vs `avarias: null` — Zod `.default([])` envia array vazio ao re-submeter, sobrescrevendo avarias existentes; resolver em Story 5.1 quando Save for habilitado.

## Deferred from: code review of 1-1-login-no-sistema (2026-04-23)

- `engine` criado em tempo de importação em `database.py` — padrão pré-existente; em testes que sobrescrevem `DATABASE_URL` o override pode chegar tarde; tratar em refactor de infra.
- Refresh token drift em falha de entrega da resposta — se o servidor emite o novo token mas o cliente não recebe (timeout/conexão derrubada), cliente e servidor ficam com tokens diferentes por até 7 dias; limitação inerente de JWT stateless sem blacklist, aceitar ou implementar jti tracking.
- Erros de rede (5xx) não distinguíveis de erros de auth no interceptor de `apiClient.ts` — trade-off aceitável; reavaliar se relatórios de erros de usuário ficarem confusos.
- Flash redirect potencial em React StrictMode/dev — `ProtectedRoute` pode renderizar `<Navigate to="/login">` por sub-ms antes do cache hidratar; quirk de dev, não afeta produção.
- `queryClient` instanciado fora do componente `App` — estado persiste entre renders em testes; extrair para dentro do componente ou limpar no teardown de testes.
- `require_role` igualdade estrita sem suporte a hierarquia de roles — com 2 roles atuais não é problema; refatorar para `role: UserRole | set[UserRole]` quando o modelo de roles crescer.
