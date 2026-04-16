---
name: exemplo-contagem-tjce
description: Exemplo resolvido de contagem APF para uma sprint TJCE curta — referencia pedagogica.
---

# Exemplo Resolvido — Sprint "Consulta de Processos"

Entrega hipotetica TJCE com 3 US, 4 RN, 2 entidades. Serve como referencia de como aplicar IFPUG CPM 4.3.1 passo a passo no dominio judicial.

## Entrada

**user-stories.md:**
- US-001: Cadastrar processo judicial com numero CNJ, partes e valor da causa
- US-002: Consultar processo por numero ou por nome da parte
- US-003: Listar processos em tramitacao por vara

**business-rules.md:**
- RN-001: Numero CNJ deve seguir padrao NNNNNNN-DD.AAAA.J.TR.OOOO
- RN-002: Processo nao pode ser cadastrado sem ao menos um autor e um reu
- RN-003: Consulta por nome e case-insensitive e busca em autores e reus
- RN-004: Listagem exibe apenas processos com status = "em tramitacao"

**data-model.md:**
- Processo (numero_cnj, data_autuacao, valor_causa, status, vara_id) — 5 atributos + 1 FK
- Parte (processo_id, nome, cpf_cnpj, tipo [autor|reu]) — 3 atributos + 1 FK, 2 subtipos

## Contagem

### Funcoes de Dados

**FD-001 — Processo (ALI)**
- DER: 6 (5 atributos + FK vara) — banda {1-19}
- RLR: 1 (sem subtipos distintos) — banda {1}
- `calculate-fp.py --type ALI --der 6 --rlr 1` → Baixa → 7 PF
- Fonte: US-001, US-002, US-003, RN-001

**FD-002 — Parte (ALI)**
- DER: 4 (3 atributos + FK processo) — banda {1-19}
- RLR: 2 (autor, reu) — banda {2-5}
- `calculate-fp.py --type ALI --der 4 --rlr 2` → Baixa → 7 PF
- Fonte: US-001, RN-002

### Funcoes Transacionais

**FT-001 — Cadastrar processo (EE)**
- DER: ~12 (6 campos processo + 4 campos parte × N + botao salvar + mensagens de validacao RN-001/RN-002) — banda {5-15}
- ALR: 2 (Processo, Parte) — banda {2}
- `calculate-fp.py --type EE --der 12 --alr 2` → Media → 4 PF
- Fonte: US-001, RN-001, RN-002

**FT-002 — Consultar processo (CE)**
- DER: ~10 (filtros numero/nome + colunas do resultado + mensagem "nenhum encontrado") — banda {6-19}
- ALR: 2 (Processo, Parte — para busca por nome) — banda {2-3}
- `calculate-fp.py --type CE --der 10 --alr 2` → Media → 4 PF
- Fonte: US-002, RN-003

**FT-003 — Listar processos por vara (CE)**
- DER: ~7 (filtro vara + colunas da listagem) — banda {6-19}
- ALR: 1 (Processo) — banda {0-1}
- `calculate-fp.py --type CE --der 7 --alr 1` → Baixa → 3 PF
- Fonte: US-003, RN-004

### Resumo

- PF Brutos: 7 + 7 + 4 + 4 + 3 = **25 PF**
- TDI assumido: 35 (neutro, sem avaliacao individual das 14 GSC)
- VAF: 1.00
- **PF Ajustado: 25 PF**

### Distribuicao

- ALI: 2 funcoes, 14 PF (56%)
- EE: 1 funcao, 4 PF (16%)
- CE: 2 funcoes, 7 PF (28%)

## Observacoes do Analista

- RN-001 (formato CNJ) e absorvida pela EE FT-001 via DER de mensagem de validacao — nao gera funcao separada
- RN-003 (case-insensitive, busca em autores+reus) justifica ALR=2 em FT-002 mas nao eleva complexidade sozinha
- Parte possui RLR=2 (autor, reu) — classificacao conservadora. Se o spec fosse explicito que sao entidades distintas em tabelas diferentes, seriam duas ALI.

## Licao para aplicar em outras contagens

1. **Entidade sempre antes de transacao**: ALI/AIE sao contados uma unica vez, transacoes referenciam eles via ALR
2. **DER inclui mensagens**: validacoes visiveis ao usuario contam como DER, mas mensagens relacionadas sao agrupadas
3. **Default prudente na duvida**: na fronteira entre Baixa/Media, prefira Baixa se DER/RLR tem apenas o minimo para entrar na banda superior
4. **Principio anti-duplicacao**: mesmo que 3 US mencionem Processo, so ha 1 ALI Processo
