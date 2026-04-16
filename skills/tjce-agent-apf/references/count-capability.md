---
name: count-capability
menu-code: C
description: Identify data and transactional functions, classify complexity via IFPUG matrices, compute PF brutos / PF ajustado / CFP, and produce auditable count reports. Supports nova, enhancement, garantia and Lote Direto modes.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and the runtime flags (`--tipo`, `--tdi`, `--functions-json`, `--project`, `--delivery`, `--responsible`) are resolved by the parent SKILL.md at activation time.

# CONTAGEM — Contagem Detalhada APF (IFPUG CPM 4.3.1)

Esta capability produz a contagem de Pontos de Funcao de uma entrega TJCE. Atende tres cenarios:

- **nova** — primeira entrega; conta todas as funcoes
- **enhancement** — manutencao; classifica funcoes como ADDED/CHANGED/DELETED/UNCHANGED contra baseline e computa CFP
- **garantia** — fast-path contratual: PF = 0

E suporta um **Lote Direto** (Expert Path) quando o usuario ja tem o inventario pronto.

## What Success Looks Like

1. **`{output_folder}/apf/contagem-detalhada.md`** — Catalogo completo de funcoes com DER, RLR/ALR, complexidade, PF brutos, referencia US/RN, e status (para enhancement)
2. **`{output_folder}/apf/resumo-apf.md`** — Resumo: total PF brutos, VAF/TDI, PF ajustados, distribuicao por tipo (para enhancement, tambem CFP), parecer do analista
3. Toda funcao com fonte (US/RN) validada por `validate-fp-sources.py`; zero orfas
4. Toda classificacao de complexidade e agregacao produzida por scripts (`calculate-fp.py --batch`, `aggregate-fp.py`)

## Fast-Path: Correcao em Garantia

Se o intent e **garantia**:

1. Coletar: descricao curta da correcao, US/RN origem, data, responsavel
2. Escrever artefatos minimos sem contagem:

**`contagem-detalhada.md`** (registro unico):
```
# Contagem Detalhada APF — Correcao em Garantia

**Tipo:** Correcao em Garantia
**Data:** {data}
**US/RN origem:** {referencia}
**Descricao:** {descricao}
**PF Detalhado:** 0 (por definicao contratual)
```

**`resumo-apf.md`** (equivalente):
```
# Resumo APF — Correcao em Garantia

Esta entrega foi classificada como **Correcao em Garantia** da entrega referenciada.
PF Detalhado = **0**. Nao ha contagem detalhada aplicavel.
```

Emitir: *"Correcao em Garantia registrada. PF = 0."* Stop.

## Lote Direto (Expert Path)

Se `--functions-json <path>` foi passado ou o usuario forneceu o inventario:

1. Ler o JSON: `[{id, name, type, der, rlr?|alr?, source, ...}]`
2. Executar `calculate-fp.py --batch <path> --json > /tmp/fns-classified.json`
3. Pular direto para **Passo 5 (Validacao)** e seguir para **Passo 6/7**

Nao e necessario reler requirements — a fonte ja vem declarada no JSON.

## Contagem Detalhada (fluxo nova / enhancement)

### Passo 1 — Ingestao (ou use o pre-pass)

Opcao A — Pre-pass deterministico (recomendado em headless):
```bash
python3 scripts/extract-fp-candidates.py {output_folder}/requirements \
  --data-model {output_folder}/architecture/data-model.md \
  -o /tmp/apf-candidates.json
```

Opcao B — Leitura direta: ler `user-stories.md`, `business-rules.md`, `data-model.md` e montar inventario mental.

Em **enhancement**, ler tambem `{output_folder}/apf/contagem-detalhada.md` (baseline) para saber funcoes preexistentes.

### Passo 2 — Classificacao de Funcoes de Dados (ALI/AIE)

Para cada entidade logica:
- **ALI:** mantida pela aplicacao. Requer ao menos uma EE que a mantenha.
- **AIE:** referenciada mas mantida externamente.

Para cada uma, determinar DER (atributos unicos nao-recursivos visiveis ao usuario; relacionamentos = 1 DER) e RLR (subgrupos logicos; default 1).

**Regra anti-duplicacao:** cada entidade aparece uma unica vez, mesmo que referenciada por N transacoes.

Duvidas sobre terminologia → consultar `references/glossario-ifpug.md`.

### Passo 3 — Classificacao de Funcoes Transacionais (EE/SE/CE)

Para cada caso de uso:
- **EE:** mantem ALI (CRUD, import, mudanca de estado)
- **SE:** apresenta dados com calculo/derivacao
- **CE:** apresenta dados sem calculo

Determinar DER (entrada + saida + mensagens) e ALR (ALI/AIE tocados).

### Passo 4 — Calculo em Lote

Montar um unico JSON com todas as funcoes classificadas e invocar o batch:

```bash
cat > /tmp/apf-functions.json <<EOF
[
  {"id": "FD-001", "name": "Processo", "type": "ALI", "der": 15, "rlr": 2, "source": "US-003, RN-001"},
  {"id": "FT-001", "name": "Cadastrar processo", "type": "EE", "der": 12, "alr": 2, "source": "US-003, RN-002"}
]
EOF
python3 scripts/calculate-fp.py --batch /tmp/apf-functions.json --json > /tmp/apf-classified.json
```

Resultado contem complexidade e PF de cada funcao, com metadata preservada.

**Nunca inventar PF.** Se scripts nao puderem rodar, pedir ao usuario que execute localmente e cole o resultado.

### Passo 5 — Validacao de Fontes

```bash
python3 scripts/validate-fp-sources.py {output_folder}/apf/contagem-detalhada.md \
  {output_folder}/requirements/user-stories.md \
  {output_folder}/requirements/business-rules.md
```

Funcoes orfas ou sem fonte → bloqueio. Corrigir antes de prosseguir. Em headless, ainda escrever o artefato mas marcar orfas e sair com exit 1.

### Passo 6 — Agregacao via Script

```bash
python3 scripts/aggregate-fp.py /tmp/apf-classified.json --tdi <N> --json > /tmp/apf-agg.json
python3 scripts/aggregate-fp.py /tmp/apf-classified.json --tdi <N> --markdown > /tmp/apf-resumo-body.md
```

- **TDI:** se usuario forneceu via `--tdi`, usar. Caso contrario em modo interativo, oferecer o checklist de `references/gsc-14-characteristics.md` ou TDI neutro = 35. Em headless, usar 35 e marcar no resumo.
- O script computa VAF, PF Ajustado, distribuicao e protege contra aritmetica LLM errada.

### Passo 7 — Escrever Artefatos

**`{output_folder}/apf/contagem-detalhada.md`** — cabecalho com `--project`/`--delivery`/`--responsible` + duas tabelas (Funcoes de Dados, Funcoes Transacionais). Para **enhancement**, adicionar coluna `Status` (ADDED/CHANGED/DELETED/UNCHANGED).

**`{output_folder}/apf/resumo-apf.md`** — cabecalho + corpo markdown produzido pelo aggregate + "Parecer do Analista" em prosa curta (complexidade predominante, funcoes de risco, pressupostos, lacunas). Em **enhancement**, incluir linha `CFP: N` apos a tabela de metricas.

Estrutura detalhada dos artefatos esta em `references/exemplo-contagem-tjce.md`.

## Modo Enhancement — especifico

Em enhancement, alem do fluxo normal, marcar status de cada funcao comparando contra baseline:

- **ADDED** — nao existia no baseline
- **CHANGED** — existia mas DER/RLR/ALR/complexidade mudaram
- **DELETED** — existia no baseline, nao esta no atual
- **UNCHANGED** — igual ao baseline (nao entra no CFP)

**CFP = soma(PF ADDED) + soma(|delta PF| CHANGED) + soma(PF_baseline DELETED)**

Registrar CFP no resumo como metrica principal da entrega de manutencao.

Alternativa: se as duas contagens ja existem, use a capability **DIFF** (ver `references/diff-capability.md`).

## Headless Mode

If `--headless` or `-H`:
- Resolve args via SKILL.md ordering
- Em Lote Direto (`--functions-json`), pular ingestao
- TDI padrao 35 com marca; pendencias → exit 1; orfas → exit 1
- Emitir JSON conforme schema em SKILL.md quando `--json` presente
- Nao prompt; nao oferecer explain-on-demand

## Interactive Mode

- Mostrar o raciocinio funcao por funcao quando pedido
- Pausar para confirmacao antes de escrever artefatos finais se houver >3 classificacoes ambiguas
- Citar matriz IFPUG ao apresentar complexidade: "EE com 8 DER e 2 ALR cai em Media segundo matriz IFPUG CPM 4.3.1"
- Ao concluir: emitir convite explicito *"Quer que eu explique alguma funcao? (ex: 'FT-001' ou 'todas')"*
