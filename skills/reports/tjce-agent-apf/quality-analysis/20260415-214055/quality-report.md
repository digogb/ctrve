# BMad Method · Analise de Qualidade: tjce-agent-apf

**Analista de Pontos de Funcao TJCE** — Analista de metricas IFPUG CPM 4.3.1
**Analisado:** 2026-04-15 21:40:55 | **Path:** /home/rodgb/projetos/ctrve/skills/tjce-agent-apf
**Relatorio interativo:** quality-report.html

## Retrato do Agente

O `tjce-agent-apf` e um analista de metricas preciso e tecnico que trata cada ponto de funcao como compromisso contratual. Fala em vocabulario IFPUG puro (ALI/AIE/EE/SE/CE, DER/RLR/ALR), mostra o raciocinio passo a passo ("ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF"), e recusa-se a arbitrar complexidade: a matriz CPM 4.3.1 vive em `calculate-fp.py`, nunca na cabeca do LLM. Uma persona de rastreabilidade absoluta, ancorada por scripts que impedem funcoes orfas.

## Capacidades

| Capacidade | Status | Observacoes |
| --- | --- | --- |
| CONTAGEM — Contagem Detalhada APF (com fast-path Garantia) | Boa | 2 observacoes de baixa severidade |

## Avaliacao

**Boa** — Agente single-capability excepcionalmente coeso: persona, capacidade e scripts formam um triade raro em que a insistencia em determinismo nao e apenas discurso — ela esta operacionalizada em `calculate-fp.py` e `validate-fp-sources.py`. A maior oportunidade e adicionar o modo **Enhancement Count (CFP)**, cenario TJCE dominante que hoje e tratado como contagem nova, inflando PF.

## O que esta quebrado

Nenhum problema critico ou alto de defeito. O ambiente local nao possui `uv` na PATH, o que impediu a execucao do ruff nos scripts Python — e uma limitacao de ambiente, nao do agente.

## Oportunidades

### 1. Cobertura de cenarios TJCE incompleta (Alta — 4 observacoes)

O agente so modela "contagem nova" e "Correcao em Garantia". Entregas TJCE reais sao majoritariamente incrementais (enhancement count / CFP), frequentemente envolvem delta contra contagem anterior, e o gestor de metricas precisa de recontagens apos mudanca de escopo. Tratar enhancement como contagem nova **infla PF** — risco de integridade contratual.

- **Acao:** Introduzir sub-rota `enhancement` (ou `--tipo enhancement`) que exige `contagem-detalhada.md` de baseline, marca funcoes como ADDED/CHANGED/DELETED/UNCHANGED e computa CFP conforme CPM 4.3.1. Pareadamente, adicionar capacidade `DIFF` que compara duas contagens e emite `delta-apf.md`.
- **Impacto:** Eleva a cobertura real do agente no dominio TJCE; evita litigios contratuais por super-contagem.

Observacoes associadas:
- `enhancement-opportunities:H1` — Missing Enhancement Count mode (CFP).
- `enhancement-opportunities:H4` — Delta contra contagem anterior nao suportado.
- `agent-cohesion:Finding 1` — Missing recontagem / update path.
- `agent-cohesion:Finding 4` — Sem export para formato de submissao contratual.

### 2. Funil de entrada rigido — falta roteamento de intencao (Alta — 3 observacoes)

O `On Activation` verifica pre-requisitos antes de entender o que o usuario quer. Um usuario de Garantia e forcado pelo gate (que depois e relaxado), e especialistas que ja tem o inventario mental precisam aguardar leitura sequencial de tres artefatos.

- **Acao:** Reordenar ativacao para **intent-before-ingestion**: saudacao → pergunta "contagem nova, enhancement ou correcao em garantia?" → aplicar pre-requisitos especificos da rota. Adicionar modo **Lote Direto** que aceita JSON/tabela `{nome, tipo, der, rlr/alr, fonte}` e pula os Passos 1-3.
- **Impacto:** Remove friccao para experts e elimina caminhos mortos para o primeiro interlocutor.

Observacoes associadas:
- `enhancement-opportunities:H3` — Intent-before-ingestion violado.
- `enhancement-opportunities:H2` — Sem modo "paste function inventory" para expert.
- `enhancement-opportunities:M7` — Recovery de pre-requisitos e dead-end.

### 3. Contrato headless incompleto — entrada e schema abertos (Media — 4 observacoes)

O headless esta 80% pronto (exit codes, ambiguidade -> PENDENTE, Garantia). Mas: o schema JSON de saida nao esta fixado, nao ha flags para `--project`, `--delivery`, `--responsible`, `--tdi`, nao se pode injetar `--functions-json` e os placeholders dos templates (`{nome}`, `{data}`, `{responsavel}`) nao tem regra de resolucao.

- **Acao:** Pinar schema JSON inline no SKILL.md (ou em `references/apf-headless-schema.json`), adicionar flags CLI e definir ordem de resolucao args > config > prompt > defaults. Expor `--functions-json` e `--tdi N`. Incluir `pending_count` e `pf_at_risk` no topo do JSON.
- **Impacto:** Torna o agente um primitivo componivel para outras skills TJCE e pipelines CI/CD.

Observacoes associadas:
- `structure:Low` — Schema JSON do `--json` nao especificado em SKILL.md.
- `enhancement-opportunities:L2` — Schema headless nao pinado.
- `enhancement-opportunities:L3` — Placeholders sem regra de resolucao.
- `agent-cohesion:Finding 3` — Headless ambiguity pode under-contar se consumidor ignorar exit 1.

### 4. Trabalho deterministico ainda no prompt (Media — 3 observacoes)

Aritmetica VAF/PF Ajustado, leitura integral de tres artefatos MD e invocacao serial do `calculate-fp.py` por funcao deixam determinismo e tokens na mesa. LLMs notoriamente errar ponto flutuante — essa matematica nao deveria existir no prompt.

- **Acao:** Criar `scripts/aggregate-fp.py` (VAF, PF Brutos, PF Ajustado, distribuicao por tipo, opcionalmente `--markdown`). Criar pre-pass `scripts/extract-fp-candidates.py` que parseia `data-model.md`, `user-stories.md` e `business-rules.md` em JSON compacto. Extender `calculate-fp.py` com `--batch functions.json` para uma unica invocacao em vez de N.
- **Impacto:** ~1.000–2.400 tokens economizados por contagem, aritmetica livre de erro, latencia menor.

Observacoes associadas:
- `script-opportunities:Finding 2` — Inventario de requisitos feito no prompt (pre-pass possivel).
- `script-opportunities:Finding 1` — Aritmetica VAF/agregacoes no prompt.
- `execution-efficiency:Finding 2` — `calculate-fp.py` invocado N vezes sequencialmente.

### 5. Onboarding e UX de novato ausentes (Media — 4 observacoes)

Nao ha glossario IFPUG, nao ha exemplo resolvido, TDI exige lembrar as 14 GSC sem checklist, e o convite "explique esta contagem" existe mas nao e descoberto pelo usuario. O principio "Pergunte, nao assuma" nao se engaja cedo o bastante para ajudar o primeiro interlocutor.

- **Acao:** Adicionar `references/glossario-ifpug.md` (DER, RLR, ALR, ALI/AIE/EE/SE/CE em PT com exemplos TJCE), `references/gsc-14-characteristics.md` (checklist 0-5 com descricoes contextuais TJCE), `references/exemplo-contagem-tjce.md` (sprint resolvida). Ao terminar contagem, emitir convite explicito "Quer que eu explique alguma funcao? (ex: FT-001 ou 'todas')".
- **Impacto:** Transforma a experiencia do primeiro interlocutor e reduz dependencia de documentacao IFPUG externa.

Observacoes associadas:
- `enhancement-opportunities:M3` — Sem glossario ou exemplo para newcomers.
- `enhancement-opportunities:M5` — Elicitacao TDI sem formulario estruturado.
- `enhancement-opportunities:M1` — Explain-on-demand nao descoberto.
- `agent-cohesion:Finding 2` — Sem referencia GSC/TDI (14 caracteristicas).

## Pontos Fortes (preservar)

- **Espelho persona-ferramenta:** determinismo nao e discurso — `calculate-fp.py` executa a matriz, `validate-fp-sources.py` bloqueia orfas. Raro nivel de coerencia.
- **Mission statement (SKILL.md:14):** "Toda funcionalidade entregue tem sua medida em Pontos de Funcao auditavel, rastreavel a requisito, e classificada deterministicamente segundo IFPUG" — DNA load-bearing.
- **Principios tangiveis (4):** Determinismo IFPUG, Rastreabilidade total, Nao contar em dobro, Pergunte nao assuma — cada um mapeia uma acao testavel.
- **Exemplo de estilo de comunicacao:** "ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF" ensina formato de saida em uma linha.
- **Fast-path Garantia:** short-circuit contratual limpo, PF=0 trivial, sem ceremonia.
- **Prerequisite Check com fallback graduado:** hard-stop para US/RN, soft-stop negociavel para data-model.
- **Delegacao externa disciplinada:** encaminha ao `tjce-agent-requirements` em vez de reimplementar elicitacao de requisitos.
- **Stateless single-capability:** escopo honestamente estreito, sem redundancia, sem memoria desnecessaria.

## Analise Detalhada

### Estrutura e Capacidades

Estruturalmente sao — todas as secoes obrigatorias presentes, frontmatter valido, capacidade unica bem-formada com config-header, Success Criteria, fast-path, 7 passos, Headless Mode e Interactive Mode. Nenhum problema critico. O pre-pass sinaliza ausencia de palavra-chave de progressao em `count-capability.md:205` — provavelmente falso-positivo, pois o fluxo usa "Passo 1..7", condicionais fast-path e contrato de exit codes.

### Persona e Voz

Agente stateless, single-capability, dominio-especialista. Overview forte (7 linhas), Identity e Communication Style concretos com exemplos IFPUG, Principles observaveis, progressive disclosure correta (SKILL 74 linhas / 1.261 tokens, capacidade 205 linhas / 2.011 tokens). Sem waste, sem back-references, sem wall-of-text. Gap minor: ausencia de sinal explicito de progressao/completion em modo interativo.

### Coesao de Identidade

Tightly cohered single-purpose specialist. Persona, capacidade e scripts formam triade raro. Principios declarados tem mecanismo concreto (determinismo -> script de matriz; rastreabilidade -> script de orfas; nao-duplicacao -> regra anti-duplicacao no Passo 2; pergunte-nao-assuma -> path de ambiguidade). Gap moderado: vizinhos naturais de APF ausentes — recontagem, diff, indicativa NESMA, export contratual.

### Eficiencia de Execucao

Pre-pass com zero issues de dependencia. Oportunidades: batelar checks de pre-requisitos em uma unica leitura paralela; batelar invocacoes de `calculate-fp.py` em um unico call (via `--batch` ou heredoc); paralelizar raciocinio dos Passos 2 e 3 (independentes); usar `{skill-root}/scripts/...` em vez de caminhos relativos.

### Experiencia de Conversacao

**Jornadas:**
- *First-Timer:* entrada seca, sem glossario, saida sem "o que fazer com esses numeros".
- *Expert:* forcado pela ingestao de 3 arquivos sem modo lote; `calculate-fp.py` direto e a escapatoria.
- *Confused:* gate hard para pre-requisitos, sem soft-gate de intencao.
- *Edge-Case:* entrega mista Garantia+nova nao modelada; enhancement count ausente; cross-system ALI/AIE sem desempate.
- *Hostile Environment:* trata `python3` ausente; nao trata `data-model.md` vazio nem `user-stories.md` malformado.
- *Automator:* 70% pronto; faltam flags e schema fixo.

**Autonomo:** `easily-adaptable` — falta pinar schema JSON de saida e expor flags de contexto (`--project`, `--delivery`, `--tdi`, `--functions-json`).

### Oportunidades de Script

Intelligence placement ja forte — matriz IFPUG e source cross-reference estao em scripts com exit codes e `--json`. Oportunidades remanescentes: pre-pass `extract-fp-candidates.py` (800–2.000+ tokens), `aggregate-fp.py` para VAF/totais/markdown (150–250 tokens + correcao de ponto flutuante), `validate-apf-artifacts.py` como gate estrutural. Savings agregados estimados em 1.000–2.400 tokens por contagem completa.

## Recomendacoes

1. **Introduzir Enhancement Count (CFP) + capacidade DIFF.** Resolve 4 observacoes e elimina o maior risco contratual do agente. Esforco: medio.
2. **Reordenar ativacao para intent-before-ingestion e adicionar modo Lote Direto.** Resolve 3 observacoes, transforma a experiencia de expert e primeiro interlocutor. Esforco: baixo.
3. **Pinar contrato headless (schema JSON, flags CLI, `--functions-json`).** Resolve 4 observacoes e torna o agente primitivo componivel. Esforco: baixo.
4. **Criar `aggregate-fp.py` e pre-pass `extract-fp-candidates.py`; adicionar `--batch` em `calculate-fp.py`.** Resolve 3 observacoes, economiza tokens e elimina aritmetica LLM. Esforco: medio.
5. **Adicionar `references/glossario-ifpug.md`, `gsc-14-characteristics.md`, `exemplo-contagem-tjce.md` e convite explain-on-demand.** Resolve 4 observacoes, resolve UX de novato. Esforco: baixo.
