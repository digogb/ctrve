---
name: count-capability
menu-code: C
description: Identify data and transactional functions, classify complexity deterministically via IFPUG matrices, compute PF brutos and adjusted PF, and produce auditable count reports.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# CONTAGEM — Contagem Detalhada APF (IFPUG CPM 4.3.1)

Esta capability produz a contagem de Pontos de Funcao de uma entrega TJCE segundo IFPUG CPM 4.3.1. Inclui fast-path para Correcao em Garantia (PF = 0). Toda funcao identificada e rastreada a US/RN; toda classificacao de complexidade passa pela matriz deterministica.

## What Success Looks Like

1. **`{output_folder}/apf/contagem-detalhada.md`** — Catalogo completo de funcoes (ALI/AIE/EE/SE/CE) com DER, RLR/ALR, complexidade, PF brutos, e referencia US/RN por funcao
2. **`{output_folder}/apf/resumo-apf.md`** — Resumo executivo: total PF brutos, fator de ajuste aplicado, PF ajustados, distribuicao por tipo de funcao, e parecer do analista
3. Toda funcao com fonte (US/RN) validada por script; zero funcoes orfas
4. Toda classificacao de complexidade derivada de matriz IFPUG via `calculate-fp.py`

## Fast-Path: Correcao em Garantia

Se o usuario declara que a tarefa e **Correcao em Garantia**, ou invoca com `garantia`:

1. Coletar: descricao curta da correcao, US/RN origem, data, responsavel
2. Nao executar contagem detalhada — por definicao contratual, Correcao em Garantia tem PF Detalhado = 0
3. Escrever diretamente ambos artefatos com conteudo minimo:

**`contagem-detalhada.md`** (cabecalho + registro unico):
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

Emitir mensagem final: "Correcao em Garantia registrada. PF = 0." Stop.

## Contagem Detalhada (fluxo normal)

### Passo 1 — Leitura e Inventario

Ler obrigatoriamente:
- `{output_folder}/requirements/user-stories.md` — fluxos de entrada/saida de dados pelo usuario
- `{output_folder}/requirements/business-rules.md` — regras que impoem validacao/processamento
- `{output_folder}/architecture/data-model.md` — entidades, atributos, relacionamentos (base para DER/RLR)

Produzir um inventario interno (nao necessariamente visivel ao usuario) de:
- Entidades candidatas a ALI (mantidas pela aplicacao) ou AIE (mantidas externamente, referenciadas)
- Casos de uso candidatos a EE (entrada que mantem ALI), SE (saida processada), CE (consulta sem processamento derivado)

### Passo 2 — Classificacao de Funcoes de Dados

Para cada entidade logica:

- **ALI (Arquivo Logico Interno):** mantida pela aplicacao em contagem. Requer pelo menos uma transacao (EE) que a mantenha.
- **AIE (Arquivo de Interface Externa):** referenciada pela aplicacao mas mantida por outra aplicacao. Nunca mantida pela aplicacao em contagem.

Para cada ALI/AIE, determinar:
- **DER (Data Element Types):** atributos unicos nao-recursivos da entidade visiveis ao usuario
- **RLR (Record Element Types):** subgrupos logicos (entidade principal + subtipos/fracoes)

Passar para `calculate-fp.py` com tipo `ALI` ou `AIE` para obter complexidade e PF.

**Regra anti-duplicacao:** cada entidade logica aparece uma unica vez no catalogo, mesmo que referenciada por N transacoes.

### Passo 3 — Classificacao de Funcoes Transacionais

Para cada caso de uso no user-stories:

- **EE (Entrada Externa):** processo elementar que mantem ao menos um ALI (CRUD, import, alteracao de estado)
- **SE (Saida Externa):** processo elementar que apresenta dados ao usuario com calculo, derivacao, ou logica adicional (relatorios, totais, graficos calculados)
- **CE (Consulta Externa):** processo elementar que apresenta dados sem calculo/derivacao (listagens simples, buscas, visualizacoes)

Para cada transacao, determinar:
- **DER:** campos de entrada + campos de saida + mensagens visiveis (botoes/acoes contam como 1 DER coletivo)
- **ALR (Arquivos Logicos Referenciados):** numero de ALI/AIE tocados pela transacao

Passar para `calculate-fp.py` com tipo `EE`, `SE`, ou `CE`.

### Passo 4 — Calculo via Script

```bash
python3 scripts/calculate-fp.py --type ALI --der 15 --rlr 2
python3 scripts/calculate-fp.py --type EE --der 8 --alr 2
# etc. para cada funcao
```

O script retorna: complexidade (Baixa/Media/Alta) e PF segundo matriz IFPUG CPM 4.3.1. Registrar no catalogo.

**Regra:** nao inventar PF. Se `calculate-fp.py` nao pode ser executado, pedir ao usuario que rode localmente e cole o resultado.

### Passo 5 — Validacao de Fontes

Toda funcao no catalogo precisa referenciar pelo menos uma US ou RN existente. Executar:

```bash
python3 scripts/validate-fp-sources.py {output_folder}/apf/contagem-detalhada.md {output_folder}/requirements/user-stories.md {output_folder}/requirements/business-rules.md
```

Se houver funcoes orfas (fonte inexistente) ou funcoes sem fonte declarada: bloqueio. Corrigir antes de prosseguir.

### Passo 6 — PF Brutos e Ajuste

Somar PF de todas as funcoes = **PF Brutos**.

Aplicar **Fator de Ajuste (VAF)** segundo as 14 Caracteristicas Gerais do Sistema IFPUG (TDI — Total Degree of Influence):

```
VAF = (TDI * 0.01) + 0.65
PF Ajustado = PF Brutos * VAF
```

VAF varia de 0.65 (TDI=0) a 1.35 (TDI=70). Se o usuario nao fornece TDI, pedir avaliacao das 14 caracteristicas (ou usar VAF = 1.00 como neutro com registro explicito da decisao).

### Passo 7 — Escrever Artefatos

**`{output_folder}/apf/contagem-detalhada.md`** — estrutura:

```
# Contagem Detalhada APF

**Projeto/Entrega:** {nome}
**Data:** {data}
**Metodologia:** IFPUG CPM 4.3.1
**Responsavel:** {nome do analista ou agente}

## Funcoes de Dados

| ID | Nome | Tipo | DER | RLR | Complexidade | PF | Fonte (US/RN) |
|----|------|------|-----|-----|--------------|----|---------------| 
| FD-001 | Processo | ALI | 15 | 2 | Baixa | 7 | US-003, RN-001 |
| ...

## Funcoes Transacionais

| ID | Nome | Tipo | DER | ALR | Complexidade | PF | Fonte (US/RN) |
|----|------|------|-----|-----|--------------|----|---------------| 
| FT-001 | Cadastrar processo | EE | 12 | 2 | Media | 4 | US-003, RN-002 |
| ...

## Subtotais

- ALI: X funcoes, Y PF
- AIE: X funcoes, Y PF
- EE: X funcoes, Y PF
- SE: X funcoes, Y PF
- CE: X funcoes, Y PF

**PF Brutos:** Z
```

**`{output_folder}/apf/resumo-apf.md`** — estrutura:

```
# Resumo APF

**Projeto/Entrega:** {nome}
**Data:** {data}

## Resultado

| Metrica | Valor |
|---------|-------|
| PF Brutos | Z |
| TDI | N |
| VAF | 0.NN |
| **PF Ajustado** | **ZZ** |

## Distribuicao por Tipo

| Tipo | Qtde | PF | % |
|------|------|----|---|
| ALI | X | Y | Z% |
| ... | ... | ... | ... |

## Parecer do Analista

{observacoes sobre complexidade predominante, funcoes de risco, pressupostos adotados, lacunas identificadas}
```

## Headless Mode

If `--headless` or `-H`:
- Execute all steps sequentially without user interaction
- For missing TDI, use VAF = 1.00 and mark the resumo with `**VAF NEUTRO APLICADO — TDI nao fornecido em modo headless**`
- For functions where DER/RLR/ALR cannot be deterministically inferred, mark `**CLASSIFICACAO PENDENTE**` in the detailed count and exit 1
- Exit with structured JSON summary when `--json` is passed: total PF brutos, PF ajustado, VAF, contagem por tipo, quantidade de pendentes, is_garantia

## Interactive Mode

- Mostrar o raciocinio funcao por funcao ao usuario quando ele pedir "explique esta contagem"
- Pausar para confirmacao antes de escrever artefatos finais quando houver mais de 3 classificacoes ambiguas
- Sempre citar matriz IFPUG ao apresentar uma complexidade: "EE com 8 DER e 2 ALR cai em Media segundo matriz IFPUG CPM 4.3.1 Tabela 7.2"
