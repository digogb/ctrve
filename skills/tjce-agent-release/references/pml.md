---
name: pml-capability
menu-code: P
description: Generate PML (Plano de Mudanca e Liberacao), the mandatory TJCE release document with identification, change description, impact analysis, deployment procedure, rollback, and post-deployment validation.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and runtime flags are resolved by the parent SKILL.md at activation time.

# PML — Plano de Mudanca e Liberacao

Produz `{output_folder}/release/PML.md` — artefato obrigatorio do PDS Unificado do TJCE. Documento oficial que autoriza a implantacao de mudancas em ambiente de producao.

## What Success Looks Like

1. **`{output_folder}/release/PML.md`** — documento completo com TODAS as 6 secoes preenchidas
2. Toda estoria implementada referenciada na Descricao da Mudanca
3. Impacto em banco (Alembic migrations), configs e integracoes declarado explicitamente
4. Procedimento de implantacao com passos numerados e ordem inequivoca
5. Procedimento de rollback completo — NUNCA ausente
6. Validacao pos-implantacao com checks especificos (nao genericos)

## Inputs

### Pre-pass Data (preferred)

- **`{output_folder}/.tmp/git-changelog.json`** — commits agrupados por US com metadata
- **`{output_folder}/.tmp/deploy-changes.json`** — migrations, dependencias, configs detectadas

### Fallback (if pre-pass unavailable)

- Git log: `git log --oneline {since}..HEAD`
- `{output_folder}/requirements/user-stories.md`
- `{output_folder}/architecture/tech-design.md`

### Metadata (from CLI flags or interactive input)

- `{project}` — nome do sistema
- `{version}` — versao da release
- `{responsible}` — responsavel pela implantacao
- `{des}` — identificador da tarefa DES
- `{date}` — data prevista (default: today)

## Estrutura do PML

```markdown
# Plano de Mudanca e Liberacao — {Nome do Sistema}

## 1. Identificacao

| Campo | Valor |
|-------|-------|
| Sistema | {project} |
| Versao | {version} |
| Data prevista | {date} |
| Responsavel | {responsible} |
| Tarefa DES | {des} |

## 2. Descricao da Mudanca

Resumo das alteracoes implementadas nesta versao, organizadas por estoria:

- **US-001 — {titulo}**: {resumo da implementacao}
- **US-002 — {titulo}**: {resumo}

## 3. Analise de Impacto

### 3.1. Banco de Dados
{migrations Alembic identificadas, ou "Sem alteracoes de banco"}

### 3.2. Configuracoes
{novas variaveis de ambiente, alteracoes em configs}

### 3.3. Dependencias
{novos pacotes pip/npm, atualizacoes de versao}

### 3.4. Integracoes
{APIs externas afetadas, ou "Sem impacto em integracoes"}

### 3.5. Indisponibilidade
{tempo estimado de downtime, ou "Deploy sem downtime (rolling)"}

## 4. Procedimento de Implantacao

1. {passo numerado com comando exato ou acao}
2. ...

## 5. Procedimento de Rollback

1. {passo para reverter em ordem inversa}
2. ...

## 6. Validacao Pos-Implantacao

- [ ] {check especifico: endpoint X retorna 200}
- [ ] {check: tela Y carrega sem erro}
- [ ] {check: migration rodou (verificar versao Alembic)}
```

## Passos de Geracao

### Passo 1 — Coletar Metadata

Se metadata nao fornecida via flags, perguntar interativamente. Em headless, derivar de config e Git.

### Passo 2 — Mapear Mudancas por Estoria

Ler `git-changelog.json` (ou Git log como fallback). Para cada commit:
- Se referencia US-NNN: agrupar sob a estoria
- Se nao referencia: listar em "Commits sem estoria associada" e sinalizar

Cruzar com `user-stories.md` para obter titulos das US.

### Passo 3 — Analisar Impacto

Ler `deploy-changes.json` (ou analisar diff manualmente). Identificar:
- Alembic migrations (arquivos em `alembic/versions/` ou `migrations/`)
- Mudancas em requirements.txt, pyproject.toml, package.json, package-lock.json
- Mudancas em .env.example, config/, settings/
- Mudancas em arquivos de integracao (API clients, webhooks)

**Nunca inventar impacto.** Se `detect-deploy-changes.py` nao encontrou migrations, registrar "Sem alteracoes de banco".

### Passo 4 — Montar Procedimento de Deploy

Ordem padrao TJCE (FastAPI + React + PostgreSQL):
1. Backup do banco
2. Executar migrations Alembic (`alembic upgrade head`)
3. Atualizar dependencias backend (`pip install -r requirements.txt`)
4. Deploy backend (restart servico)
5. Atualizar dependencias frontend (`npm ci`)
6. Build frontend (`npm run build`)
7. Deploy frontend
8. Validacao pos-implantacao

Omitir passos nao aplicaveis. Adicionar passos para novas configs de ambiente.

### Passo 5 — Montar Rollback

Para CADA passo de deploy, incluir o reverso:
- Migration: `alembic downgrade {previous_revision}`
- Dependencias: restaurar backup de requirements.txt/package.json
- Config: reverter variaveis de ambiente
- Codigo: deploy da versao anterior (tag ou SHA)

**Rollback NUNCA e "nao aplicavel".** No minimo: "reverter deploy para versao anterior {tag}."

### Passo 6 — Validacao Pos-Implantacao

Checks especificos derivados das US implementadas. **Nunca generico.** "Verificar se o sistema funciona" e proibido. Sempre: "Verificar se GET /api/v1/health retorna 200."

### Passo 7 — Escrever Artefato

Escrever em `{output_folder}/release/PML.md`.

## Headless Mode

- Derivar toda metadata de flags/config/Git
- Gerar completo sem interacao
- Se informacao insuficiente para secao, marcar com `**PENDENTE — informacao insuficiente**` e exit 1
