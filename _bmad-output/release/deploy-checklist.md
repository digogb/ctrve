# Deploy Checklist — CTRVE v1.0.0

**Data:** 2026-04-28
**Versão:** 1.0.0 (implantação inicial)
**Responsável:** Equipe de Infraestrutura TJCE

---

## Pré-Implantação

### Ambiente
- [ ] Servidor de aplicação disponível e acessível
- [ ] PostgreSQL provisionado e acessível pelo backend
- [ ] Variáveis de ambiente configuradas no servidor (ver seção Configuração)
- [ ] Certificado SSL configurado (HTTPS obrigatório para cookies `secure`)
- [ ] Proxy reverso (nginx/caddy) configurado para rotear `/api` → backend e `/` → frontend
- [ ] Backup do banco de dados existente realizado (N/A — implantação inicial)

### Configuração de Variáveis de Ambiente (backend)

```env
# Obrigatórias — sem valor padrão seguro
SECRET_KEY=<gerar com: openssl rand -hex 32>
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/ctrve

# Opcionais com padrão
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=false
CORS_ORIGINS=["https://ctrve.tjce.jus.br"]
```

- [ ] `SECRET_KEY` gerado com `openssl rand -hex 32` (nunca usar o padrão `changeme`)
- [ ] `DATABASE_URL` apontando para PostgreSQL de produção
- [ ] `DEBUG=false` configurado
- [ ] `CORS_ORIGINS` com URL de produção do frontend

### Verificação de Dependências
- [ ] Python 3.12+ disponível
- [ ] Node.js 22+ disponível (apenas para build do frontend)
- [ ] WeasyPrint e dependências de sistema instaladas (libpango, libcairo)

---

## Implantação Backend

- [ ] Clonar repositório na versão `v1.0.0` (tag ou commit `01e3017`)
- [ ] Instalar dependências: `pip install -r backend/requirements.txt`
- [ ] Executar criação de tabelas: `python -c "from app.database import create_db_and_tables; create_db_and_tables()"` *(SQLModel `create_all` — sem migrações Alembic nesta versão)*
- [ ] Iniciar servidor: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Verificar saúde da API: `curl https://ctrve.tjce.jus.br/api/health`
- [ ] Verificar documentação: `curl https://ctrve.tjce.jus.br/api/docs`

---

## Implantação Frontend

- [ ] Executar build de produção: `cd frontend && npm ci && npm run build`
- [ ] Copiar `frontend/dist/` para servidor de arquivos estáticos (nginx/S3/CDN)
- [ ] Verificar variável de ambiente de build: `VITE_API_URL=/api`
- [ ] Verificar acesso à URL principal: `https://ctrve.tjce.jus.br`

---

## Pós-Implantação

- [ ] Criar usuário Responsável inicial via API: `POST /api/v1/users` (apenas na primeira implantação)
- [ ] Verificar login com usuário criado
- [ ] Criar checklist de teste e verificar fluxo completo (entrega → devolução → PDF)
- [ ] Verificar geração de PDF
- [ ] Verificar expiração de sessão (testar após 30 min de inatividade ou reduzir timeout temporariamente)
- [ ] Verificar logs de aplicação — sem erros críticos
- [ ] Notificar usuários finais da disponibilidade do sistema

---

## Critério de Sucesso

Implantação considerada bem-sucedida quando:
1. Login funcional com perfis Responsável e Motorista
2. Criação, preenchimento e salvamento de checklist completo
3. Geração de PDF sem erros
4. Nenhum erro 500 nos logs nas primeiras 30 minutos de operação
