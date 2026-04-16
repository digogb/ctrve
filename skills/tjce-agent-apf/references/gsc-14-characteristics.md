---
name: gsc-14-characteristics
description: Checklist das 14 Caracteristicas Gerais do Sistema IFPUG (GSC) com contexto TJCE para apurar TDI e VAF.
---

# GSC — 14 Caracteristicas Gerais do Sistema

Use este checklist quando o usuario precisar calcular o Fator de Ajuste (VAF). Cada caracteristica e pontuada de **0 a 5** conforme grau de influencia:

- **0** — Nenhuma influencia
- **1** — Influencia incidental
- **2** — Influencia moderada
- **3** — Influencia media
- **4** — Influencia significativa
- **5** — Influencia forte, em todo o sistema

Soma das 14 pontuacoes = **TDI** (0-70). Default neutro: todas com 3 → TDI = 42 → VAF = 1.07. Se usuario nao tem opiniao, usar TDI = 35 (VAF = 1.00) e registrar como decisao explicita.

## Checklist TJCE

| # | Caracteristica | O que considerar no TJCE |
|---|----------------|--------------------------|
| 1 | Comunicacao de Dados | Integracao com CNJ, PJe, tribunais superiores, outros sistemas TJCE? |
| 2 | Processamento Distribuido | Componentes em servidores distintos, filas, microservicos? |
| 3 | Performance | Requisitos de SLA para consulta processual em horario de pico? |
| 4 | Uso Intensivo de Configuracao | Roda em VMs compartilhadas com outros sistemas do tribunal? |
| 5 | Taxa de Transacoes | Volume de petições eletronicas por hora em periodo de pico? |
| 6 | Entrada de Dados Online | Percentual de transacoes online (vs. batch/importacao)? |
| 7 | Eficiencia do Usuario Final | Magistrados e servidores usam intensivamente — ergonomia prioritaria? |
| 8 | Atualizacao Online | ALI sao mantidos online (nao apenas batch)? |
| 9 | Complexidade de Processamento | Calculos de prazos processuais, distribuicao por sorteio, regras de competencia? |
| 10 | Reusabilidade | Componentes pensados para reuso em outras varas/comarcas? |
| 11 | Facilidade de Instalacao | Deploy automatizado em ambientes diversos do tribunal? |
| 12 | Facilidade Operacional | Backup, recovery, monitoracao — automaticos ou manuais? |
| 13 | Multiplos Locais | Roda em mais de um foro/comarca, com configuracao por local? |
| 14 | Facilitar Mudancas | Regras de negocio expostas para alteracao via configuracao? |

## Protocolo de Elicitacao

Quando o usuario nao forneceu TDI:

1. Perguntar: "Posso avaliar as 14 GSC contigo (1-2 min) ou prefere usar TDI neutro (35, VAF=1.00)?"
2. Se ele escolher avaliar: apresentar este checklist em blocos de 4-5 caracteristicas
3. Se ele escolher neutro: registrar no resumo "VAF = 1.00 (TDI neutro, 14 GSC nao avaliadas individualmente)"

## Em modo headless

Nao prompt. Usar TDI = 35 (VAF = 1.00) e marcar o resumo com `**VAF NEUTRO APLICADO — TDI nao fornecido em modo headless**` conforme SKILL.md.
