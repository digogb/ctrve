---
name: diff-capability
menu-code: D
description: Compare two APF counts (baseline vs current) and emit a delta report classifying functions as ADDED/CHANGED/DELETED/UNCHANGED per IFPUG enhancement count rules.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# DIFF — Delta entre Contagens APF

Esta capability compara uma contagem baseline com uma contagem atual e produz um relatorio de delta que classifica cada funcao como **ADDED / CHANGED / DELETED / UNCHANGED** conforme regras IFPUG CPM 4.3.1 de contagem de enhancement (CFP). E usada tipicamente apos uma entrega para calcular PF efetivos de manutencao.

## What Success Looks Like

1. **`{output_folder}/apf/delta-apf.md`** — Relatorio de delta com tabela classificada e totais de CFP
2. Cada funcao baseline presente no atual com mesmo ID; casadas por ID ou (nome + tipo) quando ID divergir
3. CFP calculado separando ADD, CHG, DEL (UNCHANGED nao entra)

## Inputs

- **Baseline:** `{output_folder}/apf/contagem-detalhada.md` ou outro caminho informado (versao anterior)
- **Atual:** nova contagem, ja gerada pela capability CONTAGEM

Se baseline nao existe, informar: "Nao ha contagem anterior em {output_folder}/apf/. Execute CONTAGEM primeiro para estabelecer baseline; DIFF nao se aplica a primeira entrega." Stop.

## Classificacao IFPUG Enhancement

| Classificacao | Criterio |
|---------------|----------|
| **ADDED** | Funcao presente no atual, ausente no baseline |
| **CHANGED** | Funcao presente em ambos, com DER/RLR/ALR ou complexidade alterados |
| **DELETED** | Funcao presente no baseline, ausente no atual |
| **UNCHANGED** | Funcao presente em ambos com sizing identico — nao entra no CFP |

## Passos

### Passo 1 — Carregar contagens

Ler baseline e atual. Extrair lista de funcoes com {id, name, type, der, rlr/alr, complexity, pf}.

### Passo 2 — Casamento (matching)

Primeiro tentar casar por ID exato. Para funcoes nao casadas, tentar casar por `(name + type)`. Para as que ainda restarem, tratar baseline-only como DELETED e atual-only como ADDED.

### Passo 3 — Classificar

Para cada funcao casada:
- Se `(der, rlr/alr, complexity, pf)` identicos → UNCHANGED
- Caso contrario → CHANGED (registrar delta de PF: `pf_atual - pf_baseline`)

### Passo 4 — Calcular CFP

```
CFP = soma(pf_atual) ADDED + soma(|pf_atual - pf_baseline|) CHANGED + soma(pf_baseline) DELETED
```

Nota: DELETED conta o PF da versao baseline. CHANGED conta o delta absoluto (regra conservadora — o usuario pode pedir variantes).

### Passo 5 — Escrever artefato

**`{output_folder}/apf/delta-apf.md`** — estrutura:

```
# Delta APF (Enhancement Count)

**Baseline:** {caminho-ou-versao}
**Atual:** {caminho-ou-versao}
**Data:** {data}
**Metodologia:** IFPUG CPM 4.3.1 — Enhancement Count

## Classificacao

| ID | Nome | Tipo | Status | PF Baseline | PF Atual | Delta |
|----|------|------|--------|-------------|----------|-------|
| FD-001 | Processo | ALI | UNCHANGED | 7 | 7 | 0 |
| FD-002 | Parte | ALI | CHANGED | 7 | 10 | +3 |
| FT-001 | Cadastrar | EE | UNCHANGED | 4 | 4 | 0 |
| FT-002 | Consultar | CE | ADDED | — | 4 | +4 |
| FT-003 | Listar antigo | CE | DELETED | 3 | — | -3 |

## Totais

- ADDED: X funcoes, Y PF
- CHANGED: X funcoes, Y PF (delta absoluto)
- DELETED: X funcoes, Y PF
- UNCHANGED: X funcoes (nao entra no CFP)

**CFP (Enhancement):** Z
```

## Headless Mode

If `--headless` or `-H`:
- Exit codes: 0 = delta produzido com sucesso, 1 = sem baseline ou ambiguidade de casamento nao resolvivel, 2 = erro
- Saida JSON (com `--json`): `{baseline, atual, added, changed, deleted, unchanged, cfp, delta_items}`

## Interactive Mode

- Ao encontrar funcoes nao casadas por ID mas casaveis por `(name + type)`, pedir confirmacao ao usuario
- Quando houver muitas CHANGED, oferecer: "Posso detalhar o que mudou em cada funcao? (ex: 'explique FD-002' ou 'todas')"
