---
name: manual-capability
menu-code: M
description: Generate or incrementally update a complete end-user manual from user stories, system messages, and implemented screens. Produces manual-usuario.md with step-by-step instructions for every US with screen interaction.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# MANUAL — Gerar Manual do Usuario

Produz ou atualiza `{output_folder}/manual/manual-usuario.md` — um manual destinado ao usuario final do sistema (juizes, servidores, advogados). Linguagem acessivel, sem jargao tecnico. Cada estoria de usuario com interacao de tela gera uma secao com passo a passo. Mensagens do sistema sao explicadas em linguagem leiga.

Suporta dois modos: **full** (gerar do zero) e **update** (atualizar secoes novas/alteradas sem sobrescrever edicoes manuais).

## What Success Looks Like

1. **`{output_folder}/manual/manual-usuario.md`** — manual completo seguindo a estrutura padrao TJCE
2. Toda US com interacao de tela tem secao correspondente com passo a passo
3. Toda mensagem de `messages.md` que aparece em fluxo de usuario esta explicada
4. Zero termos tecnicos no texto final (validado por `validate-manual.py`)
5. Secoes sem informacao de tela marcadas como pendentes (nunca inventadas)

## Inputs

### Pre-pass Data (preferred — produced by SKILL.md pre-pass)

- **`{output_folder}/.tmp/us-inventory.json`** — inventario estruturado de US com flag `has_screen_interaction`
- **`{output_folder}/.tmp/messages-catalog.json`** — catalogo de mensagens com texto e contexto
- **`{output_folder}/.tmp/screens.json`** (ou `--screens-json`) — metadata de telas (rotas, labels, botoes, placeholders, headings)

### Fallback (if pre-pass unavailable)

- `{output_folder}/requirements/user-stories.md` — ler diretamente
- `{output_folder}/requirements/messages.md` — ler diretamente
- Frontend source — ler componentes sob demanda

### Opcional

- `{output_folder}/requirements/business-rules.md` — regras que explicam validacoes visiveis ao usuario

## Estrutura do Manual

```markdown
# Manual do Usuario — {Nome do Sistema}

**Versao:** {versao}
**Data:** {data}
**Destinatarios:** Usuarios do sistema (magistrados, servidores, advogados)

## 1. Introducao
## 2. Acesso ao Sistema
## 3. Funcionalidades
### 3.1. {Titulo da US-001}
#### O que e
#### Como acessar
#### Passo a passo
#### Mensagens que podem aparecer
### 3.N. {Titulo da US-NNN}
## 4. Perguntas Frequentes
```

Esta e a estrutura default — adaptavel quando o sistema exigir organizacao diferente.

## Modo Full — Geracao Completa

### Passo 1 — Inventario de US

Ler `us-inventory.json` (ou `user-stories.md` como fallback). Montar lista de US com interacao de tela. US puramente backend/batch nao geram secao.

**Progression gate:** Prosseguir somente quando o inventario de US estiver completo e confirmado. Em modo interativo, apresentar o inventario ao usuario: "{N} estorias com tela, {M} sem tela — confirma?" Em headless, prosseguir automaticamente.

**Para conjuntos grandes (>20 US):** Dividir em lotes de 15-20 US. Gerar cada lote sequencialmente, escrevendo no artefato incrementalmente. Isso evita degradacao por limite de contexto.

### Passo 2 — Mapear telas e campos

Se screen inventory disponivel (`screens.json` ou `--screens-json`), cruzar rotas e componentes com as US. Associar labels, botoes, placeholders e headings a cada US.

Se screen inventory nao disponivel mas codigo frontend acessivel, ler os componentes relevantes sob demanda. Priorizar: telas de formulario e listagem.

Se nem inventario nem codigo disponivel, gerar baseado apenas nos requisitos, marcando secoes com `**TELA NAO IDENTIFICADA — revisao manual necessaria**`.

### Passo 3 — Mapear mensagens

Ler `messages-catalog.json` (ou `messages.md`). Para cada mensagem:
- Identificar em qual US/fluxo ela aparece
- Preparar explicacao leiga do que significa e o que o usuario deve fazer

### Passo 4 — Redigir manual

Redigir seguindo a estrutura padrao. Regras de redacao:

- **Imperativo**: "Clique em", "Preencha", "Selecione"
- **Nomes visiveis**: label do campo/botao como aparece na tela
- **Navegacao explicita**: sempre incluir o caminho Menu > Submenu > Tela
- **Mensagens inline**: citar e explicar no passo que as gera
- **Screenshots**: indicar `[Imagem: {descricao da tela}]` como placeholder
- **FAQ**: derivar das duvidas mais provaveis (login, erros comuns, permissoes)

**Proibido no texto** (lista validada por script):
API, endpoint, query, schema, frontend, backend, request, response, payload, JSON, token, middleware, componente, rota, render, state, hook, prop, callback, deploy, commit, branch, merge, pull request, push, database, sql, orm, migration, seed

Substituicoes recomendadas:

| Termo tecnico | Equivalente funcional |
|---------------|----------------------|
| endpoint | funcionalidade / servico |
| query | consulta / busca |
| request | solicitacao |
| response | retorno / resultado |
| token | codigo de acesso |
| componente | tela / secao da tela |
| rota | pagina / tela |

### Passo 5 — Validar cobertura

**Progression gate:** Prosseguir para escrita somente quando todas as verificacoes passarem ou lacunas estiverem explicitamente marcadas.

Executar validacao deterministica:

```bash
python3 scripts/validate-manual.py {output_folder}/manual/manual-usuario.md \
  {output_folder}/requirements/user-stories.md \
  {output_folder}/requirements/messages.md
```

O script verifica:
- Toda US referenciada no manual
- Toda MSG referenciada no manual
- Zero termos tecnicos proibidos

Se algum check falhar em modo interativo, informar o usuario e pedir orientacao. Em headless, marcar as lacunas e prosseguir (exit 1).

### Passo 6 — Escrever artefato

Escrever em `{output_folder}/manual/manual-usuario.md`.

## Modo Update — Atualizacao Incremental

Quando `{output_folder}/manual/manual-usuario.md` ja existe:

### Passo 1 — Diff de requisitos

Ler o manual existente e o inventario atual de US. Identificar:
- **Novas US**: presentes no inventario mas sem secao no manual → gerar
- **US alteradas**: secao existe mas titulo mudou significativamente → atualizar
- **US removidas**: secao existe mas US nao esta mais no inventario → marcar para revisao (nao deletar automaticamente — usuario decide)
- **Mensagens novas**: MSG-NNN no catalogo mas nao no manual → integrar

### Passo 2 — Gerar delta

Gerar apenas as secoes novas/alteradas. Inserir na posicao correta dentro da estrutura existente (manter numeracao sequencial). Nao tocar em secoes inalteradas — preserva edicoes manuais.

### Passo 3 — Validar e escrever

Executar `validate-manual.py` no manual atualizado. Escrever o artefato.

## Headless Mode

If `--headless` or `-H`:
- Auto-detect full/update via existencia do manual
- Gerar sem interacao, usando pre-pass data
- Secoes sem tela: marcar `**TELA NAO IDENTIFICADA**` e continuar
- Executar `validate-manual.py` automaticamente
- Emitir JSON summary conforme schema em SKILL.md quando `--json` presente
- Exit 0 se tudo limpo; exit 1 se pendencias ou jargao; exit 2 se prereqs faltando

## Interactive Mode

- Ao encontrar US sem informacao de tela, perguntar: *"A US-NNN ({titulo}) precisa de passo a passo, mas nao encontrei informacao suficiente sobre essa tela. Pode me mostrar o componente, um screenshot, ou descrever o layout?"*
- Ao concluir, oferecer revisao: *"Manual gerado com {N} secoes. Quer que eu leia alguma secao em voz alta para verificar clareza?"*
- Se o usuario colar screenshot ou descrever tela, integrar e atualizar a secao
- Em modo update, apresentar o diff antes de aplicar: *"{N} secoes novas, {M} alteradas, {K} para revisao. Prosseguir?"*
