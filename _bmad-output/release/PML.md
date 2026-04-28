# Plano de Implantação — CTRVE

**Sistema:** CTRVE — Checklist de Transporte de Veículos
**Versão:** 1.0.0
**Solicitante:** Rodrigo Barbosa
**Data da Solicitação:** 28/04/2026

---

## 1. Controle de Versões

| Data | Versão | Descrição | Autor |
|------|--------|-----------|-------|
| 28/04/2026 | 01 | Criação do documento | Rodrigo Barbosa |

---

## 2. Autorizadores

| Grupo | Marcado |
|-------|---------|
| Sistemas Administrativos | X |
| Sistemas Judiciais de 1º Grau | |
| Sistemas Judiciais de 2º Grau | |
| Portais Intranet / Internet | |
| Infraestrutura | X |

---

## 3. Hardware e softwares básicos necessários

- Servidor Linux com Python 3.12+
- PostgreSQL 14+ acessível pelo servidor de aplicação
- Nginx configurado como proxy reverso
- Certificado SSL para o domínio de produção (obrigatório para cookies `secure`)
- WeasyPrint e dependências de sistema: libpango, libcairo, libgdk-pixbuf (geração de PDF)
- Node.js 22+ — necessário apenas para execução do build do frontend

---

## 4. Servidores Afetados

| Nome do Serviço / Sistema | IC Relacionado | Impacto Previsto |
|--------------------------|----------------|-----------------|
| CTRVE — Backend (FastAPI) | Novo serviço | Nenhum impacto em sistemas existentes. Implantação inicial sem substituição de legado. |
| CTRVE — Frontend (React) | Novo serviço | Nenhum impacto em sistemas existentes. |
| PostgreSQL | Banco compartilhado ou dedicado | Criação de banco de dados `ctrve`. Sem impacto em outros bancos. |

---

## 5. Detalhamento da Implantação

| ATIVIDADE | RESPONSÁVEL |
|-----------|-------------|
| **Pré-requisitos:** | Infraestrutura |
| • Provisionar banco de dados PostgreSQL chamado `ctrve` com usuário dedicado | |
| • Configurar DNS para o domínio de produção (ex.: `ctrve.tjce.jus.br`) | |
| • Emitir e instalar certificado SSL para o domínio | |
| • Configurar proxy reverso Nginx: `/api` → backend (porta 8000), `/` → arquivos estáticos do frontend | |
| • Instalar dependências de sistema do WeasyPrint: `libpango`, `libcairo`, `libgdk-pixbuf` | |
| • Configurar variáveis de ambiente de produção (ver Seção 6) | |
| **Passo 1 — Deploy do Backend:** | Aplicação |
| • Clonar repositório na tag `v1.0.0` (commit `01e3017`) | |
| • Instalar dependências Python: `pip install -r backend/requirements.txt` | |
| • Inicializar banco de dados: `python -c "from app.database import create_db_and_tables; create_db_and_tables()"` | |
| • Iniciar servidor: `uvicorn app.main:app --host 0.0.0.0 --port 8000` | |
| • Verificar saúde da API: `curl https://ctrve.tjce.jus.br/api/health` | |
| **Passo 2 — Deploy do Frontend:** | Aplicação |
| • Executar build de produção: `cd frontend && npm ci && npm run build` | |
| • Copiar `frontend/dist/` para o diretório raiz do Nginx | |
| • Verificar acesso à URL principal no navegador | |
| **Passo 3 — Validação Pós-Implantação:** | Aplicação / Negócio |
| • Criar usuário Responsável inicial via API: `POST /api/v1/users` | |
| • Realizar login e verificar acesso ao dashboard | |
| • Criar checklist de teste, salvar entrega, realizar devolução | |
| • Gerar PDF do checklist e verificar conteúdo | |
| • Verificar logs da aplicação — sem erros críticos | |

---

## 6. Detalhamento da configuração dos recursos adicionais

Variáveis de ambiente obrigatórias no servidor de produção:

| Variável | Descrição | Ação |
|----------|-----------|------|
| `SECRET_KEY` | Chave de assinatura JWT | Gerar com `openssl rand -hex 32`. **Nunca usar o valor padrão.** |
| `DATABASE_URL` | String de conexão PostgreSQL | Ex.: `postgresql+psycopg2://usuario:senha@host:5432/ctrve` |
| `CORS_ORIGINS` | Origens CORS permitidas | Ex.: `["https://ctrve.tjce.jus.br"]` |
| `DEBUG` | Modo debug | Definir como `false` em produção |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token | Padrão: `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token | Padrão: `7` |

---

## 7. Dependências

O sistema CTRVE não possui integrações com sistemas externos do TJCE nesta versão (sem integração com SEI, LDAP/AD ou sistema de frota). Operação independente.

---

## 8. Backup

### 8.1 Itens para backup

- Banco de dados `ctrve` (PostgreSQL)

### 8.2 Periodicidade

- **Backup completo:** 1x por semana (fins de semana ou horário de menor uso)
- **Backup incremental/diferencial:** diário, à noite, registrando mudanças desde o último backup completo

### 8.3 Retenção

- **Incrementais:** 15 dias
- **Semanais (completos):** 4 a 6 semanas

---

## 9. Monitoramento

Logs da aplicação via saída padrão do processo uvicorn. Sem ferramenta de APM configurada nesta versão inicial. Recomenda-se integração futura com a solução de observabilidade adotada pela STI/TJCE.

---

## 10. Contatos para Suporte

| NOME | FUNÇÃO |
|------|--------|
| Rodrigo Barbosa | Responsável pelo desenvolvimento — suporte a erros de aplicação |
| Equipe de Infraestrutura TJCE | Responsável pelo ambiente, rede e configuração do servidor |
| Gestor da Demanda | Ficar ciente da execução e resultado da implantação |
