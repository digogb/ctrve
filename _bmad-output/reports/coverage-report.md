# Relatório de Cobertura — CTRVE (Story 1.1)

**Data:** 22/04/2026
**Threshold:** 80%

## Resultado

| Stack | Cobertura | Status |
|-------|-----------|--------|
| Backend (Python/pytest) | **94%** | ✅ PASS |
| Frontend (TypeScript/Vitest) | **86%** | ✅ PASS |

## Backend — Detalhe por Módulo

| Módulo | Cobertura | Linhas Descobertas |
|--------|-----------|-------------------|
| `app/api/routes/auth.py` | 88% | 44, 72-74, 78 (branches de cookie/refresh) |
| `app/core/deps.py` | 93% | 28, 34 (branches de role/inactive) |
| `app/core/security.py` | 94% | 17, 54 (edge cases de token type) |
| `app/database.py` | 75% | 13-14 (create_db_and_tables — startup) |
| Demais módulos | 100% | — |

**Total: 17 testes | 94% cobertura**

## Frontend — Detalhe por Módulo

| Módulo | Cobertura | Linhas Descobertas |
|--------|-----------|-------------------|
| `src/lib/apiClient.ts` | 81% | 49-55 (fallback de redirect no refresh) |
| `src/components/ProtectedRoute.tsx` | 87% | 28 (redirect branch) |
| `src/routes.tsx` | 50% | 6 (Dashboard — componente stub) |
| `src/features/auth/LoginForm.tsx` | 100% | — |

**Total: 15 testes | 86% cobertura**

## RNs Cobertas pelos Testes

| RN | Descrição | Testes |
|----|-----------|--------|
| RN-001 | Autenticação de usuário | test_login_success, test_login_invalid_password, test_login_unknown_user, test_login_same_error_for_invalid_and_unknown, LoginForm tests |
| RN-002 | Expiração de sessão | test_refresh_success, test_refresh_without_cookie, response interceptor tests |
