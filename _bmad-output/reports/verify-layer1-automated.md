# Verificação Automatizada — Camada 1

**Data:** 2026-04-28T10:24:00Z
**Escopo:** CTRVE Epics 1–6 (Stories 1.1–6.3 | RN-001 a RN-025)
**Threshold de cobertura:** 80%
**Status:** ✅ PASS
**Cobertura: 87.32%** (backend 97% | frontend 87.32% | threshold 80%)

---

## Execução dos Testes

### Backend — Python / pytest

| Métrica | Valor |
|---------|-------|
| Total de testes | 106 |
| Passaram | **106** |
| Falharam | 0 |
| Ignorados | 0 |
| Cobertura (statements) | **97%** |
| Status | ✅ PASS |

**Detalhe por módulo (gaps residuais, todos acima de 80%):**

| Módulo | Cobertura | Linhas descobertas |
|--------|-----------|-------------------|
| `app/api/routes/auth.py` | 90% | 76-78, 82 |
| `app/api/routes/pdf.py` | 95% | 38 |
| `app/core/deps.py` | 93% | 28, 34 |
| `app/core/security.py` | 97% | 52 |
| `app/database.py` | 80% | 15-16 |
| `app/schemas/checklist.py` | 98% | 86, 97 |
| `app/services/checklist_service.py` | 99% | 166 |
| `app/services/user_service.py` | 89% | 75-77, 88 |
| Demais módulos | 100% | — |

### Frontend — TypeScript / Vitest

| Métrica | Valor |
|---------|-------|
| Total de testes | 153 |
| Passaram | **153** |
| Falharam | 0 |
| Ignorados | 0 |
| Cobertura (statements) | **87.32%** |
| Cobertura (branches) | **79.68%** |
| Cobertura (functions) | **86.43%** |
| Cobertura (lines) | **88.51%** |
| Status | ✅ PASS |

---

## Veredicto da Camada 1

| Stack | Testes | Cobertura | Status |
|-------|--------|-----------|--------|
| Backend (pytest) | 106/106 ✅ | 97% ✅ | **PASS** |
| Frontend (vitest) | 153/153 ✅ | 87.32% ✅ | **PASS** |

**Resultado: ✅ PASS — Gate de cobertura superado em ambas as stacks.**
