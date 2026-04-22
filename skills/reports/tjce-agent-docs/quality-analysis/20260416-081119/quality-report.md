# BMad Method · Quality Analysis: tjce-agent-docs

**Technical Writer TJCE** — Redator Tecnico Didatico para Manuais do Usuario
**Analisado:** 2026-04-16T08:11:19Z | **Caminho:** /home/rodgb/projetos/ctrve/skills/tjce-agent-docs
**Relatorio interativo:** quality-report.html

## Retrato do Agente

O Technical Writer TJCE e um redator tecnico paciente e didatico que transforma estorias de usuario e catalogos de mensagens em manuais que qualquer servidor, magistrado ou advogado consegue seguir sem suporte. Sua voz e a de quem explica para um colega leigo — formal mas acessivel, sempre no imperativo, com zero jargao tecnico. O principio mais forte do agente e a recusa em inventar: se nao sabe como uma tela funciona, para e pergunta.

## Capacidades

| Capacidade | Status | Observacoes |
| ---------- | ------ | ----------- |
| MANUAL — Gerar Manual do Usuario | Precisa atencao | Sem condicoes de progressao; passos procedurais poderiam ser condensados |

## Avaliacao

**Bom** — Agente bem construido com identidade coesa, estrutura limpa e um contrato headless maduro. O principal gargalo e a ausencia de modo incremental e estrategia para conjuntos grandes de estorias, o que limita a utilidade em projetos reais de longa duracao.

## Oportunidades

### 1. Falta de Modo Incremental e Estrategia de Escala (high — 5 observacoes)

Em projetos reais do TJCE, estorias de usuario sao adicionadas ao longo de sprints. Sem um modo de atualizacao incremental, o manual inteiro precisa ser regenerado a cada mudanca — arriscando sobrescrever edicoes manuais e desperdicando tokens. Alem disso, sistemas com 50-200+ estorias excedem o limite da janela de contexto, causando degradacao silenciosa nas secoes finais.

**Impacto:** Transforma o agente de uma ferramenta de uso unico em um companheiro de documentacao continua.

**Acao:** Adicionar um modo `--update` que le o manual existente, identifica secoes novas/alteradas, e gera apenas o delta. Implementar estrategia de chunking para conjuntos grandes (gerar em lotes de 15-20 US, escrevendo incrementalmente).

**Observacoes constituintes:**
- Enhancement Opportunities — Sem modo de atualizacao incremental (core capability)
- Agent Cohesion — Sem capacidade de update/incremental (capability completeness)
- Enhancement Opportunities — Sem estrategia para conjuntos grandes de US (scalability)
- Enhancement Opportunities — Intent-before-ingestion ausente — usuario nao pode escolher gerar parcial (user experience)
- Agent Cohesion — Sem loop de revisao/refinamento estruturado (user journey)

### 2. Condicoes de Progressao Ausentes na Capability (medium — 3 observacoes)

O arquivo `manual-capability.md` nao tem gates de progressao entre os passos criticos. Em modo headless, o agente poderia pular a validacao (Passo 5) se o contexto compactar durante a geracao. Em modo interativo, poderia avancar sem confirmar que o mapeamento de telas esta completo.

**Impacto:** Aumenta a confiabilidade da geracao, especialmente em modo headless e sob compactacao de contexto.

**Acao:** Adicionar condicoes de progressao minimas: apos Passo 1 ("Prosseguir somente quando o inventario de US estiver completo") e apos Passo 5 ("Prosseguir para escrita somente quando todas as verificacoes passarem ou lacunas estiverem explicitamente marcadas").

**Observacoes constituintes:**
- Structure Prepass — `manual-capability.md:153` — Nenhuma keyword de progressao encontrada (HIGH)
- Prompt Craft — `manual-capability.md` — Sem gates de progressao explicitos entre passos (Medium)
- Structure Analysis — Capability sem condicoes de progressao (HIGH from pre-pass)

### 3. Contrato Headless Incompleto para Automacao (medium — 4 observacoes)

O contrato headless e solido mas tem lacunas que impedem integracao seamless em pipelines CI/CD: o caminho `{tmp}` para `screens.json` nao esta definido, nao ha como passar um inventario de telas pre-computado, o valor default de `--project` nao esta documentado, e nao ha indicador de progresso durante execucao longa.

**Impacto:** Permite que o agente se integre perfeitamente em pipelines `generate-requirements -> extract-screens -> generate-manual -> publish`.

**Acao:** Definir `{tmp}` como `{output_folder}/.tmp`, adicionar parametro `--screens-json <path>`, documentar default de `--project` (derivar de `config.yaml` ou nome do diretorio), e considerar `--output-dir` para overrides em CI.

**Observacoes constituintes:**
- Enhancement Opportunities — `{tmp}` indefinido para screen inventory (headless contract)
- Enhancement Opportunities — Sem `--screens-json <path>` para automadores (automation)
- Enhancement Opportunities — Default de `--project` nao documentado (headless contract)
- Enhancement Opportunities — Sem indicador de progresso em modo headless (automation)

### 4. Validacao Pos-Geracao Depende Apenas do LLM (medium — 3 observacoes)

A validacao de cobertura (Passo 5) e a checagem de jargao tecnico sao feitas inteiramente pelo LLM, que pode falhar silenciosamente. Scripts deterministicos para essas tarefas seriam mais confiaveis e economizariam ~550-1000 tokens por invocacao.

**Impacto:** Melhora a confiabilidade da validacao e reduz custo de tokens.

**Acao:** Criar um script `validate-manual.py` que verifica: (a) cada US do inventario tem secao correspondente, (b) cada mensagem do catalogo aparece no manual, (c) nenhum termo tecnico proibido esta presente. Executar como pos-processamento.

**Observacoes constituintes:**
- Script Opportunities — Coverage validation checklist como script (Medium, ~400-700 tokens)
- Script Opportunities — Deteccao de jargao tecnico como script (Medium, ~150-300 tokens)
- Enhancement Opportunities — Sem validacao automatica de jargao (quality assurance)

### 5. Pre-Pass de Dados Estruturais Pode Ser Scriptado (medium — 3 observacoes)

Os Passos 1-3 (inventario de US, parse de mensagens, mapeamento de telas) sao operacoes de extracao deterministica que o LLM executa sequencialmente. Scripts Python poderiam extrair esses dados em paralelo, economizando ~500-1300 tokens e permitindo que o LLM foque na redacao.

**Impacto:** Reduz latencia e custo de tokens na fase de coleta de dados.

**Acao:** Criar scripts `extract-us-inventory.py` e `extract-messages.py` que produzem JSON estruturado. Reestruturar Passos 1-3 como uma fase paralela de coleta de dados seguida de cross-reference.

**Observacoes constituintes:**
- Script Opportunities — Extracao de inventario de US (Medium, ~300-800 tokens)
- Script Opportunities — Parse de catalogo de mensagens (Medium, ~200-500 tokens)
- Execution Efficiency — Reads sequenciais independentes nos Passos 1-3 (Medium)

## Forcas

- **Identidade afiada.** O agente sabe exatamente o que e e o que se recusa a fazer. O principio zero-jargao com lista de termos proibidos e tabela de substituicao transforma um principio vago em regras executaveis.
- **Missao exemplar.** "Nenhum usuario do tribunal precisa pedir ajuda para usar o sistema" e um dos melhores padroes para prompts de agentes — define o que "bom" significa em uma unica frase que funciona como framework de decisao para casos de borda.
- **Zero desperdicio de tokens.** Nenhum padding defensivo, nenhuma meta-explicacao, nenhuma back-reference. O pre-pass confirmou zero waste patterns, e a analise manual concorda. Total de ~3011 tokens e enxuto e eficiente.
- **Separacao persona-capability limpa.** SKILL.md cuida de identidade, voz e principios. O capability prompt cuida de workflow e regras de dominio. Sem sangramento entre os dois.
- **Contrato headless maduro.** Exit codes (0/1/2), JSON summary estruturado e degradacao graciosa (marcando secoes incompletas ao inves de inventar) mostram maturidade de design.
- **Tooling de suporte operacional.** `extract-screens.py` com testes mostra maturidade operacional — o padrao de pre-pass ja esta estabelecido.
- **Design de pipeline limpo.** A dependencia em artefatos de saida de `tjce-agent-requirements` (nao no agente em si) significa que o agente e autocontido e testavel.
- **Principio "nunca inventar" e load-bearing.** Estabelecido em Principles e reforcado em quatro pontos do capability prompt. Para um agente de documentacao, esta e a restricao comportamental mais critica.

## Analise Detalhada

### Estrutura e Capacidades

Agente estruturalmente solido com todas as secoes obrigatorias presentes, frontmatter limpo em kebab-case, e arquitetura de capability unica bem definida. A descricao segue o formato de duas partes com trigger phrases explicitas. A sequencia de ativacao e logicamente ordenada: config load, prerequisite check, optional pre-pass, capability routing. Um unico achado estrutural: a capability nao tem condicoes de progressao.

Achados adicionais nao cobertos por temas:
- **LOW** — `SKILL.md:58-60` — Secao Screen Pre-Pass referencia `python3` sem verificar disponibilidade. Adicionar nota: "Se script indisponivel, pular — capability prompt trata o fallback."
- **MEDIUM** — `references/manual-capability.md:36-75` — Template de estrutura do manual e rigido. Considerar nota-lo como "estrutura default" adaptavel.

### Persona e Voz

**Qualidade do overview:** Adequada. Overview de 9 linhas (~1330 tokens) estabelece missao, audiencia, enquadramento de dominio e teoria da mente de forma concisa. O contexto de persona e load-bearing e proporcional ao dominio (documentacao judicial requer calibracao cuidadosa de tom). Identity e Communication Style sao secoes distintas sem redundancia.

Achados adicionais nao cobertos por temas:
- **LOW** — `references/manual-capability.md:114-123` — Tabela de substituicao inline (7 linhas). Aceitavel agora, mas se crescer alem de ~15 entradas, extrair para `references/terminology-map.md`.

### Coesao de Identidade

Agente altamente coeso com identidade de proposito unico. A persona de "redator tecnico didatico e paciente" e perfeitamente refletida no design da capability. Nao ha gap entre quem o agente diz ser e o que pode fazer. A integracao com skills externos e limpa — depende de artefatos, nao de agentes em runtime.

**Dimensoes:**
- Alinhamento persona-capability: **Forte** — identidade de escritor tecnico e operacionalizada diretamente nos passos de geracao
- Completude de capabilities: **Moderada** — falta modo incremental, conversao de formato e geracao de glossario
- Deteccao de redundancia: **Forte** — zero redundancias detectadas
- Integracao externa: **Forte** — dependencia em artefatos de `tjce-agent-requirements` bem documentada
- Granularidade de capability: **Forte** — nivel correto de abstracao

Sugestoes criativas:
- Anotacoes de acessibilidade para sistemas governamentais
- Narrativa de diff entre versoes ("O que mudou nesta versao")
- Scoring de complexidade por secao como feedback de UX
- Integracao com automacao de screenshots via Playwright

### Eficiencia de Execucao

Agente enxuto e razoavelmente eficiente para uma skill stateless de capability unica. O pre-pass nao encontrou problemas de dependencia, ciclos ou violacoes de cadeia de subagentes. O `extract-screens.py` e um padrao de eficiencia solido. Ja eficiente: loading seletivo de recursos, config resolvido uma vez na ativacao, contrato headless limpo.

Achados adicionais nao cobertos por temas:
- **LOW** — `SKILL.md:48-52` — Checks de prerequisito sao sequenciais; poderiam ser batched em uma unica mensagem.

### Experiencia de Conversa

O agente esta proximo de ser headless-ready de primeira classe. A degradacao graciosa em tres camadas para informacao de tela e bem desenhada. Jornadas de primeiro uso tem boa orientacao mas falta guidance sobre como invocar `tjce-agent-requirements`. Usuarios experts nao tem fast-track para pular passos que ja conhecem.

Jornadas:
- **Primeiro uso:** Prerequisite check claro e tom acolhedor, mas falta guidance sobre como usar `tjce-agent-requirements` e quando usar o pre-pass script
- **Expert:** Headless + JSON bem desenhados, mas sem fast-track ou dry-run
- **Confuso:** Identidade forte rapidamente sinaliza que nao e a ferramenta certa, mas falta check de intencao inicial
- **Edge-case:** Sem orientacao para story sets muito grandes; sem deteccao de idioma; sem dedup de mensagens
- **Ambiente hostil:** Degradacao graciosa funciona bem; gap menor no exit code do script vs. expectativa do usuario
- **Automador:** Exit codes e JSON excelentes; gaps no `{tmp}` path e parametros de input

### Oportunidades de Script

O agente ja tem uma base solida com `extract-screens.py`. Ha oportunidades significativas para scripts adicionais: extracao de inventario de US (~300-800 tokens), parse de catalogo de mensagens (~200-500 tokens), validacao de cobertura (~400-700 tokens), deteccao de jargao (~150-300 tokens), e geracao de JSON summary (~150-250 tokens). Economia total estimada: ~1.280-2.630 tokens por invocacao.

Ordem recomendada de implementacao:
1. Validador de cobertura + checker de jargao (ganho imediato de confiabilidade)
2. Extrator de inventario de US (reduz custo pre-pass)
3. Parser de catalogo de mensagens (completa o pipeline pre-pass)
4. Checker de prerequisitos e gerador de JSON summary (ganhos menores, faceis de implementar)

## Recomendacoes

1. **Adicionar condicoes de progressao em `manual-capability.md`** — Resolve 3 observacoes. Esforco baixo. Adicionar gates apos Passo 1 e Passo 5 para prevenir avancos prematuros, especialmente sob compactacao de contexto.

2. **Implementar modo incremental (`--update`)** — Resolve 5 observacoes. Esforco alto. Ler manual existente, fazer diff com requisitos atuais, gerar apenas secoes novas/alteradas. Inclui estrategia de chunking para story sets grandes.

3. **Completar contrato headless para automacao** — Resolve 4 observacoes. Esforco baixo. Definir `{tmp}`, adicionar `--screens-json`, documentar default de `--project`.

4. **Criar script `validate-manual.py`** — Resolve 3 observacoes. Esforco medio. Validacao deterministica de cobertura US, cobertura de mensagens e jargao proibido como pos-processamento.

5. **Criar scripts de pre-pass para extracao estrutural** — Resolve 3 observacoes. Esforco medio. `extract-us-inventory.py` e `extract-messages.py` para paralelizar coleta de dados e economizar ~500-1300 tokens.

6. **Adicionar check de intencao antes da ingestao** — Resolve 2 observacoes. Esforco baixo. Perguntar o que o usuario deseja (gerar completo, atualizar, verificar cobertura) antes de processar artefatos.
