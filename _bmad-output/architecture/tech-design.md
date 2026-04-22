---
stepsCompleted: ['step-01-init', 'step-02-context', 'step-03-starter', 'step-04-decisions', 'step-05-patterns', 'step-06-structure', 'step-07-validation', 'step-08-complete']
status: 'complete'
completedAt: '2026-04-22'
inputDocuments:
  - '_bmad-output/requirements/product-vision.md'
  - '_bmad-output/requirements/user-stories.md'
  - '_bmad-output/requirements/business-rules.md'
  - '_bmad-output/requirements/messages.md'
  - '_bmad-output/requirements/traceability-matrix.md'
workflowType: 'architecture'
project_name: 'ctrve'
user_name: 'Rodgb'
date: '2026-04-22'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Análise de Contexto do Projeto

### Visão Geral dos Requisitos

**Requisitos Funcionais:**
- 14 estórias de usuário em 6 áreas: autenticação/cadastro, informações gerais, checklist de entrega (com mapa de avarias), checklist de devolução, observações, ações (salvar/PDF/cancelar/navegar)
- O fluxo principal é linear: criar checklist → preencher entrega → coletar assinaturas → salvar → (posteriormente) preencher devolução → coletar assinaturas → salvar → gerar PDF
- Componente de maior complexidade técnica: mapa de avarias interativo com 4 vistas do veículo e marcação de pontos tipificados

**Requisitos Não-Funcionais:**
- Responsividade: sistema usado em desktop e dispositivos móveis no pátio de veículos
- Imutabilidade: checklist salvo não pode ser editado; assinaturas bloqueadas (integridade de registro oficial)
- Geração de PDF: deve conter todos os dados incluindo mapa de avarias e assinaturas renderizadas
- Sessão com expiração por inatividade (30 min padrão)
- Validação completa client-side antes de submit (25 regras)

**Escala e Complexidade:**

- Domínio primário: Full-stack web (React SPA + FastAPI REST + PostgreSQL)
- Nível de complexidade: Médio
- Componentes arquiteturais estimados: ~8 (auth, checklist CRUD, validações, mapa avarias, assinatura canvas, geração PDF, busca, gestão de usuários)

### Restrições Técnicas e Dependências

- Stack obrigatória: React + FastAPI + PostgreSQL
- Autenticação própria (JWT provável) — sem integração LDAP/AD
- Canvas HTML5 para assinaturas (armazenamento como imagem base64 ou blob)
- SVG interativo para mapa de avarias (4 vistas do veículo)
- Biblioteca de geração de PDF server-side (ReportLab, WeasyPrint, ou similar)
- Sem dependência de sistemas externos (SEI, frota, DETRAN)

### Preocupações Transversais Identificadas

- **Validação**: 25 regras aplicadas tanto no frontend (UX imediata) quanto no backend (integridade)
- **Imutabilidade de registros**: após salvar, nenhum campo pode ser alterado — afeta modelo de dados (soft-lock ou versionamento)
- **Herança de dados entrega→devolução**: devolução herda e bloqueia campos da entrega — relação forte entre registros
- **Armazenamento de imagens**: assinaturas e mapa de avarias geram dados binários que precisam ser persistidos e incluídos no PDF
- **Responsividade**: mapa de avarias e canvas de assinatura precisam funcionar em telas pequenas

## Avaliação de Starter Template

### Domínio Tecnológico Primário

Full-stack web (SPA + REST API) baseado na análise de requisitos — 14 estórias de usuário com formulários interativos, mapa de avarias SVG, canvas de assinatura e geração de PDF.

### Opções Consideradas

| Starter | Stack | Prós | Contras |
|---------|-------|------|---------|
| Official Full Stack FastAPI Template | React + FastAPI + SQLModel + PostgreSQL | Stack completa, auth JWT incluso, Docker, CI/CD, mantido pelo criador do FastAPI | Mais opinativo, pode incluir mais do que necessário |
| Minimal FastAPI Postgres Template v7.0.0 | FastAPI + SQLAlchemy 2.0 async + PostgreSQL | Enxuto, async nativo, Alembic pronto | Apenas backend — frontend precisa ser criado separadamente |
| Vite React TS Template (oficial) | React + TypeScript + Vite | Leve, mínimo, oficial | Apenas frontend — sem backend, sem auth |

### Starter Selecionado: Official Full Stack FastAPI Template

**Justificativa:** Entrega a stack completa exigida (React + FastAPI + PostgreSQL) com autenticação JWT, Docker Compose e CI/CD pré-configurados. Elimina decisões de integração entre frontend e backend. Mantido pelo criador do FastAPI, garantindo compatibilidade a longo prazo.

**Comando de Inicialização:**

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template ctrve --trust
```

**Decisões Arquiteturais Providas pelo Starter:**

**Linguagem & Runtime:**
- Backend: Python 3.11+ com FastAPI e tipagem completa
- Frontend: TypeScript com React 18+ via Vite
- ORM: SQLModel (SQLAlchemy + Pydantic integrados)

**Estilização:**
- Tailwind CSS com shadcn/ui para componentes base

**Build Tooling:**
- Frontend: Vite (build + dev server + HMR)
- Backend: Uvicorn (ASGI server)
- Containerização: Docker + Docker Compose

**Testes:**
- Backend: Pytest com fixtures de banco
- Frontend: configurável (Vitest recomendado)

**Organização de Código:**
- Backend: routers → services → models (SQLModel)
- Frontend: componentes React com hooks e Tanstack Query
- Separação clara frontend/backend em diretórios distintos

**Experiência de Desenvolvimento:**
- Hot reload frontend (Vite) e backend (Uvicorn --reload)
- Docker Compose para ambiente local completo (app + db)
- GitHub Actions para CI/CD

**Nota:** A inicialização do projeto usando este comando deve ser a primeira estória de implementação.

## Decisões Arquiteturais Centrais

### Análise de Prioridade de Decisões

**Decisões Críticas (Bloqueiam Implementação):**
- Armazenamento de dados binários: Base64 no PostgreSQL
- Formato do mapa de avarias: JSON (coordenadas + tipo)
- Autorização: RBAC simples com dois perfis (Responsável, Motorista)
- Geração de PDF: WeasyPrint (HTML/CSS → PDF)
- Formulários: React Hook Form + Zod

**Decisões Importantes (Moldam a Arquitetura):**
- Canvas de assinatura: react-signature-canvas
- Mapa de avarias: SVG inline com handlers React
- Estado do servidor: Tanstack Query
- Estado local: React Context
- Logging: structlog (JSON estruturado)

**Decisões Adiadas (Pós-MVP):**
- Monitoramento com Grafana/Prometheus — logs stdout são suficientes na fase inicial
- Integração LDAP/AD — autenticação própria nesta versão
- Relatórios gerenciais e dashboards — fora de escopo

### Arquitetura de Dados

- **Armazenamento binário:** Base64 direto no PostgreSQL. Assinaturas (canvas PNG ~50-100KB) armazenadas como campo Text. Volume baixo não justifica storage externo.
- **Mapa de avarias:** JSON no PostgreSQL — array de objetos `{x, y, vista, tipo}`. Permite re-renderização no PDF sem armazenar imagem. Tipo restrito a: "risco", "amassado", "trincado".
- **Imutabilidade:** Checklist salvo recebe flag `is_locked = true`. Campos não editáveis após lock. Sem soft-delete — registros oficiais são permanentes.
- **Herança entrega→devolução:** Devolução referencia a entrega via FK (`entrega_id`). Campos herdados lidos da entrega, não duplicados.
- **Migrações:** Alembic (incluído no starter) para versionamento do schema.

### Autenticação & Segurança

- **Método:** JWT (access token 30 min + refresh token 7 dias)
- **Hashing de senha:** bcrypt (incluído no starter)
- **Autorização:** Dependency injection no FastAPI com `require_role("responsavel")`. Motorista tem acesso somente leitura (busca e visualização).
- **Expiração de sessão:** Alinhada com RN-002 — 30 min de inatividade invalida o access token.

### API & Padrões de Comunicação

- **Estilo:** REST com rotas semânticas (`/api/v1/checklists`, `/api/v1/checklists/{id}/devolucao`)
- **Geração de PDF:** WeasyPrint — template HTML/CSS no backend, renderiza assinaturas base64 e mapa SVG diretamente no PDF.
- **Padrão de erros:** Formato padronizado usando códigos MSG do PDS Unificado:
  ```json
  {"detail": "MSG-001", "message": "Usuário ou senha inválidos.", "fields": []}
  ```
- **Documentação:** OpenAPI/Swagger automático do FastAPI (já incluso).

### Arquitetura Frontend

- **Estado do servidor:** Tanstack Query — cache, refetch, sincronização com API
- **Estado local:** React Context para formulário de checklist em preenchimento
- **Formulários:** React Hook Form + Zod para validação tipada das 25 regras de negócio
- **Canvas de assinatura:** react-signature-canvas — exporta PNG base64, botão "Limpar" nativo
- **Mapa de avarias:** SVG inline com 4 vistas estáticas do veículo. Click handler registra coordenada + abre seletor de tipo. Sem biblioteca extra.
- **Validação compartilhada:** Zod (frontend) espelha Pydantic models (backend) — mesmas 25 regras em ambos os lados

### Infraestrutura & Deploy

- **Hospedagem:** On-premise via Docker Compose (infraestrutura própria do TJCE)
- **Serviços:** 3 containers — frontend (Nginx servindo build estático), backend (Uvicorn), PostgreSQL
- **Logging:** structlog com saída JSON no stdout — consultável via `docker logs`
- **Backup:** `pg_dump` agendado via cron no host
- **CI/CD:** GitHub Actions (incluído no starter)

### Análise de Impacto das Decisões

**Sequência de Implementação:**
1. Scaffold do projeto (copier template)
2. Modelo de dados (SQLModel) + migrações Alembic
3. Auth (JWT + RBAC) — já parcialmente pronto no starter
4. CRUD de checklist + validações backend (Pydantic)
5. Formulário frontend (React Hook Form + Zod)
6. Componentes especiais (canvas assinatura + mapa SVG)
7. Geração de PDF (WeasyPrint)
8. Busca por placa
9. Docker Compose de produção

**Dependências Cruzadas:**
- PDF depende do mapa de avarias (precisa re-renderizar SVG) e assinaturas (base64)
- Devolução depende da entrega (FK + herança de dados)
- Validação frontend (Zod) deve espelhar validação backend (Pydantic) — manter em sincronia
- Canvas de assinatura gera base64 que alimenta tanto o banco quanto o PDF

## Padrões de Implementação & Regras de Consistência

### Pontos de Conflito Identificados

12 áreas onde agentes IA poderiam tomar decisões diferentes sem padronização.

### Padrões de Nomenclatura

**Banco de Dados (PostgreSQL):**
- Tabelas: `snake_case` plural — `checklists`, `users`, `checklist_items`
- Colunas: `snake_case` — `created_at`, `quilometragem_inicial`, `is_locked`
- Foreign keys: `{tabela_singular}_id` — `checklist_id`, `user_id`
- Índices: `ix_{tabela}_{coluna}` — `ix_checklists_placa`
- Enums no banco: `snake_case` — `tipo_avaria`, `nivel_combustivel`

**API (FastAPI):**
- Endpoints: plural, `snake_case` — `/api/v1/checklists`, `/api/v1/users`
- Parâmetros de rota: `{id}` — `/api/v1/checklists/{id}`
- Query params: `snake_case` — `?placa=ABC1D23`
- JSON request/response: `snake_case` — `{"quilometragem_inicial": 45000}`

**Código Python (Backend):**
- Classes: `PascalCase` — `ChecklistCreate`, `UserResponse`
- Funções/métodos: `snake_case` — `get_checklist_by_placa()`
- Variáveis: `snake_case` — `checklist_items`
- Arquivos: `snake_case` — `checklist_router.py`, `user_model.py`

**Código TypeScript (Frontend):**
- Componentes: `PascalCase` — `ChecklistForm`, `DamageMap`
- Arquivos de componente: `PascalCase.tsx` — `ChecklistForm.tsx`
- Hooks: `camelCase` com prefixo `use` — `useChecklist`, `useAuth`
- Funções/variáveis: `camelCase` — `getChecklists`, `isLocked`
- Tipos/interfaces: `PascalCase` — `ChecklistResponse`, `DamagePoint`
- Arquivos utilitários: `camelCase.ts` — `validation.ts`, `apiClient.ts`

### Padrões de Estrutura

**Organização de componentes: por feature**
```
frontend/src/
  features/
    auth/          # LoginForm, RegisterForm, useAuth
    checklist/     # ChecklistForm, ChecklistList, useChecklist
    damage-map/    # DamageMap, DamagePoint, useDamageMap
    signature/     # SignatureCanvas, useSignature
    pdf/           # PdfPreview, usePdf
  components/      # componentes compartilhados (Button, Input, Modal)
  hooks/           # hooks genéricos (useLocalStorage, useDebounce)
  lib/             # apiClient, validationSchemas
  types/           # tipos globais
```

**Backend: por domínio**
```
backend/app/
  api/routes/      # checklist.py, user.py, auth.py, pdf.py
  models/          # checklist.py, user.py (SQLModel)
  schemas/         # checklist.py, user.py (Pydantic request/response)
  services/        # checklist_service.py, pdf_service.py
  core/            # config.py, security.py, deps.py
```

**Testes: co-localizados no backend, por feature no frontend**
```
backend/tests/
  api/             # test_checklist.py, test_auth.py
  services/        # test_checklist_service.py
frontend/src/features/checklist/
  __tests__/       # ChecklistForm.test.tsx
```

### Padrões de Formato

**Resposta de sucesso da API:**
```json
{"id": 1, "placa": "ABC1D23", "status": "entregue", "created_at": "2026-04-22T15:30:00Z"}
```
Resposta direta — sem wrapper `{data: ...}`. FastAPI padrão.

**Resposta de erro da API:**
```json
{"detail": "MSG-008", "message": "Já existe um checklist de entrega aberto para o veículo de placa ABC1D23.", "fields": ["placa"]}
```
Código MSG do PDS Unificado + mensagem legível + campos afetados.

**Datas:** ISO 8601 com timezone — `2026-04-22T15:30:00Z` na API. Frontend formata para `dd/mm/aaaa` e `HH:mm` na exibição.

**Booleanos:** `true`/`false` (JSON nativo). Nunca `1`/`0`.

**Null:** Campos opcionais retornam `null`, nunca string vazia ou omissão.

### Padrões de Comunicação

**Estado (Tanstack Query):**
- Query keys padronizadas: `["checklists"]`, `["checklists", id]`, `["checklists", {placa}]`
- Mutations invalidam queries relacionadas após sucesso
- Estado de formulário em preenchimento: React Context isolado por feature

**Eventos de UI:**
- Handlers: `onSubmit`, `onCancel`, `onSignatureClear`, `onDamagePointAdd`
- Sem event bus global — props drilling ou context para comunicação entre componentes

### Padrões de Processo

**Tratamento de erros:**
- Backend: exceções HTTP com schema `{detail, message, fields}`. FastAPI exception handlers globais.
- Frontend: interceptor no apiClient que captura erros HTTP e mapeia para toast/mensagem. Componente `ErrorBoundary` global para erros inesperados.
- Validação: primeiro no frontend (Zod + React Hook Form) para UX imediata, depois no backend (Pydantic) como garantia.

**Estados de loading:**
- Tanstack Query gerencia `isLoading`, `isError`, `isSuccess` por query
- Botão "Salvar" desabilitado durante submit (`isSubmitting` do React Hook Form)
- Skeleton loaders para listas; spinner para ações pontuais

**Fluxo de autenticação:**
- Access token em memória (variável JS). Refresh token em httpOnly cookie.
- Interceptor no apiClient renova token automaticamente em 401.
- Redirect para `/login` quando refresh falha.

### Diretrizes de Aplicação

**Todo agente IA DEVE:**
- Seguir as convenções de nomenclatura acima sem exceção
- Usar os códigos MSG do PDS Unificado para todas as mensagens de erro
- Validar no frontend (Zod) E no backend (Pydantic) — nunca apenas um lado
- Manter componentes em suas features — nunca criar componente de feature em `components/`
- Usar Tanstack Query para toda comunicação com API — nunca `fetch` direto em componentes

**Anti-padrões (PROIBIDO):**
- `camelCase` em nomes de tabela ou coluna do banco
- `any` como tipo no TypeScript — sempre tipar explicitamente
- Estado global (Redux/Zustand) — usar Tanstack Query + Context
- Fetch direto em `useEffect` — usar hooks do Tanstack Query
- Mensagens de erro hardcoded — sempre usar códigos MSG

## Estrutura do Projeto & Limites Arquiteturais

### Estrutura Completa de Diretórios

```
ctrve/
├── README.md
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py          # Settings via pydantic_settings
│   │   │   ├── security.py        # JWT, bcrypt, require_role()
│   │   │   └── deps.py            # FastAPI dependencies (get_db, get_current_user)
│   │   ├── models/
│   │   │   ├── user.py            # User SQLModel (US-001, US-002)
│   │   │   ├── checklist.py       # Checklist SQLModel (US-003, US-005, US-008)
│   │   │   ├── checklist_item.py  # 20 itens verificação (US-005, US-008)
│   │   │   ├── damage_point.py    # Pontos de avaria JSON (US-006)
│   │   │   └── signature.py       # Assinaturas base64 (US-007, US-009)
│   │   ├── schemas/
│   │   │   ├── user.py            # UserCreate, UserResponse
│   │   │   ├── checklist.py       # ChecklistCreate, ChecklistResponse, ChecklistSearch
│   │   │   ├── damage.py          # DamagePointSchema
│   │   │   ├── auth.py            # LoginRequest, TokenResponse
│   │   │   └── error.py           # ErrorResponse (detail, message, fields)
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py        # POST /login, POST /refresh (US-001)
│   │   │       ├── users.py       # POST /users, GET /users/me (US-002)
│   │   │       ├── checklists.py  # CRUD + busca por placa (US-003, US-004, US-005, US-008)
│   │   │       └── pdf.py         # GET /checklists/{id}/pdf (US-012)
│   │   ├── services/
│   │   │   ├── checklist_service.py  # Lógica de negócio: validações RN-005 a RN-025
│   │   │   ├── user_service.py       # Cadastro, unicidade matrícula (RN-003, RN-004)
│   │   │   └── pdf_service.py        # WeasyPrint: geração HTML→PDF (RN-023)
│   │   └── templates/
│   │       └── pdf/
│   │           ├── checklist.html    # Template HTML do PDF
│   │           └── checklist.css     # Estilos do PDF
│   └── tests/
│       ├── conftest.py               # Fixtures: db, client, auth headers
│       ├── api/
│       │   ├── test_auth.py
│       │   ├── test_checklists.py
│       │   ├── test_users.py
│       │   └── test_pdf.py
│       └── services/
│           ├── test_checklist_service.py
│           └── test_pdf_service.py
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   ├── public/
│   │   └── vehicle/
│   │       ├── top.svg
│   │       ├── left.svg
│   │       ├── right.svg
│   │       └── front-rear.svg
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes.tsx
│       ├── features/
│       │   ├── auth/
│       │   │   ├── LoginForm.tsx
│       │   │   ├── RegisterForm.tsx
│       │   │   ├── useAuth.ts
│       │   │   └── __tests__/
│       │   │       └── LoginForm.test.tsx
│       │   ├── checklist/
│       │   │   ├── ChecklistForm.tsx
│       │   │   ├── ChecklistList.tsx
│       │   │   ├── ChecklistView.tsx
│       │   │   ├── ChecklistItems.tsx
│       │   │   ├── FuelLevel.tsx
│       │   │   ├── ObservationsField.tsx
│       │   │   ├── useChecklist.ts
│       │   │   ├── checklistSchema.ts
│       │   │   └── __tests__/
│       │   │       └── ChecklistForm.test.tsx
│       │   ├── damage-map/
│       │   │   ├── DamageMap.tsx
│       │   │   ├── DamagePoint.tsx
│       │   │   ├── useDamageMap.ts
│       │   │   └── __tests__/
│       │   │       └── DamageMap.test.tsx
│       │   ├── signature/
│       │   │   ├── SignatureCanvas.tsx
│       │   │   ├── useSignature.ts
│       │   │   └── __tests__/
│       │   │       └── SignatureCanvas.test.tsx
│       │   └── pdf/
│       │       ├── PdfActions.tsx
│       │       └── usePdf.ts
│       ├── components/
│       │   ├── ui/
│       │   ├── Layout.tsx
│       │   ├── ProtectedRoute.tsx
│       │   ├── ConfirmDialog.tsx
│       │   └── ErrorBoundary.tsx
│       ├── hooks/
│       │   └── useUnsavedChanges.ts
│       ├── lib/
│       │   ├── apiClient.ts
│       │   └── formatters.ts
│       └── types/
│           ├── checklist.ts
│           ├── user.ts
│           └── damage.ts
```

### Limites Arquiteturais

**Limites de API:**
- `/api/v1/auth/*` — autenticação (login, refresh) — público
- `/api/v1/users/*` — gestão de usuários — requer role `responsavel`
- `/api/v1/checklists/*` — CRUD e busca — requer autenticação (leitura: ambos perfis; escrita: `responsavel`)
- `/api/v1/checklists/{id}/pdf` — geração PDF — requer autenticação

**Limites de Dados:**
- `checklist_service.py` é o único ponto de acesso ao modelo Checklist — rotas nunca acessam o banco diretamente
- `pdf_service.py` lê dados via `checklist_service` — nunca acessa o banco sozinho
- Assinaturas base64 trafegam como string no JSON — sem endpoint separado de upload

**Limites de Componentes Frontend:**
- Cada feature é autossuficiente (componentes + hook + schema + testes)
- `components/` contém apenas UI genérica reutilizável (não lógica de negócio)
- `lib/apiClient.ts` é o único ponto de comunicação com o backend

### Mapeamento Requisitos → Estrutura

| Estória | Backend | Frontend |
|---------|---------|----------|
| US-001 Login | `routes/auth.py`, `core/security.py` | `features/auth/LoginForm.tsx` |
| US-002 Cadastro | `routes/users.py`, `services/user_service.py` | `features/auth/RegisterForm.tsx` |
| US-003 Criar checklist | `routes/checklists.py`, `services/checklist_service.py` | `features/checklist/ChecklistForm.tsx` |
| US-004 Busca por placa | `routes/checklists.py` | `features/checklist/ChecklistList.tsx` |
| US-005 Checklist entrega | `services/checklist_service.py` | `ChecklistItems.tsx`, `FuelLevel.tsx` |
| US-006 Mapa avarias | `models/damage_point.py` | `features/damage-map/DamageMap.tsx` |
| US-007 Assinaturas entrega | `models/signature.py` | `features/signature/SignatureCanvas.tsx` |
| US-008 Checklist devolução | `services/checklist_service.py` | `ChecklistForm.tsx` (modo devolução) |
| US-009 Assinaturas devolução | `models/signature.py` | `features/signature/SignatureCanvas.tsx` |
| US-010 Observações | `models/checklist.py` | `features/checklist/ObservationsField.tsx` |
| US-011 Salvar | `services/checklist_service.py` | `ChecklistForm.tsx` + `ConfirmDialog.tsx` |
| US-012 PDF | `routes/pdf.py`, `services/pdf_service.py` | `features/pdf/PdfActions.tsx` |
| US-013 Cancelar | — | `ChecklistForm.tsx` + `ConfirmDialog.tsx` |
| US-014 Navegação | — | `hooks/useUnsavedChanges.ts` |

### Fluxo de Dados

```
[Browser] → [Nginx] → [React SPA]
                          ↓ (API calls via apiClient.ts)
                    [FastAPI/Uvicorn]
                          ↓ (SQLModel queries)
                    [PostgreSQL]
```

**Fluxo de entrega completo:**
1. React `ChecklistForm` coleta dados gerais → valida com Zod
2. `ChecklistItems` coleta 20 itens + `FuelLevel` + `DamageMap` + `SignatureCanvas`
3. `onSubmit` → `apiClient.post("/checklists")` com payload completo (dados + avarias JSON + assinaturas base64)
4. FastAPI `checklists.py` → `checklist_service.py` valida com Pydantic → persiste no PostgreSQL
5. Resposta 201 → frontend redireciona para visualização read-only
6. Botão PDF → `apiClient.get("/checklists/{id}/pdf")` → `pdf_service.py` renderiza WeasyPrint → retorna blob PDF

## Validação da Arquitetura

### Validação de Coerência ✅

**Compatibilidade de decisões:** Sem conflitos. React + Vite + Tailwind + shadcn/ui + React Hook Form + Zod + Tanstack Query + react-signature-canvas são todas bibliotecas compatíveis no ecossistema React. FastAPI + SQLModel + Alembic + WeasyPrint + structlog são compatíveis no ecossistema Python. PostgreSQL suporta JSON nativo (mapa avarias) e Text (base64 assinaturas).

**Consistência de padrões:** `snake_case` no banco e API Python, `camelCase`/`PascalCase` no TypeScript — conversão automática pelo SQLModel/Pydantic. Códigos MSG do PDS Unificado usados consistentemente nos erros de API e mensagens frontend.

**Alinhamento da estrutura:** Organização por feature no frontend alinha com as 6 áreas funcionais das estórias. Backend por domínio (routes/models/schemas/services) alinha com o padrão do starter FastAPI.

### Validação de Cobertura de Requisitos ✅

**Cobertura de estórias:** 14/14 estórias mapeadas para arquivos específicos no backend e frontend.

**Cobertura de regras de negócio:** 25/25 RNs cobertas:
- RN-001 a RN-004 (auth) → `core/security.py` + `services/user_service.py`
- RN-005 a RN-012 (validações) → `services/checklist_service.py` + `checklistSchema.ts`
- RN-013 a RN-014 (mapa avarias) → `models/damage_point.py` + `DamageMap.tsx`
- RN-015 a RN-016 (assinaturas) → `models/signature.py` + `SignatureCanvas.tsx`
- RN-017 a RN-019 (devolução) → `services/checklist_service.py`
- RN-020 a RN-025 (observações/ações) → `ChecklistForm.tsx` + `ConfirmDialog.tsx`

**Requisitos não-funcionais:**
- Responsividade: Tailwind CSS responsivo
- Imutabilidade: `is_locked` flag no modelo + bloqueio de endpoints
- PDF: WeasyPrint com template HTML dedicado
- Sessão: JWT 30 min alinhado com RN-002

### Validação de Prontidão para Implementação ✅

**Decisões completas:** Todas as 5 categorias decididas com tecnologias específicas.
**Estrutura completa:** ~60 arquivos mapeados explicitamente.
**Padrões completos:** 12 pontos de conflito cobertos com regras e exemplos.

### Análise de Lacunas

**Lacunas críticas:** Nenhuma.

**Lacunas importantes:**
- Schema de banco de dados detalhado será gerado na primeira migração Alembic
- Testes E2E não planejados — suficiente para MVP com unitários e integração

**Lacunas opcionais (pós-MVP):**
- Throttling/rate limiting na API
- PWA/offline capability para uso no pátio sem conexão

### Checklist de Completude

- [x] Contexto do projeto analisado
- [x] Escala e complexidade avaliados
- [x] Restrições técnicas identificadas
- [x] Preocupações transversais mapeadas
- [x] Starter template selecionado com justificativa
- [x] Decisões críticas documentadas com tecnologias
- [x] Padrões de nomenclatura estabelecidos
- [x] Padrões de estrutura definidos
- [x] Padrões de comunicação especificados
- [x] Padrões de processo documentados
- [x] Estrutura de diretórios completa
- [x] Limites de componentes estabelecidos
- [x] Mapeamento requisitos → estrutura completo
- [x] Fluxo de dados documentado

### Avaliação de Prontidão

**Status:** PRONTO PARA IMPLEMENTAÇÃO

**Nível de confiança:** Alto — 14/14 estórias e 25/25 regras de negócio com cobertura arquitetural explícita.

**Pontos fortes:**
- Stack coesa e madura (FastAPI + React + PostgreSQL)
- Rastreabilidade completa US → RN → arquivo
- Padrões claros para prevenir conflitos entre agentes IA

**Melhorias futuras:**
- Schema detalhado do banco (gerado via Alembic na implementação)
- Testes E2E com Playwright (pós-MVP)
- Rate limiting e monitoramento (quando em produção)

**Primeira prioridade de implementação:**
```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template ctrve --trust
```

**Diretrizes para agentes IA:**
- Seguir todas as decisões arquiteturais exatamente como documentadas
- Usar padrões de implementação consistentemente em todos os componentes
- Respeitar estrutura do projeto e limites entre componentes
- Consultar este documento para todas as dúvidas arquiteturais
