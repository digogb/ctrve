---
name: glossario-ifpug
description: Glossario IFPUG CPM 4.3.1 em PT-BR com exemplos TJCE para termos de contagem.
---

# Glossario IFPUG — Referencia Rapida TJCE

Vocabulario essencial para contagem de pontos de funcao com exemplos do dominio judicial do TJCE. Consulte quando precisar classificar uma funcao mas a terminologia nao esta obvia.

## Tipos de Funcao

### Funcoes de Dados

**ALI (Arquivo Logico Interno)** — Grupo de dados logicamente relacionado, mantido pela aplicacao em contagem atraves de pelo menos uma Entrada Externa (EE).

*Exemplos TJCE:* Processo judicial, Parte (autor/reu), Movimentacao processual, Decisao, Anexo processual, Usuario interno.

Criterio: se a aplicacao grava/atualiza/exclui, e candidato a ALI.

**AIE (Arquivo de Interface Externa)** — Grupo de dados referenciado pela aplicacao mas mantido por outra aplicacao.

*Exemplos TJCE:* CPF/CNPJ (consultado em base da Receita), Endereco de CEP (correios), Tabela de feriados nacionais, Cadastro de magistrados (mantido por sistema central do CNJ).

Criterio: se a aplicacao so le, nao grava — e AIE.

### Funcoes Transacionais

**EE (Entrada Externa)** — Processo elementar que processa dados vindos de fora da fronteira da aplicacao e mantem ao menos um ALI.

*Exemplos TJCE:* Cadastrar processo, Atualizar parte, Registrar movimentacao, Anexar peca, Arquivar processo, Distribuir processo por sorteio.

Criterio: CRUD, mudanca de estado, importacao — sempre que ALI muda.

**SE (Saida Externa)** — Processo elementar que apresenta dados ao usuario com calculo, derivacao ou logica de negocio adicional.

*Exemplos TJCE:* Relatorio de prazos vencidos (calcula dias), Estatistica por vara, Mapa de produtividade (agregacoes), Extrato de custas com totalizacao.

Criterio: saida que NAO e apenas repeticao direta dos dados armazenados.

**CE (Consulta Externa)** — Processo elementar que apresenta dados sem calculo ou derivacao adicional.

*Exemplos TJCE:* Consulta de processo por numero, Listagem de partes, Visualizacao de decisao, Busca por nome.

Criterio: apresenta dado como esta armazenado — sem agregacao, sem calculo, sem derivacao.

## Atributos de Sizing

**DER (Data Element Type)** — Campo unico, nao-recursivo, significativo ao usuario.

- Em ALI/AIE: atributos unicos da entidade (CPF, nome, data de nascimento = 3 DER). Relacionamentos contam como 1 DER (chave estrangeira). Atributos repetidos ou de auditoria tecnica (created_at) nao contam.
- Em transacoes: campos de entrada + campos de saida + mensagens visiveis (grupos de botoes/acoes funcionalmente equivalentes contam como 1 DER coletivo).

**RLR (Record Element Type)** — Subgrupo logico de dados dentro de uma ALI/AIE.

- Uma entidade sem subtipos: RLR = 1 (ela mesma).
- Entidade com subtipos opcionais/obrigatorios (ex: Parte com Pessoa Fisica / Pessoa Juridica): RLR = numero de subtipos.
- Heranca (Processo -> ProcessoCivel / ProcessoCriminal / ProcessoTrabalhista): RLR = 3 (um por subtipo distinto).

**ALR (Arquivo Logico Referenciado)** — Numero de ALI ou AIE tocados pela transacao (leitura ou escrita).

- EE "Cadastrar processo" que grava em Processo e le Parte e Vara: ALR = 3.
- CE "Consulta de processo" que le apenas Processo: ALR = 1.

## Matrizes de Complexidade (resumo)

| Funcao | Baixa | Media | Alta |
|--------|-------|-------|------|
| ALI | 7 PF | 10 PF | 15 PF |
| AIE | 5 PF | 7 PF | 10 PF |
| EE | 3 PF | 4 PF | 6 PF |
| SE | 4 PF | 5 PF | 7 PF |
| CE | 3 PF | 4 PF | 6 PF |

**ALI/AIE:** DER bands {1-19 / 20-50 / >50} x RLR bands {1 / 2-5 / >5}
**EE:** DER bands {1-4 / 5-15 / >15} x ALR bands {0-1 / 2 / >2}
**SE/CE:** DER bands {1-5 / 6-19 / >19} x ALR bands {0-1 / 2-3 / >3}

Classificacao vem sempre do `calculate-fp.py` — nao memorize matrizes, invoque o script.

## Contagem de Projeto

**Contagem de Desenvolvimento (Nova):** conta todas as funcoes entregues pela primeira vez.

**Contagem de Manutencao / Enhancement (CFP):** conta apenas deltas — funcoes ADDED, CHANGED, DELETED. Funcoes UNCHANGED nao entram.

**Correcao em Garantia:** correcao de defeito em entrega ainda sob garantia. Contratualmente PF = 0.

## Fator de Ajuste (VAF)

Calculado a partir das 14 Caracteristicas Gerais do Sistema (GSC), cada uma pontuada 0-5. Soma = TDI (0 a 70).

```
VAF = (TDI * 0.01) + 0.65
PF Ajustado = PF Brutos * VAF
```

TDI = 35 resulta em VAF = 1.00 (neutro). Ver `gsc-14-characteristics.md` para o checklist.
