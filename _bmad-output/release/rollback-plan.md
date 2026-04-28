# Rollback Plan — CTRVE v1.0.0

**Data:** 2026-04-28
**Versão:** 1.0.0 (implantação inicial)

---

## Cenários de Ativação de Rollback

| Cenário | Critério | Ação |
|---------|----------|------|
| API não responde após implantação | `/api/health` retorna erro por >5 min | Rollback imediato |
| Erro 500 em operações críticas | Taxa >10% nas primeiras 30 min | Rollback imediato |
| Falha na geração de PDF | 100% das tentativas falham | Rollback imediato |
| Banco de dados inacessível | Sem conexão após restart do serviço | Verificar configuração antes de rollback |
| Erro de autenticação generalizado | Login impossível para todos os usuários | Rollback imediato |

---

## Procedimento de Rollback

### Implantação Inicial (v1.0.0)

Como esta é a **primeira implantação**, não existe versão anterior para restaurar. O rollback consiste em desativar o serviço.

#### 1. Parar o serviço backend
```bash
systemctl stop ctrve-backend
# ou
kill $(lsof -t -i:8000)
```

#### 2. Desativar o frontend
```bash
# Remover ou renomear o diretório dist no servidor nginx
mv /var/www/ctrve/dist /var/www/ctrve/dist.failed
# Retornar página de manutenção
cp /var/www/ctrve/manutencao.html /var/www/ctrve/index.html
```

#### 3. Verificar banco de dados
Como a implantação usa `create_all` (sem Alembic), as tabelas podem ter sido criadas. Se precisar limpar:
```sql
-- CUIDADO: destrói todos os dados
DROP TABLE IF EXISTS checklist CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
```

#### 4. Notificar usuários
Comunicar indisponibilidade temporária e prazo de resolução.

---

## Diagnóstico Rápido

```bash
# Verificar status do backend
curl -f http://localhost:8000/api/health || echo "Backend DOWN"

# Verificar logs
tail -100 /var/log/ctrve/app.log

# Verificar conexão com banco
python3 -c "from app.database import engine; engine.connect(); print('DB OK')"

# Verificar variáveis críticas
python3 -c "from app.core.config import settings; print('SECRET_KEY OK' if settings.SECRET_KEY != 'changeme-use-env-in-production' else 'ERRO: SECRET_KEY padrão em produção')"
```

---

## Contato em Caso de Falha

- **Equipe de Infraestrutura TJCE** — suporte de implantação
- **Equipe de Desenvolvimento** — para erros de aplicação
- **Responsável pela Demanda** — Rodrigo Barbosa

---

## Decisão de Rollback

Rollback deve ser decidido pelo **Gerente de Infraestrutura** em conjunto com o **Responsável pela Demanda** quando qualquer critério da tabela de ativação for atingido. Prazo máximo para decisão: **15 minutos** após identificação do problema.
