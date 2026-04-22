# Story 1.2: Cadastro de Usuário

Status: review

## Story

Como Responsável,
quero cadastrar novos usuários no sistema,
para que motoristas e outros responsáveis possam acessar o CTRVE.

## Acceptance Criteria

1. Formulário de cadastro com campos: nome completo, matrícula, perfil (Responsável ou Motorista), nome de usuário e senha.
2. Sistema impede cadastro com matrícula já existente e exibe MSG-003 ("A matrícula informada já está cadastrada no sistema").
3. Cadastro bem-sucedido retorna 201 e exibe MSG-023 ("Usuário cadastrado com sucesso").
4. Senha deve atender RN-004: mínimo 8 caracteres, ao menos uma maiúscula, uma minúscula e um número. Falha exibe MSG-004.
5. Apenas usuários com perfil **Responsável** podem cadastrar novos usuários (403 com MSG-026 para Motorista).
6. `GET /api/v1/users/me` retorna dados do usuário autenticado (usado pelo `ProtectedRoute` e `useAuth`).
7. Formulário acessível somente para usuários autenticados com perfil Responsável.

## Tasks / Subtasks

- [ ] **T1 — user_service.py (AC: 2, 3, 4)** — `backend/app/services/user_service.py`
  - [ ] `create_user(session, data: UserCreate) -> User`:
    - Verifica unicidade de `matricula` — se duplicada, levanta `HTTPException(400, detail="MSG-003", fields=["matricula"])`
    - Valida senha (RN-004): regex `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$` — falha levanta `HTTPException(422, detail="MSG-004", fields=["password"])`
    - Chama `hash_password()` de `core/security.py`
    - Persiste e retorna `User`
  - [ ] `get_user_by_username(session, username: str) -> User | None`

- [ ] **T2 — Router de usuários (AC: 2, 3, 5, 6)** — `backend/app/api/routes/users.py`
  - [ ] `POST /api/v1/users` (requer `require_role(UserRole.responsavel)`):
    - Recebe `UserCreate`
    - Delega para `user_service.create_user()`
    - Retorna `UserResponse` com status 201
  - [ ] `GET /api/v1/users/me` (requer `get_current_user`):
    - Retorna `UserResponse` do usuário autenticado
  - [ ] Registrar router em `main.py` com prefix `/api/v1`

- [ ] **T3 — Testes backend (AC: 2, 3, 4, 5, 6)** — `backend/tests/api/test_users.py`
  - [ ] `test_create_user_success`: POST /users com dados válidos → 201 + `UserResponse`
  - [ ] `test_create_user_duplicate_matricula`: POST /users com matrícula já existente → 400 + `detail == "MSG-003"`
  - [ ] `test_create_user_weak_password`: POST /users com senha sem maiúscula → 422 + `detail == "MSG-004"`
  - [ ] `test_create_user_requires_responsavel`: POST /users autenticado como motorista → 403 + `detail == "MSG-026"`
  - [ ] `test_create_user_unauthenticated`: POST /users sem token → 401
  - [ ] `test_get_me_authenticated`: GET /users/me com token válido → 200 + dados do usuário
  - [ ] `test_get_me_unauthenticated`: GET /users/me sem token → 401

- [ ] **T4 — Zod schema + RegisterForm (AC: 1, 2, 3, 4)** — `frontend/src/features/auth/RegisterForm.tsx`
  - [ ] Schema Zod `registerSchema`:
    - `full_name`: `string().min(1)`
    - `matricula`: `string().min(1)`
    - `username`: `string().min(1)`
    - `role`: `enum(["responsavel", "motorista"])`
    - `password`: regex `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$` com mensagem MSG-004
    - `confirmPassword`: deve ser igual a `password` (validação cross-field com `refine`)
  - [ ] Componente `RegisterForm`:
    - Campos: nome completo, matrícula, usuário, perfil (select), senha, confirmação de senha
    - `onSubmit` → `POST /api/v1/users` via `apiClient`
    - Sucesso: exibe MSG-023 como alerta de sucesso + redireciona para `/login` após 2s
    - Erro 400 (matrícula duplicada): exibe MSG-003 no campo matrícula
    - Erro 422 (senha fraca): exibe MSG-004 no campo senha
    - Erro 403: não ocorre (rota protegida — só Responsável acessa)

- [ ] **T5 — Rota `/register` e proteção por perfil (AC: 5, 7)** — `frontend/src/routes.tsx`
  - [ ] Adicionar rota `/register` dentro do `ProtectedRoute`
  - [ ] Criar `RequireRole` wrapper que redireciona para `/` se o perfil não for `responsavel`
  - [ ] Wrapper aplicado à rota `/register`

- [ ] **T6 — Testes frontend (AC: 1, 2, 3, 4)** — `frontend/src/features/auth/__tests__/RegisterForm.test.tsx`
  - [ ] `test_renders_all_fields`: formulário renderiza todos os campos
  - [ ] `test_cadastro_success`: mock POST 201 → exibe MSG-023
  - [ ] `test_matricula_duplicada`: mock POST 400 MSG-003 → exibe erro no campo matrícula
  - [ ] `test_senha_fraca_frontend`: senha sem maiúscula → Zod bloqueia antes de submeter
  - [ ] `test_confirmacao_senha_diferente`: confirmação diferente da senha → Zod bloqueia

## Dev Notes

### Código Reutilizável da Story 1.1 — NÃO REIMPLEMENTAR

| Item | Localização | Reutiliza Como |
|------|-------------|----------------|
| `User` model | `backend/app/models/user.py` | Import direto — não criar novo model |
| `UserCreate`, `UserResponse` | `backend/app/schemas/user.py` | Schemas prontos para POST e GET |
| `hash_password()` | `backend/app/core/security.py` | Chamar em `user_service.create_user()` |
| `get_current_user` | `backend/app/core/deps.py` | Dependency para `GET /users/me` |
| `require_role(UserRole.responsavel)` | `backend/app/core/deps.py` | Dependency para `POST /users` |
| `ErrorResponse` | `backend/app/schemas/error.py` | Formato de erro padronizado |
| `apiClient` | `frontend/src/lib/apiClient.ts` | Usar para POST /users |
| `UserRole` type | `frontend/src/types/user.ts` | Import no RegisterForm |

### Validação de Senha (RN-004) — implementar em AMBAS as camadas

```python
# Backend — user_service.py
import re
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

if not PASSWORD_REGEX.match(data.password):
    raise HTTPException(
        status_code=422,
        detail="MSG-004",
        headers=None,
    )
```

```typescript
// Frontend — Zod schema
const passwordSchema = z
  .string()
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
    "A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número."
  );
```

### Unicidade de Matrícula (RN-003) — verificar ANTES do hash

```python
existing = session.exec(select(User).where(User.matricula == data.matricula)).first()
if existing:
    raise HTTPException(
        status_code=400,
        detail="MSG-003",
        message="A matrícula informada já está cadastrada no sistema.",
        fields=["matricula"],
    )
```

**Importante:** usar `HTTPException` com `detail="MSG-003"` — não retornar 409 Conflict, usar 400 conforme padrão estabelecido.

### `GET /users/me` — Crítico para o `ProtectedRoute`

O `ProtectedRoute` da Story 1.1 chama `GET /api/v1/users/me` para verificar autenticação. Este endpoint DEVE ser implementado nesta story, ou o ProtectedRoute quebra em produção.

```python
@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

### Padrão de Resposta de Erro

Seguir exatamente o padrão de `schemas/error.py`:
```json
{"detail": "MSG-003", "message": "A matrícula informada já está cadastrada.", "fields": ["matricula"]}
```

**Atenção:** `HTTPException` do FastAPI aceita `detail` como qualquer tipo, mas o campo `message` e `fields` precisam ser passados via `headers` ou tratados com `exception_handler`. Solução: criar `UserException` customizada ou usar `HTTPException(detail={"detail": "MSG-003", "message": "...", "fields": []})` e configurar handler em `main.py`.

### Estrutura de Arquivos a Criar/Modificar

**Backend:**
```
backend/app/
  services/user_service.py     ← CRIAR
  api/routes/users.py          ← CRIAR
  main.py                      ← MODIFICAR (registrar router de users)
backend/tests/api/
  test_users.py                ← CRIAR
```

**Frontend:**
```
frontend/src/
  features/auth/
    RegisterForm.tsx            ← CRIAR
    registerSchema.ts           ← CRIAR (Zod schema separado)
    __tests__/
      RegisterForm.test.tsx     ← CRIAR
  components/
    RequireRole.tsx             ← CRIAR
  routes.tsx                   ← MODIFICAR
```

### Padrão de Erros HTTP com Campos — Implementar Exception Handler

A Story 1.1 usou `HTTPException(detail="MSG-XXX")` que funciona para erros simples. Para erros com `fields` (RN-003, RN-004), a solução mais limpa é criar uma exception customizada com handler global em `main.py`:

```python
# main.py
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, status_code: int, detail: str, message: str, fields: list[str] = []):
        self.status_code = status_code
        self.detail = detail
        self.message = message
        self.fields = fields

@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "message": exc.message, "fields": exc.fields}
    )
```

Esta `AppError` será reutilizada em todas as stories seguintes (RN-005 a RN-025).

### Convenções Estabelecidas na Story 1.1

- Nomenclatura tabelas: `snake_case` plural — `users`
- Classes Python: `PascalCase` — `UserService`, `UserCreate`
- Funções Python: `snake_case` — `create_user()`
- Componentes React: `PascalCase.tsx` — `RegisterForm.tsx`
- Anti-padrões: `any` no TypeScript, fetch direto sem `apiClient`, mensagens hardcoded sem código MSG

### Project Structure Notes

- `user_service.py` é o primeiro service file — estabelece o padrão de service layer para as stories seguintes (checklist_service.py, pdf_service.py)
- `RequireRole` component complementa o `ProtectedRoute` existente para controle de acesso por perfil no frontend
- O `exception_handler` de `AppError` em `main.py` será base para todas as validações de checklist

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-003, RN-004
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-003, MSG-004, MSG-023, MSG-026
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — seções "Autenticação & Segurança", "Estrutura de Diretórios"
- Story 1.1: `_bmad-output/implementation-artifacts/1-1-login-no-sistema.md` — código base reutilizado

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `getByLabelText(/Senha/i)` capturava "Senha" e "Confirmar Senha" — seletores do fillForm corrigidos para `password` e `confirmPassword` keys

### Completion Notes List

- Backend: `user_service.py` com validação RN-003 (matrícula única) e RN-004 (senha complexa), `UserError` exception reutilizável
- Backend: `POST /api/v1/users` (requer responsavel) + `GET /api/v1/users/me` (qualquer autenticado)
- Backend: `exception_handler(UserError)` em `main.py` — padrão `{detail, message, fields}` para todas as stories seguintes
- Frontend: `registerSchema.ts` com Zod incluindo validação cross-field de confirmação de senha
- Frontend: `RegisterForm.tsx` com tratamento granular de MSG-003 e MSG-004
- Frontend: `RequireRole.tsx` para controle de acesso por perfil em rotas
- 9 testes backend + 5 testes frontend (+ 17 regressões passando)

### File List

backend/app/services/user_service.py
backend/app/api/routes/users.py
backend/app/main.py
backend/tests/api/test_users.py
frontend/src/features/auth/registerSchema.ts
frontend/src/features/auth/RegisterForm.tsx
frontend/src/features/auth/__tests__/RegisterForm.test.tsx
frontend/src/components/RequireRole.tsx
frontend/src/routes.tsx
