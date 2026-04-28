# CHANGELOG — CTRVE

## [1.0.0] — 2026-04-28

Versão inicial do sistema CTRVE (Checklist de Transporte de Veículos), desenvolvido em conformidade com a Resolução nº 641/2025 do TJCE.

### Adicionado

#### Epic 1 — Autenticação e Acesso
- Login com usuário e senha (JWT — access token + refresh token via httpOnly cookie)
- Sessão com expiração por inatividade configurável (padrão: 30 min)
- Cadastro de usuários com perfis Responsável e Motorista
- Validação de unicidade de matrícula e requisitos de senha

#### Epic 2 — Informações Gerais do Checklist
- Criação de novo checklist com campos: Nº de Controle, Placa, Unidade, Subunidade, Motorista, Matrícula, Quilometragem Inicial
- Validação de formato de placa (Mercosul ABC1D23 e antigo ABC-1234)
- Bloqueio de entrega duplicada para mesmo veículo sem devolução concluída
- Busca de checklists por placa (parcial ou completa), ordenados por data decrescente

#### Epic 3 — Checklist de Entrega
- 20 itens de verificação organizados em duas colunas (OK / Não OK)
- Nível de combustível com seleção exclusiva (1/4, 2/4, 3/4, 4/4)
- Mapa de avarias interativo com 4 vistas do veículo (topo, laterais, frontal/traseira) e 3 tipos (Risco, Amassado, Trincado)

#### Epic 4 — Assinaturas e Devolução
- Coleta de assinaturas digitais via canvas para Responsável e Motorista
- Imutabilidade de assinaturas após salvamento
- Checklist de devolução com validação de Quilometragem Final ≥ Inicial e Data Devolução ≥ Data Entrega
- Herança automática de dados da entrega correspondente

#### Epic 5 — Ações e Saída
- Campo de observações em texto livre (opcional) em entrega e devolução
- Salvamento com confirmação prévia e validação completa (todas as RNs)
- Geração e download de PDF do checklist completo (WeasyPrint)
- Compartilhamento via Web Share API e impressão
- Cancelamento com confirmação e descarte de dados
- Navegação com alerta de dados não salvos

#### Epic 6 — UX e Design Visual
- Design system TJCE (paleta azul institucional `#003366`/`#004080`)
- Interface responsiva (desktop e mobile)
- Gradiente de cabeçalho, cards de status coloridos, badges de severidade
- Dashboard com saudação, contadores e atalhos rápidos
- Tipografia e espaçamento padronizados

### Técnico
- **Backend:** FastAPI 0.135 + SQLModel + SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **PDF:** WeasyPrint + Jinja2 templates
- **Auth:** JWT (access token em memória, refresh token httpOnly cookie)
- **Testes:** 106 pytest (BE 97%) + 153 Vitest (FE 87%)
