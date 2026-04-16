---
name: deploy-capability
menu-code: D
description: Generate deployment checklist with ordered steps and mandatory rollback plan. Detects migrations, dependency changes, and config changes from Git diff.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and runtime flags are resolved by the parent SKILL.md at activation time.

# DEPLOY — Checklist de Implantacao e Rollback

Produz dois artefatos:
- **`{output_folder}/release/deploy-checklist.md`** — passos ordenados de implantacao
- **`{output_folder}/release/rollback-plan.md`** — procedimento de reversao SEMPRE presente

## What Success Looks Like

1. Checklist com passos numerados, cada um executavel sem ambiguidade
2. Ordem correta: Banco -> Backend -> Frontend
3. Rollback plan completo cobrindo cada passo do deploy
4. Mudancas detectadas automaticamente (migrations, deps, configs)
5. Pre-deploy e post-deploy validation checks

## Inputs

### Pre-pass Data (preferred)

- **`{output_folder}/.tmp/deploy-changes.json`** — output de `detect-deploy-changes.py`

### Fallback

- `git diff {since}..HEAD --name-only` — arquivos alterados
- Ler conteudo dos arquivos de migration, requirements.txt, package.json manualmente

## Estrutura do Deploy Checklist

```markdown
# Checklist de Implantacao — {Nome do Sistema} v{version}

**Data prevista:** {date}
**Responsavel:** {responsible}
**Ambiente:** Producao

## Pre-Deploy

- [ ] Backup do banco de dados realizado
- [ ] Versao anterior taggeada: `{previous_tag}`
- [ ] Variaveis de ambiente atualizadas: {lista}
- [ ] Equipe notificada sobre janela de manutencao

## Deploy — Banco de Dados

- [ ] Executar migrations: `alembic upgrade head`
- [ ] Verificar versao Alembic: `alembic current` -> {expected_revision}

## Deploy — Backend

- [ ] Atualizar dependencias: `pip install -r requirements.txt`
- [ ] Restart servico backend
- [ ] Health check: `curl -f http://localhost:8000/api/v1/health`

## Deploy — Frontend

- [ ] Atualizar dependencias: `npm ci`
- [ ] Build: `npm run build`
- [ ] Deploy estaticos
- [ ] Verificar carregamento da aplicacao

## Pos-Deploy

- [ ] {checks especificos por US implementada}
- [ ] Monitorar logs por 15 minutos
- [ ] Confirmar implantacao bem-sucedida
```

## Estrutura do Rollback Plan

```markdown
# Plano de Rollback — {Nome do Sistema} v{version}

**Versao anterior:** {previous_tag}
**Responsavel:** {responsible}

## Criterios para Rollback

Executar rollback se qualquer check pos-deploy falhar ou se erro critico for detectado.

## Procedimento

### 1. Frontend
- Deploy da versao anterior dos estaticos

### 2. Backend
- Deploy da versao anterior: `git checkout {previous_tag}`
- Restaurar dependencias: `pip install -r requirements.txt`
- Restart servico

### 3. Banco de Dados
- Reverter migration: `alembic downgrade {previous_revision}`
- Verificar: `alembic current` -> {previous_revision}

### 4. Configuracoes
- Reverter variaveis de ambiente

## Validacao Pos-Rollback

- [ ] Health check: `curl -f http://localhost:8000/api/v1/health`
- [ ] Funcionalidades anteriores operacionais
- [ ] Notificar equipe sobre rollback
```

## Passos de Geracao

### Passo 1 — Detectar Mudancas

Ler `deploy-changes.json`. Se indisponivel, executar:

```bash
python3 scripts/detect-deploy-changes.py {project-root} \
  --since {since} \
  -o {output_folder}/.tmp/deploy-changes.json
```

### Passo 2 — Montar Checklist

Incluir apenas secoes aplicaveis:
- Se `has_migrations: false` -> omitir secao "Deploy — Banco de Dados"
- Se sem mudancas em frontend -> omitir secao "Deploy — Frontend"
- Sempre incluir Pre-Deploy e Pos-Deploy

Adicionar passos especificos para:
- Cada nova variavel de ambiente em `config_changes`
- Cada nova dependencia significativa
- Cada migration com descricao

### Passo 3 — Montar Rollback

Para CADA passo do checklist, incluir o reverso. Ordem inversa: Frontend -> Backend -> Banco.

**Rollback NUNCA e opcional.** Mesmo se deploy nao tem migrations: "Deploy da versao anterior e restart."

### Passo 4 — Escrever Artefatos

Escrever `{output_folder}/release/deploy-checklist.md` e `{output_folder}/release/rollback-plan.md`.

## Headless Mode

- Gerar ambos artefatos sem interacao
- Inferir `{previous_tag}` do Git (`git describe --tags --abbrev=0`)
- Se zero mudancas detectadas: exit 1 com warning
