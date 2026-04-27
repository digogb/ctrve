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

## Deferred from: code review of 3-3-coletar-assinaturas-na-entrega (2026-04-23)

- Migração de banco para colunas `assinatura_responsavel` e `assinatura_motorista` — em dev, deletar `ctrve.db`; gerar Alembic migration antes de deploy.
- Validação base64 verifica apenas prefixo `data:image/png;base64,`, não valida conteúdo real — defense-in-depth; implementar `base64.b64decode(payload, validate=True)` em refactor de segurança.
- `fetchMe` em `useAuth.ts` retorna `null` para 401 — mudança de tipo pode causar inconsistência `null` vs `undefined` em consumers; auditar quando refatorar auth.
- `queryClient.cancelQueries` não awaited em `logout()` — race condition teórica onde resposta stale pode sobrescrever `null`; resolver em refactor de auth.
- `session-expired` condicionado a `hadSession` — comportamento once-only via variável module-level; documentar intenção.
- Componentes shadcn `select.tsx`, `radio-group.tsx` instalados mas não importados — manter para stories futuras (RegisterForm, etc.).
- `react-signature-canvas@1.1.0-alpha.2` em versão alpha — fixar versão exata ou avaliar estável `1.0.6` quando necessário.
- `legacy-peer-deps=true` no `.npmrc` — workaround para React 19 peer deps; resolver quando ecossistema atualizar.
- ReadOnly mostra seção "Assinaturas" sem feedback quando apenas uma assinatura existe — adicionar placeholder "Não assinado" em melhoria UX futura.
- Canvas `react-signature-canvas` com resolução fixa 300x150 pixels — distorção em containers maiores; implementar ResizeObserver ou dimensões explícitas em story de responsividade mobile.

## Deferred from: code review of 4-1-preencher-checklist-de-devolucao (2026-04-23)

- Frontend string date comparison no submit handler de devolução — compara ISO strings em vez de `new Date()` objects; código morto enquanto botão Salvar estiver disabled; corrigir em Story 5.1.
- Sem success handler / query refresh no submit de devolução — `.catch()` existe mas não há `.then()` para invalidar query cache ou dar feedback; código morto enquanto botão Salvar estiver disabled; implementar em Story 5.1.
- Sem verificação de ownership (IDOR) no endpoint PATCH devolucao — qualquer `responsavel` pode alterar qualquer checklist; pre-existing desde Epic 2; avaliar como requisito de segurança quando multi-tenant for necessário.
- Sem idempotência / proteção contra double-submit e race condition — last-write-wins silencioso no PATCH devolucao; pre-existing (já listado em review de 3-1); implementar versioning/409 em story dedicada.
- Erros do backend (422/400) não exibidos no frontend DevolucaoForm — apenas erro genérico no catch; código morto; implementar em Story 5.1.
- Sem testes de validação do formulário frontend de devolução — form não é submittable (botão disabled); adicionar quando Story 5.1 habilitar o Save.

## Deferred from: code review of 4-2-coletar-assinaturas-na-devolucao (2026-04-24)

- Impossível limpar assinatura já salva — `checklist_service.py:124-127` usa `if data.assinatura_responsavel is not None` para decidir se persiste; `None` (campo não enviado) e `null` (limpar) são indistinguíveis; implementar distinção via `model_fields_set` ou sentinel quando necessário.
- Zod schema não valida formato base64 das assinaturas — `checklistSchema.ts:74-75` aceita qualquer string; backend valida no Pydantic; adicionar `.regex()` ou `.refine()` no frontend para mensagens de erro amigáveis.
- Backend aceita devolução sem `data_entrega` preenchida — `checklist_service.py:110` pula validação de data se `data_entrega` é None; depende do fluxo de lock garantir que data_entrega está preenchida; considerar constraint no banco.

## Deferred from: code review of 4-3-registrar-observacoes (2026-04-24)

- Sem limite de tamanho no campo `observacoes` — spec RN-020 diz "sem max_length" mas payload arbitrariamente grande pode causar DoS; considerar limit server-side de defesa (ex: 10KB) que não afeta uso normal.
- String vazia `""` vs `null` em `observacoes` — banco persiste `""`, frontend read-only oculta como falsy; considerar normalizar `""` para `null` no backend ou Zod transform.
- `ObservationsField` usa textarea com estilo manual (`bg-white`, sem `focus-visible:ring`) em vez de componente shadcn `Textarea` — inconsistência visual com outros campos; tratar em story de UI polish.

## Deferred from: code review of 5-1-salvar-checklist (2026-04-26)

- `update_devolucao` não seta `is_locked = True` após salvar devolução — protegido pelos guards existentes (`is_locked=True` na entrada + status transita para `devolvido`), mas há assimetria arquitetural com `update_entrega`; tornar explícito em refactor cross-service.
- `queryClient.invalidateQueries` key inconsistência — entrega usa `id ?? ""` (string do param), devolução usa `String(checklist.id)` (number coerced); normalizar para um único padrão ao refatorar o componente.
- Assinatura vazia `""` retorna mensagem de erro genérica no backend ("deve ser imagem PNG") em vez de "é obrigatória" — `validate_base64_signature` captura antes de `validate_signatures`; adicionar `or not v` na guard do model_validator ou validar tamanho mínimo.
- Sem teste frontend para exibição de erros do backend (400/422) — `submitError` display não coberto; adicionar após corrigir campo `.detail` vs `.message`.

## Deferred from: code review of 5-2-gerar-e-compartilhar-pdf (2026-04-27)

- Jinja2 3.1.2 CVE-2024-34064 (filtro `xmlattr`, não utilizado no template desta story) — atualizar para 3.1.4+ em janela de dependency maintenance cross-story.
- WeasyPrint deps de sistema (libcairo, libpango, libgdk-pixbuf, libffi) não documentadas em Dockerfile ou script de setup — documentar antes de deploy em ambiente limpo.
- `window.alert` para MSG-025 (sucesso) e mensagens de erro — padrão pré-existente estabelecido pela spec de story 5.1; substituir por componente de toast/notificação em story de UI polish.
- `generate_checklist_pdf` executa `HTML(...).write_pdf()` de forma síncrona bloqueando thread do FastAPI — WeasyPrint é CPU/I/O intensivo; usar `run_in_executor` em story de performance quando concorrência for necessária. [backend/app/services/pdf_service.py]
- Endpoint `GET /checklists/{id}/pdf` sem `response_model`/`responses` no decorador `@router.get` — OpenAPI infere resposta como JSON em vez de `application/pdf`; adicionar `responses={200: {"content": {"application/pdf": {}}}}` em refactor de schema. [backend/app/api/routes/pdf.py]
- `data_entrega.strftime` e `data_devolucao.strftime` no template renderizam UTC sem indicação de fuso — usuário BR vê horário -3h do real; parametrizar timezone (America/Sao_Paulo) quando localização for necessária. [backend/app/templates/pdf/checklist.html]
- Padrão `item is mapping` espalhado em 4+ blocos do template — normalizar `itens`, `itens_devolucao` e `avarias` para listas de dicts simples em `pdf_service.py` antes de passar ao Jinja2, eliminando a ambiguidade. [backend/app/services/pdf_service.py]
