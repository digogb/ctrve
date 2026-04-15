# Analise de Coesao do Agente — tjce-requirements

**Data:** 2026-04-15  
**Agente:** `skills/tjce-requirements/`  
**Artefatos analisados:** SKILL.md, references/generate-requirements.md, references/artifact-templates.md

---

## 1. Alinhamento Persona-Capacidade

**Veredicto: FORTE**

A persona declarada — "analista de requisitos senior com experiencia em sistemas judiciais — metodico, preciso, e desconfortavel com ambiguidade" — esta em plena consonancia com as capacidades entregues. A identidade nao e decorativa: ela fundamenta decisoes de comportamento concretas:

- A aversao a ambiguidade se materializa no princípio operacional de parar e perguntar (modo interativo) ou marcar `[ASSUMIDO]` (modo headless) — nunca preencher com suposicao silenciosa.
- A precisao se traduz nos templates fixos, IDs sequenciais obrigatorios e na checklist de auto-validacao antes do output.
- O "senior" justifica a competencia para conduzir entrevistas estruturadas, derivar regras de estorias e mensagens de regras, e auditar a rastreabilidade de ponta a ponta.

Nao ha capacidades declaradas que excedam o perfil, nem perfil que exceda as capacidades. A correspondencia e 1:1.

---

## 2. Completude das Capacidades

### 2.1 O que esta bem coberto

- Geracao dos 4 artefatos obrigatorios do PDS Unificado com ordem de geracao definida (Visao -> Estorias -> Regras -> Mensagens).
- Dois modos de entrada estruturados: entrevista interativa e geracao a partir de PRD/brief.
- Modo headless com tratamento explicito de ausencia de input.
- Rastreabilidade bidirecional: US referencia RNs, RN referencia US, MSG referencia RN.
- Auto-validacao antes do output com lista de checks nomeados.
- Sumario de rastreabilidade pos-geracao.
- Tratamento de premissas em modo headless (`assumptions.md`).

### 2.2 Lacunas identificadas

**L1 — Atualizacao incremental de artefatos existentes**  
O agente define bem como _criar_ especificacoes do zero, mas nao existe fluxo para _atualizar_ artefatos ja gerados. Projetos reais evoluem: novas estorias entram, regras mudam, mensagens sao renumeradas. Sem esse fluxo, o agente e descartado apos a primeira geracao ou exige reescrita manual fora do controle do agente.

**L2 — Sem capacidade de validacao autonoma de artefatos existentes**  
Nao ha capacidade de receber artefatos produzidos por terceiros (ou por versao anterior do agente) e auditar sua coesao. Um analista senior, na pratica, revisa o trabalho de outros. Isso seria valioso como capability separada.

**L3 — Sem tratamento de conflito entre documentos de entrada**  
Quando o PRD contradiz um brief anterior, ou quando dois documentos de entrada descrevem o mesmo requisito de formas diferentes, o agente nao tem protocolo definido. Apenas "leia o documento inteiro" nao e suficiente para casos de entrada multi-documento.

**L4 — Criterios de Aceitacao nao possuem template estruturado**  
O template de User Stories inclui criterios de aceitacao como lista de checkboxes livres. Nao ha convencao sobre granularidade (quantos criterios por estoria? todos devem ser verificaveis com sim/nao? devem cobrir o caminho feliz e os excepcionais?). Isso e a unica secao sem convencao explicita nos templates.

**L5 — Ausencia de glossario de termos judiciais**  
O agente atua em dominio especializado (sistemas judiciais do TJCE) mas nao carrega nem referencia um glossario. Termos como "processo", "autuacao", "distribuicao", "conclusao" tem significados tecnicos precisos no contexto judicial que diferem do uso comum. Sem glossario, a consistencia terminologica depende da sessao corrente, quebrando entre projetos.

---

## 3. Deteccao de Redundancias

**Veredicto: BAIXA REDUNDANCIA — 1 caso menor identificado**

**R1 — Restricao de rastreabilidade declarada em dois lugares**  
A secao "Principles" do SKILL.md e a secao "Traceability Constraints" do generate-requirements.md descrevem as mesmas restricoes de rastreabilidade (RN vinculada a US, MSG vinculada a RN, RN com caso de teste derivavel). A duplicacao e intencional do ponto de vista de enfase — o SKILL.md comunica ao orquestrador o que o agente garante, enquanto o generate-requirements.md e a instrucao operacional para o agente durante execucao. A redundancia nao cria inconsistencia e tem justificativa estrutural. Nao requer correcao, mas deve ser mantida sincronizada.

Nao ha outros casos de redundancia relevantes. O fluxo esta bem particionado: SKILL.md define identidade e entrada, generate-requirements.md define execucao, artifact-templates.md define formato.

---

## 4. Granularidade das Capacidades

**Veredicto: ADEQUADA com uma observacao**

O agente tem exatamente uma capability exposta: `Gerar Especificacao de Requisitos`. Dado que os 4 artefatos sao interdependentes por design (rastreabilidade cruzada), agrupá-los em uma unica capability e correto — gerar qualquer subconjunto quebraria as restricoes de rastreabilidade.

**Observacao — granularidade interna da entrevista**  
O fluxo de entrevista e descrito de forma concisa ("conduza entrevista estruturada por area funcional") sem script de perguntas ou criterio de completude. Para um agente deterministico em sessoes longas com varios atores e areas funcionais, a ausencia de estrutura na entrevista pode resultar em sessoes incompletas ou com cobertura desigual. Uma referencia separada `interview-guide.md` aumentaria a previsibilidade sem aumentar o numero de capabilities expostas.

---

## 5. Coerencia da Jornada do Usuario

**Veredicto: COERENTE com gap no fim do ciclo de vida**

A jornada esta bem definida do ponto de ativacao ate a entrega dos artefatos:

```
Ativacao
  └─> Detecta modo (headless / interativo com arquivo / interativo verbal / interativo sem input)
        └─> [Se verbal] Entrevista estruturada por area funcional
        └─> [Se arquivo/PRD] Le documento, identifica ambiguidades
              └─> [headless] Marca [ASSUMIDO], gera assumptions.md
              └─> [interativo] Para e pergunta
        └─> Gera em ordem: Visao -> Estorias -> Regras -> Mensagens
        └─> Auto-validacao (checklist de 7 pontos)
        └─> Output: 4 arquivos + sumario de rastreabilidade
```

**Gap: fim do ciclo nao esta mapeado**  
A jornada termina na entrega dos artefatos. Nao ha instrucao para o agente sobre o que fazer quando o usuario pede revisao, rejeita uma estoria, ou solicita adicionar um ator que foi omitido na entrevista. A saida do fluxo e um endpoint, nao um ciclo. Para um produto documental que inevitavelmente passa por revisao com stakeholders, isso e uma lacuna de jornada real.

**Gap secundario: confirmacao de escopo antes de gerar**  
Apos a entrevista (ou leitura do PRD), o agente nao apresenta um "resumo do escopo entendido" para confirmacao antes de gerar os 4 artefatos. Em projetos complexos, gerar tudo e descobrir no final que o escopo estava errado e custoso. Um checkpoint de confirmacao de escopo entre a coleta de input e a geracao seria coerente com o perfil do analista senior.

---

## 6. Integracao com Skills Externas

**Veredicto: DEPENDENCIA IMPLICITA NAO ENDOSSADA**

O agente depende de `{project-root}/_bmad/config.yaml` e `{project-root}/_bmad/config.user.yaml` para configuracao de caminhos e linguagem. Esta dependencia esta documentada no SKILL.md. Porem:

- Nao ha instrucao sobre o que fazer se os arquivos de config nao existirem (alem de usar defaults entre parenteses). Um `_bmad/config.yaml` ausente em projetos novos e um cenario comum — o comportamento de fallback para defaults e adequado, mas poderia ser explicito.
- O agente grava em `{project-root}/spec/requirements/` (conforme generate-requirements.md) mas o SKILL.md declara `{output_folder}` como base de output. Ha uma discrepancia potencial: se `{output_folder}` for customizado no config, o caminho `spec/requirements/` hardcoded em generate-requirements.md o ignoraria. Isso pode causar artefatos escritos no lugar errado.

**Nao ha integracao com outros agentes BMAD declarada.** O agente consome PRDs (potencialmente gerados por `bmad-agent-pm`) mas nao ha handshake formal, schema esperado para o PRD de entrada, nem referencia a outros agentes do ecossistema. Para um fluxo BMAD completo (PM -> Requisitos -> Arquitetura -> Dev), a ausencia de contratos de interface entre agentes e uma limitacao sistêmica, nao apenas deste agente.

---

## 7. Sumario e Recomendacoes Priorizadas

| Prioridade | Item | Tipo |
|------------|------|------|
| Alta | L1 — Adicionar fluxo de atualizacao incremental de artefatos | Lacuna de capability |
| Alta | Discrepancia de caminho de output entre SKILL.md e generate-requirements.md | Bug de configuracao |
| Media | L4 — Adicionar convencoes para Criterios de Aceitacao no template US | Lacuna de template |
| Media | Gap de checkpoint de confirmacao de escopo antes da geracao | Lacuna de jornada |
| Media | L5 — Referenciar ou incluir glossario de termos judiciais TJCE | Lacuna de dominio |
| Media | Gap de jornada no fim do ciclo (revisao e iteracao pos-entrega) | Lacuna de jornada |
| Baixa | L2 — Capability de validacao de artefatos existentes | Capability nova |
| Baixa | L3 — Protocolo para conflito entre documentos de entrada multiplos | Lacuna de fluxo |
| Baixa | Guia de entrevista estruturado (`interview-guide.md`) | Melhoria de previsibilidade |

---

## 8. Conclusao

O agente `tjce-requirements` apresenta coesao alta entre persona, principios e capacidades nucleares. O design da rastreabilidade cruzada entre os 4 artefatos e sua ordenacao de geracao sao pontos fortes genuinos — demonstram pensamento de dominio, nao apenas template. As lacunas identificadas sao de dois tipos: gaps de ciclo de vida (o agente nao acompanha o artefato apos entrega) e gaps de robustez operacional (configuracao, glossario, conflito de entrada). Nenhuma lacuna compromete o caso de uso central. O agente esta apto para uso em producao com as limitacoes documentadas acima.
