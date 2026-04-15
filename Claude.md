# CLAUDE.md — CTRVE @TJCE/CODESA

## Contexto
- Sistema: CTRVE
- Descrição: Controle de Veículos do TJCE
- Stack: FastAPI (Python 3.12) + React (TypeScript) + PostgreSQL
- Tipo: Greenfield (projeto novo)
- Coordenadoria: CODESA
- Processo: BMAD Method customizado para TJCE

## Estrutura do Projeto
backend/          # FastAPI — API REST
app/
api/          # Endpoints
models/       # SQLAlchemy models
schemas/      # Pydantic schemas
services/     # Lógica de negócio
core/         # Config, security, database
tests/          # Pytest
alembic/        # Migrations
frontend/         # React TypeScript
src/
components/
pages/
services/     # API calls
hooks/

## Comandos
- test backend: `cd backend && pytest --cov=app --cov-report=term-missing`
- test frontend: `cd frontend && npm test`
- lint backend: `cd backend && ruff check .`
- lint frontend: `cd frontend && npm run lint`
- run backend: `cd backend && uvicorn app.main:app --reload`
- run frontend: `cd frontend && npm start`
- migration: `cd backend && alembic revision --autogenerate -m "descricao"`

## Artefatos OBRIGATÓRIOS (Esteira TJCE)
### Requisitos (Phase 2 — SPEC)
- Estórias de Usuário → spec/requirements/user-stories.md
- Regras de Negócio → spec/requirements/business-rules.md
- Mensagens do Sistema → spec/requirements/messages.md
- Visão do Produto → spec/requirements/product-vision.md

### Implementação (Phase 4 — BUILD)
- Testes unitários: meta ≥80% cobertura
- Code Review: obrigatório (sessão limpa)
- Modelo de Dados: spec/architecture/data-model.md

### Entrega (Phase 6 — SHIP)
- PML → release/PML.md
- Contagem APF → release/apf/contagem-detalhada.md
- Manual do Usuário → release/manual/ (quando necessário)

## Segurança
- Dados pessoais (CPF, nome, endereço) = sensíveis (LGPD)
- NUNCA commitar secrets, tokens, credenciais ou dados reais
- Queries SEMPRE via SQLAlchemy ORM — NUNCA SQL raw sem parametrização
- Sanitização de input via Pydantic schemas
- Logs NUNCA contêm dados pessoais em texto plano
- CORS restrito a domínios autorizados
- Auth via JWT / Keycloak (conforme padrão do tribunal)

## Classificação de Erros (Esteira TJCE)
- Alta: Bloqueia completamente funcionalidade ou aplicação
- Média: Bloqueia uso apropriado, mas existe workaround
- Baixa: Não compromete objetivo final, problemas de layout

## Padrões de Código
### Backend (Python/FastAPI)
- Type hints obrigatórios em todas as funções
- Docstrings em português para funções públicas
- Endpoints seguem REST: GET/POST/PUT/DELETE
- Responses com Pydantic models (nunca dict cru)
- Erros com HTTPException e códigos corretos

### Frontend (React/TypeScript)
- Componentes funcionais com hooks
- TypeScript strict mode
- Styling via [Tailwind/CSS Modules/styled-components]
- Chamadas API centralizadas em services/