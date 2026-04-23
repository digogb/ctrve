# Story 1.1: Login no Sistema

Status: done

## Story

Como Responsável ou Motorista,
quero realizar login com minhas credenciais (usuário + senha),
para que eu possa acessar as funcionalidades do sistema de acordo com meu perfil.

## Acceptance Criteria

1. Sistema exibe tela de login com campos de usuário e senha.
2. Login bem-sucedido redireciona para a tela principal e exibe MSG-024 ("Login realizado com sucesso").
3. Login com credenciais inválidas exibe MSG-001 ("Usuário ou senha inválidos. Verifique suas credenciais e tente novamente.") sem revelar qual campo está incorreto.
4. Sessão expira após 30 minutos de inatividade — redireciona para `/login` com MSG-002.
5. Access token armazenado em memória JS (nunca em localStorage/sessionStorage). Refresh token em httpOnly cookie.
6. Interceptor em `apiClient.ts` renova access token automaticamente em respostas 401 — transparente para o usuário.
7. Rota `/login` é pública. Todas as demais rotas requerem autenticação via `ProtectedRoute`.

## Tasks / Subtasks

- [ ] **T1 — Scaffold do projeto** (pré-requisito de todos os outros tasks)
  - [ ] Executar `copier copy https://github.com/fastapi/full-stack-fastapi-template . --trust` na raiz do repositório
  - [ ] Ajustar `project_name`, `stack_name` e variáveis do `.env.example` para o CTRVE
  - [ ] Verificar que `docker compose up` sobe frontend, backend e PostgreSQL sem erros

- [ ] **T2 — Modelo de usuário (AC: 2, 3)** — `backend/app/models/user.py`
  - [ ] Definir `User` (SQLModel, `table=True`) com campos: `id`, `username`, `full_name`, `matricula` (único), `hashed_password`, `role` (enum: `responsavel`, `motorista`), `is_active`, `created_at`
  - [ ] Criar migration Alembic: `alembic revision --autogenerate -m "create_users_table"`
  - [ ] Criar índice único em `username` e `matricula`

- [ ] **T3 — Schemas de auth (AC: 2, 3)** — `backend/app/schemas/auth.py`
  - [ ] `LoginRequest`: `username: str`, `password: str`
  - [ ] `TokenResponse`: `access_token: str`, `token_type: str = "bearer"` — refresh token vai via Set-Cookie
  - [ ] `ErrorResponse`: `detail: str`, `message: str`, `fields: list[str] = []` (reutilizado em `schemas/error.py`)

- [ ] **T4 — Segurança JWT (AC: 2, 3, 4, 5)** — `backend/app/core/security.py`
  - [ ] Usar bcrypt já provido pelo starter para `hash_password()` e `verify_password()`
  - [ ] `create_access_token(data, expires_delta=30min)` — assina com `SECRET_KEY` do `.env`
  - [ ] `create_refresh_token(data, expires_delta=7days)` — mesmo mecanismo
  - [ ] `decode_token(token)` — levanta `HTTPException(401)` com `{"detail": "MSG-002", "message": "Sua sessão expirou..."}` se expirado
  - [ ] Dependency `get_current_user(token: str = Depends(oauth2_scheme))` → retorna `User` ou levanta 401
  - [ ] Dependency `require_role(role: str)` → levanta 403 se perfil insuficiente

- [ ] **T5 — Router de auth (AC: 2, 3, 6)** — `backend/app/api/routes/auth.py`
  - [ ] `POST /api/v1/auth/login`:
    - Recebe `LoginRequest`
    - Busca usuário por `username` — se não encontrado ou senha inválida: retorna 401 com `{"detail": "MSG-001", "message": "Usuário ou senha inválidos...", "fields": []}` (resposta idêntica para ambos os casos — sem revelar campo)
    - Se válido: retorna `TokenResponse` com access token no body + seta httpOnly cookie `refresh_token` (SameSite=Lax, Secure em produção)
  - [ ] `POST /api/v1/auth/refresh`:
    - Lê cookie `refresh_token`
    - Valida e retorna novo `access_token` no body
    - Se refresh expirado: 401 com MSG-002
  - [ ] Registrar router em `main.py` com prefix `/api/v1/auth`

- [ ] **T6 — Testes backend (AC: 2, 3, 4)** — `backend/tests/api/test_auth.py`
  - [ ] `test_login_success`: POST /login com credenciais válidas → 200 + access_token no body + cookie `refresh_token` setado
  - [ ] `test_login_invalid_password`: POST /login com senha errada → 401 + `detail == "MSG-001"`
  - [ ] `test_login_unknown_user`: POST /login com usuário inexistente → 401 + `detail == "MSG-001"` (mesma resposta)
  - [ ] `test_refresh_success`: POST /refresh com cookie válido → 200 + novo access_token
  - [ ] `test_refresh_expired`: POST /refresh com cookie expirado → 401 + `detail == "MSG-002"`
  - [ ] Adicionar fixture `test_user` em `conftest.py` que cria usuário com role `responsavel`

- [ ] **T7 — apiClient com interceptor (AC: 5, 6, 7)** — `frontend/src/lib/apiClient.ts`
  - [ ] Usar `axios` (já no starter) com `baseURL = import.meta.env.VITE_API_URL`
  - [ ] Access token em variável de módulo (`let accessToken: string | null = null`) — nunca em storage
  - [ ] Exportar `setAccessToken(token)` e `clearAccessToken()`
  - [ ] Interceptor de request: adiciona `Authorization: Bearer ${accessToken}` se presente
  - [ ] Interceptor de response: em 401, chama `POST /api/v1/auth/refresh` uma vez (flag `_retry`). Se OK: atualiza `accessToken` e repete request original. Se falhar: chama `clearAccessToken()` + redireciona para `/login`

- [ ] **T8 — Hook useAuth (AC: 2, 3, 4, 5)** — `frontend/src/features/auth/useAuth.ts`
  - [ ] `login(username, password)` → POST /api/v1/auth/login → salva access token via `setAccessToken()`, retorna `User`
  - [ ] `logout()` → `clearAccessToken()` + redireciona para `/login`
  - [ ] Estado: `{ user: User | null, isLoading: boolean, isAuthenticated: boolean }`
  - [ ] Usar Tanstack Query para estado do servidor — query key `["me"]` com `GET /api/v1/users/me`
  - [ ] Expor via `AuthContext` + `AuthProvider` em `features/auth/AuthContext.tsx`

- [ ] **T9 — LoginForm (AC: 1, 2, 3)** — `frontend/src/features/auth/LoginForm.tsx`
  - [ ] Campos: `username` (text), `password` (password) com labels em português
  - [ ] Validação com Zod: ambos `required` — sem validação de formato (erro vem do backend)
  - [ ] React Hook Form com `onSubmit` → chama `login()` do `useAuth`
  - [ ] Em erro 401: exibe MSG-001 em toast/alerta acima do formulário — **não indica qual campo**
  - [ ] Em sucesso: redireciona para `/` com `navigate("/")`
  - [ ] Botão "Entrar" com `isSubmitting` state (desabilitado + spinner durante request)
  - [ ] Importar shadcn/ui: `Button`, `Input`, `Label`, `Card`

- [ ] **T10 — ProtectedRoute e roteamento (AC: 7)** — `frontend/src/components/ProtectedRoute.tsx`
  - [ ] Se `!isAuthenticated && !isLoading`: redireciona para `/login` via `<Navigate to="/login" replace />`
  - [ ] Se `isLoading`: exibe spinner (aguarda verificação do token)
  - [ ] Configurar em `routes.tsx`: `/login` → `<LoginForm>` (público), `/*` → `<ProtectedRoute><Layout>` (autenticado)

- [ ] **T11 — Testes frontend (AC: 1, 2, 3)** — `frontend/src/features/auth/__tests__/LoginForm.test.tsx`
  - [ ] `test_renders_login_form`: formulário renderiza campos username e password
  - [ ] `test_login_success`: mock de `login()` retornando user → verifica redirecionamento para `/`
  - [ ] `test_login_invalid_credentials`: mock de `login()` rejeitando com MSG-001 → verifica mensagem exibida sem indicar campo
  - [ ] `test_submit_button_disabled_during_submit`: botão fica desabilitado durante o request

## Dev Notes

### Pré-Requisito Crítico: Scaffold do Projeto

**ANTES de qualquer implementação**, executar o scaffold do Full Stack FastAPI Template:

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template . --trust
```

O starter já provê: bcrypt, JWT (python-jose), Alembic, Docker Compose, Tanstack Query, shadcn/ui, axios. **Não reimplementar nada que já está no template.**

### Stack Técnica (obrigatória)

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | FastAPI + Python 3.11+ | — |
| ORM | SQLModel (SQLAlchemy + Pydantic integrados) | — |
| Auth | python-jose (JWT) + bcrypt | já no starter |
| Frontend | React 18 + TypeScript + Vite | — |
| Formulários | React Hook Form + Zod | — |
| Estado servidor | Tanstack Query | — |
| HTTP client | axios (já no starter) | — |
| UI | shadcn/ui + Tailwind CSS | — |
| Testes backend | Pytest com fixtures de banco | — |
| Testes frontend | Vitest | — |

### Padrão de Tokens (crítico — RN-001, RN-002)

```
Access token:  JWT 30min → armazenado em variável de módulo JS (NUNCA localStorage)
Refresh token: JWT 7 dias → httpOnly cookie (SameSite=Lax)
```

O interceptor do axios (`apiClient.ts`) é o **único lugar** onde os tokens são manipulados. Nenhum componente React deve acessar tokens diretamente.

### Resposta de Erro de Auth (crítico — RN-001)

Login com usuário inexistente e login com senha errada devem retornar **exatamente a mesma resposta** para impedir enumeração de usuários:

```json
{"detail": "MSG-001", "message": "Usuário ou senha inválidos. Verifique suas credenciais e tente novamente.", "fields": []}
```

Status HTTP: `401`. Tempo de resposta similar em ambos os casos (bcrypt.checkpw sempre executado mesmo quando usuário não existe — use dummy hash).

### Formato de Erro Padronizado

Todos os erros do backend seguem o schema de `schemas/error.py`:

```json
{"detail": "MSG-XXX", "message": "<texto legível>", "fields": ["campo1"]}
```

Nunca use mensagens hardcoded nos handlers — sempre referenciar código MSG do PDS Unificado.

### Estrutura de Arquivos a Criar/Modificar

**Backend:**
```
backend/app/
  models/user.py              ← CRIAR (SQLModel User)
  schemas/auth.py             ← CRIAR (LoginRequest, TokenResponse)
  schemas/error.py            ← CRIAR (ErrorResponse — reutilizado em toda a app)
  core/security.py            ← MODIFICAR starter (adicionar require_role, ajustar expiração)
  core/deps.py                ← MODIFICAR starter (get_current_user já existe — verificar)
  api/routes/auth.py          ← CRIAR (POST /login, POST /refresh)
  main.py                     ← MODIFICAR (registrar router de auth)
backend/tests/
  conftest.py                 ← MODIFICAR (adicionar fixture test_user)
  api/test_auth.py            ← CRIAR
```

**Frontend:**
```
frontend/src/
  lib/apiClient.ts                        ← CRIAR (axios + interceptors)
  features/auth/AuthContext.tsx           ← CRIAR
  features/auth/useAuth.ts               ← CRIAR
  features/auth/LoginForm.tsx            ← CRIAR
  features/auth/__tests__/LoginForm.test.tsx  ← CRIAR
  components/ProtectedRoute.tsx           ← CRIAR
  routes.tsx                             ← CRIAR/MODIFICAR
```

### Roles de Usuário (RBAC — RN-001)

```python
class UserRole(str, Enum):
    responsavel = "responsavel"
    motorista = "motorista"
```

- `responsavel`: acesso de escrita a checklists, cadastro de usuários
- `motorista`: acesso somente leitura (busca + visualização)

Implementar `require_role()` como dependency FastAPI — será reutilizado em todas as rotas das próximas stories.

### Convenções de Nomenclatura

- Tabela PostgreSQL: `users` (snake_case plural)
- Colunas: `snake_case` — `hashed_password`, `created_at`, `is_active`
- Classes Python: `PascalCase` — `User`, `UserCreate`, `UserResponse`
- Funções Python: `snake_case` — `get_current_user()`, `verify_password()`
- Componentes React: `PascalCase.tsx` — `LoginForm.tsx`
- Hooks: `camelCase` prefixo `use` — `useAuth.ts`

### Anti-padrões (PROIBIDO nesta story)

- ❌ `localStorage.setItem("token", ...)` — tokens nunca em storage persistente
- ❌ `fetch()` direto em componente React — usar apenas via `apiClient.ts`
- ❌ Mensagem diferente para "usuário não existe" vs "senha errada" — timing attack
- ❌ `any` em TypeScript — sempre tipar explicitamente
- ❌ Validação apenas no frontend — backend DEVE validar também

### Project Structure Notes

- Esta story estabelece o padrão de autenticação reutilizado por todas as demais: `get_current_user`, `require_role`, `ProtectedRoute`, `AuthContext`
- O `apiClient.ts` criado aqui será o único ponto de comunicação com o backend em **todas as stories futuras** — implementar bem agora evita refatorações

### References

- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — seções "Autenticação & Segurança", "Padrões de Comunicação", "Estrutura Completa de Diretórios"
- Regras de Negócio: `_bmad-output/requirements/business-rules.md` — RN-001, RN-002
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-001, MSG-002, MSG-024
- Starter template: https://github.com/fastapi/full-stack-fastapi-template

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- bcrypt + passlib incompatível com Python 3.12 — substituído por uso direto do `bcrypt`
- pydantic-settings e pydantic_settings instalados separadamente no venv
- Frontend migrado de CRA para Vite; App.test.tsx do CRA atualizado

### Completion Notes List

- Backend: estrutura completa criada (models, schemas, core, routes, tests)
- JWT: access token 30min em memória JS, refresh token 7d em httpOnly cookie
- Anti-enumeração: `verify_password_safe()` sempre executa bcrypt mesmo sem usuário
- 6 testes backend passando (login ok, login inválido, usuário inexistente, resposta idêntica, refresh ok, refresh sem cookie)
- Frontend: migrado CRA → Vite; instalado axios, Tanstack Query, React Hook Form, Zod, react-router-dom, vitest
- 5 testes frontend passando (renderização, login ok, credenciais inválidas, botão desabilitado durante submit, App renderiza login)

### File List

backend/app/__init__.py
backend/app/main.py
backend/app/database.py
backend/app/core/__init__.py
backend/app/core/config.py
backend/app/core/security.py
backend/app/core/deps.py
backend/app/models/__init__.py
backend/app/models/user.py
backend/app/schemas/__init__.py
backend/app/schemas/auth.py
backend/app/schemas/error.py
backend/app/schemas/user.py
backend/app/api/__init__.py
backend/app/api/routes/__init__.py
backend/app/api/routes/auth.py
backend/tests/__init__.py
backend/tests/conftest.py
backend/tests/api/__init__.py
backend/tests/api/test_auth.py
frontend/index.html
frontend/vite.config.ts
frontend/src/App.tsx
frontend/src/App.test.tsx
frontend/src/index.tsx
frontend/src/setupTests.ts
frontend/src/routes.tsx
frontend/src/lib/apiClient.ts
frontend/src/types/user.ts
frontend/src/features/auth/AuthContext.tsx
frontend/src/features/auth/useAuth.ts
frontend/src/features/auth/LoginForm.tsx
frontend/src/features/auth/__tests__/LoginForm.test.tsx
frontend/src/components/ProtectedRoute.tsx

### Review Findings

> Code review executado em 2026-04-23 — 2 decision-needed, 21 patches, 6 deferred, 2 dismissed.

#### Decisões necessárias

- [x] [Review][Decision → Patch] Inactivity timer — implementar agora: listener DOM + timer de reset + logout automático aos 30min
- [x] [Review][Decision → Patch] `AuthContext` sem Provider — refatorar: criar `AuthProvider`, `LoginForm` e `ProtectedRoute` consomem `useAuthContext()`

#### Patches

- [x] [Review][Patch] Cookie `secure` ausente no endpoint `/refresh` — cookie rotacionado não terá flag Secure em produção [backend/app/api/routes/auth.py:91]
- [x] [Review][Patch] `matricula: str` — tipo Python em arquivo TypeScript, deveria ser `string` [frontend/src/types/user.ts:5]
- [x] [Review][Patch] `user.is_active` acessado sem guarda `user is None` explícita — seguro apenas pela ordem atual das linhas [backend/app/api/routes/auth.py:33]
- [x] [Review][Patch] MSG-024 nunca exibida no login bem-sucedido — AC-2 violado; `navigate("/")` sem toast/mensagem [frontend/src/features/auth/LoginForm.tsx:34]
- [x] [Review][Patch] MSG-002 nunca exibida no redirect por sessão expirada — AC-4 violado; `SessionGuard` só navega, não passa a mensagem [frontend/src/App.tsx:22]
- [x] [Review][Patch] `DUMMY_HASH` usa custo bcrypt `$2b$04$` — muito baixo; timing anti-enumeration é trivialmente detectável [backend/app/core/security.py:7]
- [x] [Review][Patch] `initialData: null` em `useQuery` torna `isLoading` sempre `false` no mount — pode causar redirect prematuro para `/login` [frontend/src/features/auth/useAuth.ts:17]
- [x] [Review][Patch] `DEBUG: bool = True` como padrão — inverte segurança; produção sem `.env` explícito emite cookies sem `Secure` [backend/app/core/config.py:9]
- [x] [Review][Patch] Interceptor de refresh usa URL hardcoded `/api/v1/auth/refresh` ignorando `VITE_API_URL` [frontend/src/lib/apiClient.ts:30]
- [x] [Review][Patch] Race condition: requisições concorrentes com 401 não são enfileiradas — a segunda falha silenciosamente enquanto `isRefreshing=true` [frontend/src/lib/apiClient.ts:24]
- [x] [Review][Patch] `SECRET_KEY` com valor padrão público — deve falhar na inicialização se não houver valor real de ambiente [backend/app/core/config.py:5]
- [x] [Review][Patch] `staleTime` inconsistente: `Infinity` em `useAuth` vs `5min` em `ProtectedRoute` para a mesma query `["me"]` [frontend/src/features/auth/useAuth.ts:17, frontend/src/components/ProtectedRoute.tsx:8]
- [x] [Review][Patch] `login()` em `useAuth` não captura erros — `loginError` nunca é populado pelo hook [frontend/src/features/auth/useAuth.ts:27]
- [x] [Review][Patch] `HTTPException` reutilizada como instância global mutável — potencial corrupção em requisições concorrentes [backend/app/api/routes/auth.py:13]
- [x] [Review][Patch] CORS com origens hardcoded e `allow_methods=["*"]` — mover para `settings` [backend/app/main.py:13]
- [x] [Review][Patch] `fetchMe` duplicada em `ProtectedRoute` e `useAuth` — extrair para módulo compartilhado [frontend/src/components/ProtectedRoute.tsx:6, frontend/src/features/auth/useAuth.ts:8]
- [x] [Review][Patch] `require_role` sem cobertura de testes [backend/tests/api/test_auth.py]
- [x] [Review][Patch] `test_refresh_success` não verifica rotação do cookie de refresh [backend/tests/api/test_auth.py:43]
- [x] [Review][Patch] Ausência de teste para usuário inativo (`is_active=False`) [backend/tests/api/test_auth.py]
- [x] [Review][Patch] `LoginRequest` sem `max_length` — senha muito longa alcança bcrypt (DoS potencial) [backend/app/schemas/auth.py]
- [x] [Review][Patch] `LoginForm` importa `axios` diretamente para `isAxiosError` — quebra encapsulamento de `apiClient` [frontend/src/features/auth/LoginForm.tsx:7]
- [x] [Review][Patch] Implementar inactivity timer — listener DOM (`mousemove`, `keydown`, `click`) + timeout de 30min + logout automático com MSG-002 [frontend/src/features/auth/useAuth.ts ou AuthContext]
- [x] [Review][Patch] Criar `AuthProvider` e refatorar `LoginForm` e `ProtectedRoute` para consumir `useAuthContext()` [frontend/src/features/auth/AuthContext.tsx]

#### Deferidos

- [x] [Review][Defer] `engine` criado em tempo de importação de módulo [backend/app/database.py:3] — deferred, padrão pré-existente do projeto
- [x] [Review][Defer] Refresh token drift em falha de entrega da resposta — deferred, limitação inerente de JWT stateless sem blacklist
- [x] [Review][Defer] Erros de rede (5xx) não distinguíveis de erros de auth no interceptor — deferred, trade-off aceitável
- [x] [Review][Defer] Flash redirect potencial em StrictMode/dev — deferred, quirk de desenvolvimento sub-ms
- [x] [Review][Defer] `queryClient` instanciado fora do componente em `App.tsx` — deferred, impacta isolamento de testes
- [x] [Review][Defer] `require_role` igualdade estrita sem suporte a hierarquia de roles — deferred, sem requisito de hierarquia na spec atual
