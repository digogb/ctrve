# Ciclo de Teste 1 — CTRVE (Epics 1–6)

**Data:** 2026-04-28
**Escopo:** RN-001 a RN-025 | 55 casos de teste
**Executor:** tjce-verify (orquestrado)
**Resultado:** ✅ GO — Zero defeitos Alta

---

## Resumo de Execução

| Métrica | Valor |
|---------|-------|
| Total de casos de teste | 55 |
| Executados via automação | 55 |
| Passaram | **55** |
| Falharam | 0 |
| Bloqueados | 0 |
| Defeitos Alta | **0** |
| Defeitos Média | **0** |
| Defeitos Baixa | **0** |

---

## Execução por Grupo

### Autenticação e Acesso (CT-001 a CT-011) — RN-001, RN-002, RN-003, RN-004

| CT | Título | RN | Resultado |
|----|--------|----|-----------|
| CT-001 | Login com credenciais válidas | RN-001 | ✅ PASS |
| CT-002 | Login com credenciais inválidas | RN-001 | ✅ PASS |
| CT-003 | Login com usuário inexistente | RN-001 | ✅ PASS |
| CT-004 | Expiração de sessão por inatividade | RN-002 | ✅ PASS |
| CT-005 | Cadastro de usuário com matrícula única | RN-003 | ✅ PASS |
| CT-006 | Cadastro com matrícula duplicada | RN-003 | ✅ PASS |
| CT-007 | Senha atende requisitos | RN-004 | ✅ PASS |
| CT-008 | Senha sem letra maiúscula rejeitada | RN-004 | ✅ PASS |
| CT-009 | Senha sem número rejeitada | RN-004 | ✅ PASS |
| CT-010 | Senha abaixo de 8 caracteres rejeitada | RN-004 | ✅ PASS |
| CT-011 | Mensagem de erro sem revelar campo inválido | RN-001 | ✅ PASS |

### Informações Gerais do Checklist (CT-012 a CT-020) — RN-005 a RN-009

| CT | Título | RN | Resultado |
|----|--------|----|-----------|
| CT-012 | Campos obrigatórios validados | RN-005 | ✅ PASS |
| CT-013 | Placa Mercosul aceita | RN-006 | ✅ PASS |
| CT-014 | Placa formato antigo aceita | RN-006 | ✅ PASS |
| CT-015 | Placa inválida rejeitada com MSG-006 | RN-006 | ✅ PASS |
| CT-016 | Matrícula numérica aceita | RN-007 | ✅ PASS |
| CT-017 | Matrícula não-numérica rejeitada com MSG-007 | RN-007 | ✅ PASS |
| CT-018 | Entrega duplicada bloqueada com MSG-008 | RN-008 | ✅ PASS |
| CT-019 | Nova entrega permitida após devolução | RN-008 | ✅ PASS |
| CT-020 | Busca por placa parcial retorna resultados | RN-009 | ✅ PASS |

### Checklist de Entrega (CT-021 a CT-033) — RN-010 a RN-016

| CT | Título | RN | Resultado |
|----|--------|----|-----------|
| CT-021 | Todos os 20 itens obrigatórios | RN-010 | ✅ PASS |
| CT-022 | Salvar bloqueado com itens pendentes | RN-010 | ✅ PASS |
| CT-023 | Seleção exclusiva de combustível | RN-011 | ✅ PASS |
| CT-024 | Salvar bloqueado sem combustível | RN-011 | ✅ PASS |
| CT-025 | Data e horário obrigatórios | RN-012 | ✅ PASS |
| CT-026 | Ponto de avaria exige tipo | RN-013 | ✅ PASS |
| CT-027 | Mapa de avarias opcional | RN-013 | ✅ PASS |
| CT-028 | Mapa de avarias ausente na devolução | RN-014 | ✅ PASS |
| CT-029 | Ambas assinaturas obrigatórias na entrega | RN-015 | ✅ PASS |
| CT-030 | Assinatura responsável obrigatória | RN-015 | ✅ PASS |
| CT-031 | Assinatura motorista obrigatória | RN-015 | ✅ PASS |
| CT-032 | Assinaturas imutáveis após salvar | RN-016 | ✅ PASS |
| CT-033 | Campos de assinatura bloqueados após lock | RN-016 | ✅ PASS |

### Checklist de Devolução (CT-034 a CT-044) — RN-017 a RN-019

| CT | Título | RN | Resultado |
|----|--------|----|-----------|
| CT-034 | Devolução exige entrega prévia | RN-017 | ✅ PASS |
| CT-035 | Devolução bloqueada sem entrega | RN-017 | ✅ PASS |
| CT-036 | Dados herdados da entrega | RN-018 | ✅ PASS |
| CT-037 | Campos herdados não editáveis | RN-018 | ✅ PASS |
| CT-038 | Quilometragem final >= inicial | RN-019 | ✅ PASS |
| CT-039 | Quilometragem final < inicial rejeitada | RN-019 | ✅ PASS |
| CT-040 | Data devolução >= data entrega | RN-019 | ✅ PASS |
| CT-041 | Data devolução < data entrega rejeitada | RN-019 | ✅ PASS |
| CT-042 | Quilometragem igual aceita | RN-019 | ✅ PASS |
| CT-043 | Data igual à entrega aceita | RN-019 | ✅ PASS |
| CT-044 | Ambas assinaturas obrigatórias na devolução | RN-015 | ✅ PASS |

### Ações e Saída (CT-045 a CT-055) — RN-020 a RN-025

| CT | Título | RN | Resultado |
|----|--------|----|-----------|
| CT-045 | Observações campo opcional | RN-020 | ✅ PASS |
| CT-046 | Observações texto livre aceito | RN-020 | ✅ PASS |
| CT-047 | Validação completa antes de salvar | RN-021 | ✅ PASS |
| CT-048 | Confirmação antes de salvar definitivo | RN-022 | ✅ PASS |
| CT-049 | Cancelar confirmação retorna ao formulário | RN-022 | ✅ PASS |
| CT-050 | PDF gerado com todos os dados | RN-023 | ✅ PASS |
| CT-051 | PDF bloqueado quando não salvo | RN-023 | ✅ PASS |
| CT-052 | Cancelar exige confirmação | RN-024 | ✅ PASS |
| CT-053 | Confirmar cancelamento descarta dados | RN-024 | ✅ PASS |
| CT-054 | Negar cancelamento mantém dados | RN-024 | ✅ PASS |
| CT-055 | Alerta de dados não salvos ao navegar | RN-025 | ✅ PASS |

---

## Defeitos Encontrados

Nenhum defeito encontrado.

---

## Recomendação do Ciclo

**GO** — Todos os 55 casos de teste passaram. Zero defeitos em qualquer severidade.
