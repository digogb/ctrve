---
name: changelog-capability
menu-code: C
description: Derive release notes from Git commits since last tag, grouped by user story (US-XXX). Identifies unmapped commits and validates story references against spec.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and runtime flags are resolved by the parent SKILL.md at activation time.

# CHANGELOG — Release Notes por Estoria

Produz `{output_folder}/release/CHANGELOG.md` — release notes agrupadas por estoria de usuario implementada. Baseado em commits Git reais desde a ultima tag.

## What Success Looks Like

1. **`{output_folder}/release/CHANGELOG.md`** — changelog completo agrupado por US
2. Cada US com titulo e lista de mudancas derivadas dos commits
3. Commits sem referencia a US listados separadamente
4. Nenhuma mudanca inventada — tudo rastreavel a commits reais

## Inputs

### Pre-pass Data (preferred)

- **`{output_folder}/.tmp/git-changelog.json`** — output de `extract-git-changelog.py`

### Fallback

- Git log: `git log --oneline {since}..HEAD`
- `{output_folder}/requirements/user-stories.md` — para titulos de US

## Estrutura do CHANGELOG

```markdown
# CHANGELOG — {Nome do Sistema} v{version}

**Data:** {date}
**Periodo:** {since_tag} -> {current_tag_or_HEAD}
**Total de commits:** {total}

## Funcionalidades Implementadas

### US-001 — {Titulo da Estoria}
- {resumo do commit 1} (`abc1234`)
- {resumo do commit 2} (`def5678`)

### US-002 — {Titulo da Estoria}
- ...

## Manutencao e Infraestrutura

- {message} (`sha`) — @{author}

## Estatisticas

- Commits mapeados a estorias: {N}/{total} ({pct}%)
- Estorias entregues: {stories_count}
- Autores: {authors_list}
```

## Passos de Geracao

### Passo 1 — Extrair Commits

Ler `git-changelog.json`. Se indisponivel, executar:

```bash
python3 scripts/extract-git-changelog.py {project-root} \
  --since {since} \
  --stories {output_folder}/requirements/user-stories.md \
  -o {output_folder}/.tmp/git-changelog.json
```

### Passo 2 — Enriquecer com Titulos

Se `user-stories.md` disponivel, cruzar US-NNN com titulos. Se nao disponivel, usar apenas o ID.

### Passo 3 — Redigir CHANGELOG

Agrupar commits por US. Para cada commit:
- Resumir a mensagem (primeira linha do commit message)
- Incluir SHA abreviado
- Incluir autor

Commits sem US vao para "Manutencao e Infraestrutura".

### Passo 4 — Escrever Artefato

Escrever em `{output_folder}/release/CHANGELOG.md`.

## Headless Mode

- Sem interacao
- `--since` default: ultima tag Git
- Unmapped commits geram warning mas nao bloqueiam (exit 0)
- Se 100% unmapped: exit 1 (provavel problema de rastreabilidade)
