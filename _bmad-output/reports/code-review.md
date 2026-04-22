# Code Review — CTRVE Story 1.1 (Login no Sistema)

**Data:** 22/04/2026
**Escopo:** `backend/app/` + `frontend/src/` — Story 1.1 (RN-001, RN-002)
**Resultado:** 4 achados Média, 2 achados Baixa. Nenhum bloqueador Alta.

---

## Achados Média

### CR-001 — Cookie sem `secure=True` em produção

| Campo | Valor |
|-------|-------|
| **Severidade** | Média |
| **Arquivo** | `backend/app/api/routes/auth.py` linhas 49-55 e 83-89 |
| **Evidência** | `response.set_cookie(..., samesite="lax")` — ausência de `secure=True` |

O cookie `refresh_token` não define `secure=True`. Em HTTPS (obrigatório em produção no TJCE), o cookie pode ser transmitido por HTTP sem proteção. O flag `secure` garante transmissão apenas por HTTPS.

**Correção:**
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    samesite="lax",
    secure=not settings.DEBUG,  # True em produção
    max_age=60 * 60 * 24 * 7,
)
```
Adicionar `DEBUG: bool = True` ao `Settings` e definir `DEBUG=False` no `.env` de produção.

---

### CR-002 — `require_role` com mensagem hardcoded (violação de arquitetura)

| Campo | Valor |
|-------|-------|
| **Severidade** | Média |
| **Arquivo** | `backend/app/core/deps.py` linha 43 |
| **Evidência** | `detail="Acesso negado para este perfil."` — sem código MSG |

A arquitetura define explicitamente: *"Nunca use mensagens hardcoded nos handlers — sempre referenciar código MSG do PDS Unificado."* O `messages.md` não define MSG para 403, mas o padrão `{"detail": "MSG-XXX", ...}` deve ser seguido mesmo assim.

**Correção:** Adicionar `MSG-026 — Acesso negado para este perfil de usuário.` ao `messages.md`, ou usar `detail="ACESSO_NEGADO"` com mensagem legível no campo `message`.

---

### CR-003 — `window.location.href` bypassa React Router no logout por expiração

| Campo | Valor |
|-------|-------|
| **Severidade** | Média |
| **Arquivo** | `frontend/src/lib/apiClient.ts` linha 51 |
| **Evidência** | `window.location.href = "/login"` no catch do interceptor de refresh |

Hard navigation recarrega o bundle JavaScript inteiro e perde o estado da aplicação. Embora intencional para "limpeza" de sessão, há alternativa que mantém a SPA íntegra e é mais previsível.

**Recomendação:** Emitir um evento customizado (`window.dispatchEvent(new Event("session-expired"))`) que o `AuthProvider` captura e chama `navigate("/login")`. Mantém SPA e permite exibir MSG-002 antes do redirect.

---

### CR-004 — Catch genérico em `LoginForm` mascara erros de rede como credenciais inválidas

| Campo | Valor |
|-------|-------|
| **Severidade** | Média |
| **Arquivo** | `frontend/src/features/auth/LoginForm.tsx` linhas 39-43 |
| **Evidência** | `catch { setServerError("Usuário ou senha inválidos...") }` — sem distinção de status HTTP |

Se o servidor estiver indisponível (timeout, CORS, rede), o usuário verá "Usuário ou senha inválidos" — mensagem enganosa que pode levar o usuário a tentar credenciais diferentes indefinidamente.

**Correção:**
```typescript
} catch (err) {
  if (axios.isAxiosError(err) && err.response?.status === 401) {
    setServerError("Usuário ou senha inválidos. Verifique suas credenciais e tente novamente.");
  } else {
    setServerError("Erro de comunicação com o servidor. Tente novamente em instantes.");
  }
}
```

---

## Achados Baixa

### CR-005 — `verify_password()` definida mas não usada (dead code)

| Campo | Valor |
|-------|-------|
| **Severidade** | Baixa |
| **Arquivo** | `backend/app/core/security.py` linhas 16-17 |
| **Evidência** | Função `verify_password` não importada em nenhum módulo |

A função `verify_password_safe` substituiu `verify_password` para proteção contra timing attack. A versão simples pode ser removida para evitar que futuros desenvolvedores a usem por engano.

---

### CR-006 — `DUMMY_HASH` gerado no import adiciona latência de startup

| Campo | Valor |
|-------|-------|
| **Severidade** | Baixa |
| **Arquivo** | `backend/app/core/security.py` linha 9 |
| **Evidência** | `DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt())` no nível de módulo |

`bcrypt.gensalt()` gera um novo salt a cada importação (~50-100ms). Em produção, é preferível usar um salt fixo hardcoded para o dummy hash — o objetivo é apenas impor tempo constante, não segurança criptográfica.

**Correção:**
```python
DUMMY_HASH = b"$2b$12$dummy.salt.for.timing.attack.prevention.hash.value"
```

---

## Pontos Positivos

- **Anti-enumeração implementado corretamente** — `verify_password_safe` sempre executa bcrypt, mesmo para usuários inexistentes. Resistência a timing attacks confirmada por `test_login_same_error_for_invalid_and_unknown`.
- **Token armazenado em memória JS** — nenhum dado sensível em `localStorage` ou `sessionStorage`. Confirmado por teste `test_token_nunca_vai_para_localStorage`.
- **Resposta de erro padronizada** — `{"detail": "MSG-001", ...}` segue o padrão de arquitetura em todas as rotas de auth.
- **Interceptor de refresh transparente** — renovação automática do access token em 401 sem intervenção do usuário.
- **Cobertura: 94% backend, 86% frontend** — acima do threshold de 80%.
