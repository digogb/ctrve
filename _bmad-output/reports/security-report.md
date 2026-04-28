# Security Report — APROVADO (findings: false positives verificados)

**Data:** 2026-04-28T10:26:31.092795+00:00
**Total findings:** 14
**Critical:** 14 | **High:** 0 | **Medium:** 0 | **Low:** 0

## Findings

| Severidade | Categoria | Arquivo | Linha | Issue | Fix |
| ---------- | --------- | ------- | ----- | ----- | --- |
| false-positive | secrets | /home/rodgb/projetos/ctrve/backend/tests/test_schemas.py | 9 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | secrets | /home/rodgb/projetos/ctrve/backend/tests/test_schemas.py | 34 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | secrets | /home/rodgb/projetos/ctrve/frontend/src/features/auth/__tests__/RegisterForm.test.tsx | 47 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | secrets | /home/rodgb/projetos/ctrve/frontend/src/features/auth/__tests__/RegisterForm.test.tsx | 48 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | secrets | /home/rodgb/projetos/ctrve/frontend/src/features/auth/__tests__/RegisterForm.test.tsx | 115 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | secrets | /home/rodgb/projetos/ctrve/frontend/src/features/auth/__tests__/RegisterForm.test.tsx | 126 | Possible Password found in source code | Move to environment variable or secrets manager |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/api/routes/auth.py | 43 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/api/routes/auth.py | 80 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/core/deps.py | 32 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/services/checklist_service.py | 56 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/services/checklist_service.py | 183 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/services/user_service.py | 42 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/services/user_service.py | 53 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |
| false-positive | input_validation | /home/rodgb/projetos/ctrve/backend/app/services/user_service.py | 88 | Use of eval/exec — potential code injection | Replace with safe alternatives (json.loads, ast.literal_eval) |

---

## Análise de False Positives

### Grupo 1 — "Possible Password" em arquivos de teste (6 findings) — FALSE POSITIVE ✅

**Arquivos afetados:** `backend/tests/test_schemas.py`, `frontend/src/features/auth/__tests__/RegisterForm.test.tsx`

**Diagnóstico:** O scanner identifica o padrão `password\s*[=:]\s*"..."` em qualquer arquivo. Todos os 6 findings estão em **arquivos de teste** (`tests/`, `__tests__/`) com senhas de fixture deliberadamente simples (`"pass"`, `"Senha123"`). Nenhum desses valores representa credencial real ou segredo de produção.

**Evidência de não-risco:** Esses arquivos são excluídos do build de produção. Não existem no bundle final. Não há `.env` com credenciais reais no repositório.

**Veredicto:** ✅ False positive — sem risco de exposição de segredo.

---

### Grupo 2 — "Use of eval/exec" (8 findings) — FALSE POSITIVE ✅

**Arquivos afetados:** `auth.py`, `deps.py`, `checklist_service.py`, `user_service.py`

**Diagnóstico:** O scanner detecta o padrão `\.exec\(` e o classifica como uso do built-in `exec()` do Python. **Na realidade**, todas as ocorrências são chamadas ao método `Session.exec()` do **SQLModel ORM** — a forma correta e segura de executar queries parametrizadas no SQLModel.

**Evidência de não-risco:** As queries usam `select(Model).where(Model.field == param)` — a parametrização é tratada pelo SQLModel/SQLAlchemy, que nunca interpola strings diretamente no SQL. Não há concatenação de string SQL em nenhum dos arquivos flagados.

**Veredicto:** ✅ False positive — ORM com queries parametrizadas, sem risco de SQL injection ou code injection.

---

## Veredicto Final — Segurança

| Tipo | Quantidade | Real? | Decisão |
|------|-----------|-------|---------|
| "Password" em test fixtures | 6 | ❌ FP | Ignorar |
| `session.exec()` SQLModel ORM | 8 | ❌ FP | Ignorar |
| **Vulnerabilidades reais** | **0** | — | — |

**Status: ✅ APROVADO — Nenhuma vulnerabilidade real identificada.**
