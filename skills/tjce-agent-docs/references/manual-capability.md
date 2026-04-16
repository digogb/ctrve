---
name: manual-capability
menu-code: M
description: Generate a complete end-user manual from user stories, system messages, and implemented screens. Produces manual-usuario.md with step-by-step instructions for every US with screen interaction.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# MANUAL — Gerar Manual do Usuario

Produz `{output_folder}/manual/manual-usuario.md` — um manual destinado ao usuario final do sistema (juizes, servidores, advogados). Linguagem acessivel, sem jargao tecnico. Cada estoria de usuario com interacao de tela gera uma secao com passo a passo. Mensagens do sistema sao explicadas em linguagem leiga.

## What Success Looks Like

1. **`{output_folder}/manual/manual-usuario.md`** — manual completo seguindo a estrutura padrao TJCE
2. Toda US com interacao de tela tem secao correspondente com passo a passo
3. Toda mensagem de `messages.md` que aparece em fluxo de usuario esta explicada
4. Zero termos tecnicos no texto final
5. Secoes sem informacao de tela marcadas como pendentes (nunca inventadas)

## Inputs

### Obrigatorios

- **`{output_folder}/requirements/user-stories.md`** — estorias de usuario com fluxos de interacao
- **`{output_folder}/requirements/messages.md`** — catalogo de mensagens do sistema (codigos, textos, contextos de exibicao)

### Opcionais (enriquecem o manual)

- **Screen inventory** (`{tmp}/screens.json`) — se o pre-pass `extract-screens.py` foi executado, usar para mapear rotas, labels e botoes sem reler codigo
- **Frontend source** — quando o inventario nao basta, ler componentes especificos sob demanda para entender layout e fluxo de tela
- **`{output_folder}/requirements/business-rules.md`** — regras que explicam validacoes visiveis ao usuario (ex: "CPF invalido")

## Estrutura do Manual

```markdown
# Manual do Usuario — {Nome do Sistema}

**Versao:** {versao}
**Data:** {data}
**Destinatarios:** Usuarios do sistema (magistrados, servidores, advogados)

## 1. Introducao
- Objetivo do sistema
- A quem se destina
- Como usar este manual

## 2. Acesso ao Sistema
- Como acessar (URL, navegadores compativeis)
- Login e primeiro acesso
- Perfis de acesso e o que cada um pode fazer
- Recuperacao de senha

## 3. Funcionalidades
### 3.1. {Titulo da US-001}
#### O que e
Breve descricao funcional.
#### Como acessar
Caminho de navegacao: Menu > Submenu > Opcao.
#### Passo a passo
1. Na tela "{nome da tela}", preencha o campo "{label}".
2. Clique em "{botao}".
3. O sistema exibira a mensagem "{texto da mensagem}", 
   confirmando que {explicacao leiga}.
#### Mensagens que podem aparecer
- "{MSG-001}" — aparece quando {contexto}. Significa que {explicacao}.

### 3.N. {Titulo da US-NNN}
(...)

## 4. Perguntas Frequentes
- Pergunta tipica 1?
  Resposta.
- (...)
```

## Passos de Geracao

### Passo 1 — Inventario de US com tela

Ler `user-stories.md`. Identificar todas as US que envolvem interacao de tela (cadastro, consulta, listagem, relatorio, configuracao). US puramente backend/batch/integracao nao geram secao no manual.

Montar lista: `{US-ID, titulo, tipo de interacao}`.

### Passo 2 — Mapear telas e campos

Se screen inventory disponivel (`{tmp}/screens.json`), cruzar rotas e componentes com as US. Associar labels, botoes, placeholders e headings a cada US.

Se screen inventory nao disponivel mas codigo frontend acessivel, ler os componentes relevantes sob demanda. Priorizar: telas de formulario e listagem (mais material pro manual).

Se nem inventario nem codigo disponivel, gerar o manual baseado apenas em `user-stories.md` e `messages.md`, marcando secoes sem informacao de tela com `**TELA NAO IDENTIFICADA — revisao manual necessaria**`.

### Passo 3 — Mapear mensagens

Ler `messages.md`. Para cada mensagem:
- Identificar em qual US/fluxo ela aparece (pelo contexto ou pelo codigo referenciado)
- Preparar explicacao leiga do que a mensagem significa e o que o usuario deve fazer ao ve-la

### Passo 4 — Redigir manual

Redigir seguindo a estrutura padrao. Regras de redacao:

- **Imperativo**: "Clique em", "Preencha", "Selecione" — nunca "Voce deve clicar em"
- **Nomes visiveis**: usar label do campo/botao exatamente como aparece na tela (entre aspas quando necessario)
- **Navegacao explicita**: sempre incluir o caminho Menu > Submenu > Tela
- **Mensagens inline**: ao descrever um passo que gera mensagem, citar a mensagem e explicar
- **Screenshots**: quando referencia a tela e clara, indicar `[Imagem: {descricao da tela}]` como placeholder para screenshot futuro
- **FAQ**: derivar das duvidas mais provaveis baseadas nos fluxos (login, erros comuns, permissoes)

**Proibido no texto:**
- API, endpoint, query, schema, frontend, backend, request, response, payload, JSON, token, middleware, componente, rota, render, state, hook, prop, callback
- Qualquer termo que um servidor do tribunal nao entenderia sem ajuda

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

Antes de escrever o artefato final, verificar:

- [ ] Toda US com interacao de tela tem secao no manual?
- [ ] Toda mensagem de `messages.md` em fluxo de usuario esta explicada?
- [ ] Nenhuma secao contem termos tecnicos proibidos?
- [ ] Secoes sem informacao de tela estao marcadas (nao inventadas)?

Se algum check falhar em modo interativo, informar o usuario e pedir orientacao. Em headless, marcar as lacunas e prosseguir.

### Passo 6 — Escrever artefato

Escrever em `{output_folder}/manual/manual-usuario.md`.

## Headless Mode

If `--headless` or `-H`:
- Gerar manual completo sem interacao
- Secoes sem informacao de tela: marcar com `**TELA NAO IDENTIFICADA — revisao manual necessaria**` e continuar
- Emitir JSON summary quando `--json` (schema em SKILL.md)
- Exit 0 se todas as secoes completas; exit 1 se alguma pendente; exit 2 se prereqs faltando

## Interactive Mode

- Ao encontrar US sem informacao de tela, perguntar: "A US-NNN ({titulo}) precisa de passo a passo com tela, mas nao encontrei informacao suficiente sobre essa tela. Pode me mostrar o componente, um screenshot, ou descrever o layout?"
- Ao concluir primeira versao, oferecer revisao: "Manual gerado com {N} secoes. Quer que eu leia alguma secao especifica em voz alta para verificar clareza?"
- Se o usuario colar screenshot ou descrever tela, integrar e atualizar a secao correspondente
