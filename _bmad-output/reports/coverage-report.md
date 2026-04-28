# Relatório de Cobertura — CTRVE (Epics 1–6)

**Data:** 2026-04-28
**Threshold:** 80%
**Resultado:** ✅ APROVADO

---

## Resultado por Stack

| Stack | Testes | Cobertura | Status |
|-------|--------|-----------|--------|
| Backend (Python/pytest) | **106/106** | **97.0%** | ✅ PASS |
| Frontend (TypeScript/Vitest) | **153/153** | **87.32%** | ✅ PASS |

---

## Backend — Detalhe por Módulo

| Módulo | Cobertura | Linhas Descobertas |
|--------|-----------|-------------------|
| `app/api/routes/auth.py` | 90% | 76-78, 82 |
| `app/api/routes/checklists.py` | 100% | — |
| `app/api/routes/pdf.py` | 95% | 38 |
| `app/api/routes/users.py` | 100% | — |
| `app/core/deps.py` | 93% | 28, 34 |
| `app/core/security.py` | 97% | 52 |
| `app/database.py` | 80% | 15-16 |
| `app/main.py` | 100% | — |
| `app/models/checklist.py` | 100% | — |
| `app/models/user.py` | 100% | — |
| `app/schemas/checklist.py` | 98% | 86, 97 |
| `app/services/checklist_service.py` | 99% | 166 |
| `app/services/pdf_service.py` | 100% | — |
| `app/services/user_service.py` | 89% | 75-77, 88 |

**Total: 106 testes | 97.0% cobertura (544/561 statements)**

---

## Frontend — Detalhe por Módulo

| Módulo | Statements | Branches | Funcs | Lines |
|--------|-----------|----------|-------|-------|
| `src/features/dashboard/Dashboard.tsx` | **100%** | 88.88% | **100%** | **100%** |
| `src/features/signature/SignaturePad.tsx` | **100%** | 92.85% | **100%** | **100%** |
| `src/features/auth/LoginForm.tsx` | **100%** | 88.23% | **100%** | **100%** |
| `src/features/auth/useAuth.ts` | **95.45%** | 92.3% | 90% | 95.23% |
| `src/features/checklist/ChecklistItems.tsx` | **100%** | 89.28% | **100%** | **100%** |
| `src/features/checklist/FuelLevel.tsx` | **100%** | 75% | **100%** | **100%** |
| `src/features/damage-map/VehicleView.tsx` | 92.5% | 80.95% | **100%** | 94.73% |
| `src/components/ui/button.tsx` | **100%** | 80% | **100%** | **100%** |
| `src/components/ui/badge.tsx` | **100%** | 75% | **100%** | **100%** |
| `src/features/auth/RegisterForm.tsx` | 81.48% | 71.87% | 80% | 84% |
| `src/features/checklist/ChecklistForm.tsx` | 82.75% | 73.68% | 66.66% | 82.75% |
| `src/lib/apiClient.ts` | 82.22% | 78.57% | 63.63% | 84.09% |
| `src/components/RequireRole.tsx` | 75% | 60% | **100%** | 77.77% |
| `src/features/checklist/ChecklistView.tsx` | 81.64% | 80.73% | 78.26% | 83.85% |
| `src/features/checklist/ChecklistList.tsx` | 88.46% | 81.48% | 90% | 95.83% |
| `src/hooks/useUnsavedChanges.ts` | 83.33% | 87.5% | 80% | 78.57% |

**Total: 153 testes | 87.32% cobertura (565/647 statements)**

---

## RNs Cobertas pelos Testes

| RN | Descrição | Stack | Testes Representativos |
|----|-----------|-------|------------------------|
| RN-001 | Autenticação de usuário | BE+FE | test_login_*, LoginForm tests, useAuth login tests |
| RN-002 | Expiração de sessão | BE+FE | test_refresh_*, useAuth logout/inactivity tests |
| RN-003 | Unicidade de matrícula | BE+FE | test_create_user_duplicate_matricula, RegisterForm tests |
| RN-004 | Requisitos de senha | BE+FE | test_create_user_weak_password_* |
| RN-005 | Campos obrigatórios | BE+FE | test_create_checklist_*, ChecklistForm validation tests |
| RN-006 | Formato de placa | BE+FE | test_create_checklist_placa_invalida, ChecklistForm placa tests |
| RN-007 | Matrícula numérica | BE+FE | test_create_checklist_matricula_nao_numerica |
| RN-008 | Entrega duplicada | BE+FE | test_create_checklist_entrega_duplicada, ChecklistForm MSG-008 test |
| RN-009 | Busca por placa | BE+FE | test_search_by_placa_*, ChecklistList tests |
| RN-010 | Verificação 20 itens | BE | test_update_entrega_menos_de_20_itens |
| RN-011 | Combustível exclusivo | BE+FE | ChecklistView fuel tests |
| RN-012 | Data e horário | BE+FE | test_update_entrega_*, ChecklistView tests |
| RN-013 | Tipo de avaria | BE+FE | test_update_entrega_avaria_*, DamageMap tests |
| RN-014 | Avarias só na entrega | BE+FE | test_update_devolucao_*, ChecklistView tests |
| RN-015 | Assinaturas obrigatórias | BE+FE | test_update_entrega_sem_assinatura_*, SignaturePad tests |
| RN-016 | Imutabilidade de assinatura | BE | test_update_entrega_locked |
| RN-017 | Devolução exige entrega | BE | test_update_devolucao_sem_entrega_previa |
| RN-018 | Herança de dados | BE+FE | test_get_checklist_retorna_campos_devolucao |
| RN-019 | Consistência km/data | BE | test_update_devolucao_quilometragem_menor, test_update_devolucao_data_anterior |
| RN-020 | Observações opcionais | BE+FE | test_update_entrega_com_observacoes |
| RN-021 | Validação antes de salvar | BE+FE | test_update_entrega_ok, ChecklistView save tests |
| RN-022 | Confirmação antes de salvar | FE | ChecklistView confirmation tests |
| RN-023 | Geração de PDF | BE+FE | test_gerar_pdf_*, ChecklistView PDF tests |
| RN-024 | Cancelamento com descarte | BE+FE | test_cancelar_checklist_*, ChecklistForm cancel test |
| RN-025 | Alerta dados não salvos | FE | useUnsavedChanges tests |

---

## Novos Testes Adicionados neste BUILD

| Arquivo | Testes | Cobertura Anterior | Cobertura Atual |
|---------|--------|-------------------|----------------|
| `RequireRole.test.tsx` | 5 | 0% | 75% |
| `useAuth.test.ts` | 12 | 6.81% | 95.45% |
| `AuthContext.test.tsx` | 3 | 57.14% | ~85% |
| `Dashboard.test.tsx` | 11 | 5.55% | 100% |
| `apiClient.test.ts` (ampliado) | +4 | 64.44% | 82.22% |
| `ChecklistForm.test.tsx` (ampliado) | +4 | 65.51% | 82.75% |
