# Contagem Detalhada de Pontos de Função — CTRVE v1.0.0

**Projeto:** CTRVE — Controle de Transporte e Recebimento de Veículos Externos  
**Versão:** 1.0.0 (implantação inicial — nova funcionalidade)  
**Método:** IFPUG CPM 4.3.1  
**Tipo de contagem:** Projeto de Desenvolvimento (Development Project Function Point Count)  
**Data:** 2026-04-28  
**Responsável:** tjce-agent-apf  

---

## 1. Escopo e Fronteira

A fronteira do sistema delimita o CTRVE como uma aplicação única composta por:
- Frontend React (SPA)
- Backend FastAPI
- Banco de dados PostgreSQL (tabelas internas: `users`, `checklists`)

Não há sistemas externos integrados (nenhum EIF identificado).

---

## 2. Arquivos Lógicos Internos (ILF)

Os ILFs são grupos de dados logicamente relacionados, mantidos e controlados **dentro** da fronteira do sistema.

### ILF-01 — Usuário (`users`)

| Atributo         | Coluna BD        | Observação                         |
|------------------|------------------|------------------------------------|
| id               | id               | Chave primária, gerada pelo sistema |
| username         | username         | Identificador de login, único       |
| full_name        | full_name        | Nome completo                       |
| matricula        | matricula        | Matrícula funcional, única          |
| hashed_password  | hashed_password  | Senha cifrada (bcrypt)              |
| role             | role             | Enum: responsavel / motorista       |
| is_active        | is_active        | Flag de ativação da conta           |
| created_at       | created_at       | Timestamp de criação                |

**Contagem de DETs:** 8 (id, username, full_name, matricula, hashed_password, role, is_active, created_at)  
**Contagem de RETs:** 1 (um único subtipo lógico de registro de usuário)

**Tabela de complexidade ILF (IFPUG CPM 4.3.1):**

| RETs \ DETs | 1–19 DETs | 20–50 DETs | 51+ DETs |
|-------------|-----------|------------|----------|
| 1 RET       | **Baixa** | Baixa      | Média    |
| 2–5 RETs    | Baixa     | Média      | Alta     |
| 6+ RETs     | Média     | Alta       | Alta     |

**ILF-01:** 1 RET × 8 DETs → **Complexidade Baixa = 7 PF**

---

### ILF-02 — Checklist (`checklists`)

Tabela com dois grupos lógicos de dados distintos: **Entrega** e **Devolução**.

| Atributo                          | RET        | Observação                              |
|-----------------------------------|------------|-----------------------------------------|
| id                                | —          | Chave primária                          |
| placa                             | Entrega    | Placa do veículo                        |
| unidade                           | Entrega    | Unidade responsável                     |
| subunidade                        | Entrega    | Subunidade (opcional)                   |
| motorista                         | Entrega    | Nome do motorista                       |
| matricula_motorista               | Entrega    | Matrícula do motorista                  |
| quilometragem_inicial             | Entrega    | KM no momento da entrega                |
| status                            | Entrega    | Enum: entregue / devolvido              |
| is_locked                         | Entrega    | Flag de bloqueio após salvamento        |
| itens                             | Entrega    | JSON com 20 itens e status ok/nao_ok    |
| avarias                           | Entrega    | JSON com pontos de avaria (x, y, vista, tipo) |
| nivel_combustivel                 | Entrega    | Enum: 1/4, 2/4, 3/4, 4/4               |
| data_entrega                      | Entrega    | Timestamp de entrega                    |
| assinatura_responsavel            | Entrega    | Imagem base64 da assinatura             |
| assinatura_motorista              | Entrega    | Imagem base64 da assinatura             |
| observacoes                       | Entrega    | Texto livre de observações              |
| created_at                        | Entrega    | Timestamp de criação do registro        |
| quilometragem_final               | Devolução  | KM no momento da devolução              |
| data_devolucao                    | Devolução  | Timestamp de devolução                  |
| itens_devolucao                   | Devolução  | JSON com 20 itens e status ok/nao_ok    |
| nivel_combustivel_devolucao       | Devolução  | Enum: 1/4, 2/4, 3/4, 4/4               |
| assinatura_responsavel_devolucao  | Devolução  | Imagem base64                           |
| assinatura_motorista_devolucao    | Devolução  | Imagem base64                           |
| observacoes_devolucao             | Devolução  | Texto livre de observações da devolução |

**Contagem de DETs:** 24 (todos os campos da tabela, exceto id que é chave interna sem valor para o usuário — nota: id é exposto na resposta e visível ao usuário como Nº de Controle, portanto conta como DET)  
**Revisão:** id é exibido ao usuário como "Nº de Controle" e "Nº", portanto é um DET válido → **24 DETs**  
**Contagem de RETs:** 2 (subgrupo Entrega e subgrupo Devolução)

**ILF-02:** 2 RETs × 24 DETs → **Complexidade Baixa = 7 PF**

> Justificativa: Com 2 RETs e 24 DETs, a intersecção na tabela IFPUG cai na célula (2–5 RETs × 20–50 DETs) = **Média = 10 PF**.

**Correção:** 2 RETs × 24 DETs → tabela (2–5 RETs, 20–50 DETs) = **Complexidade Média = 10 PF**

---

**Subtotal ILF:**

| ID      | Nome       | DETs | RETs | Complexidade | PF  |
|---------|------------|------|------|--------------|-----|
| ILF-01  | Usuário    | 8    | 1    | Baixa        | 7   |
| ILF-02  | Checklist  | 24   | 2    | Média        | 10  |
| **Total ILF** |      |      |      |              | **17** |

---

## 3. Arquivos de Interface Externa (EIF)

Nenhum arquivo externo é referenciado ou consultado. O sistema não consome dados de outros sistemas.

**Total EIF: 0 PF**

---

## 4. Entradas Externas (EI — External Input)

Uma EI é uma transação elementar que processa dados que entram na fronteira do sistema e mantém um ou mais ILFs.

### Critérios de complexidade EI (IFPUG CPM 4.3.1):

| FTRs \ DETs | 1–4 DETs | 5–15 DETs | 16+ DETs |
|-------------|----------|-----------|----------|
| 0–1 FTR     | Baixa    | Baixa     | Média    |
| 2 FTRs      | Baixa    | Média     | Alta     |
| 3+ FTRs     | Média    | Alta      | Alta     |

Pesos: Baixa = 3 PF, Média = 4 PF, Alta = 6 PF.

---

### EI-01 — Login (POST /v1/auth/login)

**US:** US-001 | **RN:** RN-001, RN-002

**Processo:** Recebe username e password; valida credenciais contra ILF-01; se válido, emite access_token (JWT no body) e seta cookie httponly com refresh_token. Não altera dados persistidos.

> Nota metodológica: Login não mantém ILF (não grava dados). Contudo, segundo IFPUG CPM 4.3.1, transações que referenciam dados para autenticação e retornam dados derivados (tokens) são classificadas como EI quando há validação de dados de entrada.  
> Em contagens IFPUG conservadoras, login é frequentemente tratado como **EI** por realizar validação com leitura de ILF e alteração de estado implícito (cookie de sessão). Adota-se essa abordagem.

**DETs de entrada:** username, password (2 DETs)  
**FTRs referenciados:** ILF-01 (1 FTR)

**EI-01:** 1 FTR × 2 DETs → **Complexidade Baixa = 3 PF**

---

### EI-02 — Refresh de Sessão (POST /v1/auth/refresh)

**US:** US-001 (implícito, renovação de sessão) | **RN:** RN-001, RN-002

**Processo:** Lê cookie refresh_token; valida token e existência do usuário em ILF-01; emite novo access_token e renova o cookie. Referencia ILF-01. Processo elementar distinto de EI-01 (entrada diferente, lógica distinta).

**DETs de entrada:** refresh_token (cookie) = 1 DET  
**FTRs referenciados:** ILF-01 (1 FTR)

**EI-02:** 1 FTR × 1 DET → **Complexidade Baixa = 3 PF**

---

### EI-03 — Logout (POST /v1/auth/logout)

**Nota:** O endpoint POST /v1/auth/logout não está implementado no código analisado (não há rota `logout` em `auth.py`). Consta apenas na especificação de endpoints fornecida.

> Decisão: Como o endpoint foi declarado no escopo do projeto, inclui-se na contagem como funcionalidade prevista (desenvolvimento). Processo: invalida o cookie de sessão no cliente.

**DETs de entrada:** nenhum dado de entrada persistido (apenas limpa cookie)  
**FTRs referenciados:** 0 (não mantém ILF)

> Segundo IFPUG, um logout que apenas remove cookie sem alterar ILF pode ser questionável como EI. Contudo, é um processo elementar identificável pelo usuário. Classifica-se como EI de complexidade mínima.

**DETs de entrada:** refresh_token (cookie) = 1 DET  
**FTRs referenciados:** 0 FTRs mantidos (não persiste nada)  

**EI-03:** 0 FTR × 1 DET → **Complexidade Baixa = 3 PF**

---

### EI-04 — Cadastrar Usuário (POST /v1/users)

**US:** US-002 | **RN:** RN-003, RN-004

**Processo:** Recebe dados do novo usuário; valida senha (política), matrícula (unicidade, formato), username (unicidade), role; persiste em ILF-01.

**DETs de entrada:** username, full_name, matricula, password, confirmPassword (frontend), role = 6 DETs  
**FTRs referenciados:** ILF-01 (leitura para unicidade + escrita) = 1 FTR

**EI-04:** 1 FTR × 6 DETs → **Complexidade Baixa = 3 PF**

---

### EI-05 — Criar Novo Checklist (POST /v1/checklists)

**US:** US-003 | **RN:** RN-005, RN-006, RN-007, RN-008

**Processo:** Recebe dados básicos do checklist; valida formato de placa, matrícula numérica, duplicidade de entrega aberta; persiste registro inicial em ILF-02.

**DETs de entrada:** placa, unidade, subunidade, motorista, matricula_motorista, quilometragem_inicial = 6 DETs  
**FTRs referenciados:** ILF-02 (leitura para validação de duplicidade + escrita) = 1 FTR

**EI-05:** 1 FTR × 6 DETs → **Complexidade Baixa = 3 PF**

---

### EI-06 — Preencher e Salvar Checklist de Entrega (PATCH /v1/checklists/{id}/entrega)

**US:** US-005, US-006, US-007, US-010, US-011 | **RN:** RN-010, RN-011, RN-012, RN-013, RN-014, RN-015, RN-016, RN-020, RN-021, RN-022

**Processo:** Recebe 20 itens de verificação (ok/nao_ok), nível de combustível, data/hora de entrega, lista de avarias (mapa gráfico com x, y, vista, tipo), assinatura do responsável (base64), assinatura do motorista (base64), observações; valida status do checklist, valida que não está bloqueado, valida assinaturas (formato PNG base64, tamanho máximo), valida exatamente 20 itens com status definido; persiste e bloqueia (is_locked=True) em ILF-02.

**DETs de entrada:**
- itens (array de 20 objetos com nome + status) = conta-se como 2 DETs (o campo itens e o atributo status repetido — conforme IFPUG, campos repetidos dentro de grupo contam como 1 DET por atributo único do grupo: nome, status = 2 DETs do grupo itens)
- nivel_combustivel = 1 DET
- data_entrega = 1 DET
- avarias (array: x, y, vista, tipo) = 4 DETs do grupo avarias
- assinatura_responsavel = 1 DET
- assinatura_motorista = 1 DET
- observacoes = 1 DET  
**Total DETs:** 11 DETs

**FTRs referenciados:** ILF-02 (leitura + escrita) = 1 FTR

**EI-06:** 1 FTR × 11 DETs → **Complexidade Baixa = 3 PF**

> Nota: Mesmo com 11 DETs, a célula (1 FTR × 5–15 DETs) = Baixa = 3 PF.

---

### EI-07 — Preencher e Salvar Checklist de Devolução (PATCH /v1/checklists/{id}/devolucao)

**US:** US-008, US-009, US-010, US-011 | **RN:** RN-010, RN-011, RN-012, RN-017, RN-018, RN-019, RN-020, RN-021, RN-022

**Processo:** Recebe 20 itens de verificação da devolução, nível de combustível devolução, quilometragem final, data/hora de devolução, assinatura do responsável devolução, assinatura do motorista devolução, observações devolução; valida status (is_locked=True e status=entregue), valida quilometragem final >= inicial, valida data devolução >= data entrega; persiste em ILF-02 e altera status para devolvido.

**DETs de entrada:**
- itens (nome, status) = 2 DETs
- nivel_combustivel = 1 DET
- quilometragem_final = 1 DET
- data_devolucao = 1 DET
- assinatura_responsavel = 1 DET
- assinatura_motorista = 1 DET
- observacoes = 1 DET  
**Total DETs:** 8 DETs

**FTRs referenciados:** ILF-02 (leitura + escrita) = 1 FTR

**EI-07:** 1 FTR × 8 DETs → **Complexidade Baixa = 3 PF**

---

### EI-08 — Cancelar Checklist (DELETE /v1/checklists/{id})

**US:** US-013 | **RN:** RN-024

**Processo:** Recebe o ID do checklist; valida que não está bloqueado (apenas checklists em preenchimento — is_locked=False — podem ser cancelados); exclui o registro de ILF-02.

**DETs de entrada:** checklist_id (parâmetro de rota) = 1 DET  
**FTRs referenciados:** ILF-02 (leitura para validação + exclusão) = 1 FTR

**EI-08:** 1 FTR × 1 DET → **Complexidade Baixa = 3 PF**

---

**Subtotal EI:**

| ID     | Nome                            | DETs | FTRs | Complexidade | PF |
|--------|---------------------------------|------|------|--------------|-----|
| EI-01  | Login                           | 2    | 1    | Baixa        | 3  |
| EI-02  | Refresh de Sessão               | 1    | 1    | Baixa        | 3  |
| EI-03  | Logout                          | 1    | 0    | Baixa        | 3  |
| EI-04  | Cadastrar Usuário               | 6    | 1    | Baixa        | 3  |
| EI-05  | Criar Novo Checklist            | 6    | 1    | Baixa        | 3  |
| EI-06  | Salvar Checklist de Entrega     | 11   | 1    | Baixa        | 3  |
| EI-07  | Salvar Checklist de Devolução   | 8    | 1    | Baixa        | 3  |
| EI-08  | Cancelar Checklist              | 1    | 1    | Baixa        | 3  |
| **Total EI** |                           |      |      |              | **24** |

---

## 5. Saídas Externas (EO — External Output)

Uma EO é uma transação elementar que envia dados para fora da fronteira do sistema e inclui **lógica de processamento adicional** (derivação, cálculo ou transformação) além da simples recuperação de dados.

### Critérios de complexidade EO (IFPUG CPM 4.3.1):

| FTRs \ DETs | 1–5 DETs | 6–19 DETs | 20+ DETs |
|-------------|----------|-----------|----------|
| 0–1 FTR     | Baixa    | Baixa     | Média    |
| 2–3 FTRs    | Baixa    | Média     | Alta     |
| 4+ FTRs     | Média    | Alta      | Alta     |

Pesos: Baixa = 4 PF, Média = 5 PF, Alta = 7 PF.

---

### EO-01 — Gerar PDF do Checklist (GET /v1/checklists/{id}/pdf)

**US:** US-012 | **RN:** RN-023

**Processo:** Recupera dados do checklist de ILF-02; **transforma** os dados em documento PDF usando WeasyPrint (geração de relatório formatado, renderização de imagens de assinatura como base64, composição de layout HTML→PDF); valida que o checklist está bloqueado (is_locked=True) antes de gerar; valida formato das assinaturas via regex; retorna arquivo binário PDF com Content-Disposition para download.

Este é um processo elementar com **lógica de processamento adicional significativa** (conversão HTML→PDF, validação de segurança das assinaturas, geração de nome de arquivo dinâmico), qualificando-o como EO.

**DETs de saída:** conteúdo do PDF (arquivo binário = 1 DET de dados) + Content-Disposition header = 2 DETs funcionais  
**FTRs referenciados:** ILF-02 (1 FTR)

**EO-01:** 1 FTR × 2 DETs → **Complexidade Baixa = 4 PF**

---

### EO-02 — Token de Acesso (resposta do Login / Refresh)

**Nota metodológica:** A emissão de JWT como resultado do login/refresh já foi contabilizada nas EIs (EI-01 e EI-02). Em contagem IFPUG rigorosa, quando a saída de dados derivada (token) é o único resultado de uma EI, não se conta separadamente uma EO — a EI absorve o processamento. Portanto, **EO-02 não é contada separadamente**.

---

**Subtotal EO:**

| ID     | Nome                  | DETs | FTRs | Complexidade | PF |
|--------|-----------------------|------|------|--------------|-----|
| EO-01  | Gerar PDF Checklist   | 2    | 1    | Baixa        | 4  |
| **Total EO** |               |      |      |              | **4** |

---

## 6. Consultas Externas (EQ — External Query)

Uma EQ é uma transação elementar que envia dados para fora da fronteira do sistema sem lógica de processamento adicional (apenas recuperação e apresentação de dados).

### Critérios de complexidade EQ (IFPUG CPM 4.3.1):

| FTRs \ DETs | 1–5 DETs | 6–19 DETs | 20+ DETs |
|-------------|----------|-----------|----------|
| 0–1 FTR     | Baixa    | Baixa     | Média    |
| 2–3 FTRs    | Baixa    | Média     | Alta     |
| 4+ FTRs     | Média    | Alta      | Alta     |

Pesos: Baixa = 3 PF, Média = 4 PF, Alta = 6 PF.

---

### EQ-01 — Consultar Usuário Logado (GET /v1/users/me)

**US:** US-001 (contexto de autenticação) | **RN:** RN-001

**Processo:** Recupera dados do usuário autenticado (via token JWT) de ILF-01; retorna id, username, full_name, matricula, role, is_active (sem hashed_password).

**DETs de saída (UserResponse):** id, username, full_name, matricula, role, is_active = 6 DETs  
**FTRs referenciados:** ILF-01 (1 FTR)

**EQ-01:** 1 FTR × 6 DETs → **Complexidade Baixa = 3 PF**

---

### EQ-02 — Buscar Checklists por Placa (GET /v1/checklists?placa=...)

**US:** US-004 | **RN:** RN-009

**Processo:** Recupera lista de checklists de ILF-02, com filtro opcional por placa (LIKE/contains), ordenados por created_at DESC; retorna lista de ChecklistResponse.

**DETs de saída (ChecklistResponse, campos relevantes exibidos na listagem):** id, placa, unidade, status, is_locked, created_at + placa (filtro de entrada) = considera-se os DETs do tipo de dado retornado.

Conforme IFPUG, para EQ que retorna lista, os DETs são contados para um único tipo de registro mais o controle da lista. Os campos retornados no ChecklistResponse são: id, placa, unidade, subunidade, motorista, matricula_motorista, quilometragem_inicial, status, is_locked, itens, nivel_combustivel, data_entrega, avarias, assinatura_responsavel, assinatura_motorista, quilometragem_final, data_devolucao, itens_devolucao, nivel_combustivel_devolucao, assinatura_responsavel_devolucao, assinatura_motorista_devolucao, observacoes, observacoes_devolucao, created_at = **24 DETs** de saída.

**FTRs referenciados:** ILF-02 (1 FTR)

**EQ-02:** 1 FTR × 24 DETs → **Complexidade Média = 4 PF**

> Justificativa: 1 FTR × 20+ DETs → célula (0–1 FTR, 20+ DETs) = Média = 4 PF.

---

### EQ-03 — Consultar Checklist por ID (GET /v1/checklists/{id})

**US:** US-004, US-005, US-008 (ao carregar a tela de preenchimento) | **RN:** RN-009

**Processo:** Recupera um checklist específico de ILF-02 pelo ID; retorna ChecklistResponse completo com todos os campos.

**DETs de saída:** mesmo conjunto de 24 DETs do ChecklistResponse  
**FTRs referenciados:** ILF-02 (1 FTR)

> Nota: EQ-02 e EQ-03 são processos elementares distintos (EQ-02 retorna lista com filtro, EQ-03 retorna um único registro por chave primária). Ambos qualificam como EQs independentes.

**EQ-03:** 1 FTR × 24 DETs → **Complexidade Média = 4 PF**

---

**Subtotal EQ:**

| ID     | Nome                           | DETs | FTRs | Complexidade | PF |
|--------|--------------------------------|------|------|--------------|-----|
| EQ-01  | Consultar Usuário Logado       | 6    | 1    | Baixa        | 3  |
| EQ-02  | Buscar Checklists (lista)      | 24   | 1    | Média        | 4  |
| EQ-03  | Consultar Checklist por ID     | 24   | 1    | Média        | 4  |
| **Total EQ** |                          |      |      |              | **11** |

---

## 7. Análise das User Stories vs. Elementos Contados

| US     | Descrição                              | Elementos APF cobertos                          |
|--------|----------------------------------------|-------------------------------------------------|
| US-001 | Login no sistema                       | EI-01 (login), EI-02 (refresh), EQ-01 (users/me) |
| US-002 | Cadastro de usuário                    | EI-04 (POST /users)                             |
| US-003 | Criar novo checklist                   | EI-05 (POST /checklists)                        |
| US-004 | Buscar checklist por placa             | EQ-02 (GET /checklists), EQ-03 (GET /checklists/{id}) |
| US-005 | Preencher checklist de entrega (20 itens, combustível) | EI-06 (PATCH /entrega)        |
| US-006 | Registrar avarias no mapa gráfico      | EI-06 (campo avarias dentro do PATCH /entrega)  |
| US-007 | Coletar assinaturas na entrega         | EI-06 (campos assinatura dentro do PATCH /entrega) |
| US-008 | Preencher checklist de devolução       | EI-07 (PATCH /devolucao)                        |
| US-009 | Coletar assinaturas na devolução       | EI-07 (campos assinatura dentro do PATCH /devolucao) |
| US-010 | Registrar observações em texto livre   | EI-06 e EI-07 (campo observacoes em ambos)      |
| US-011 | Salvar checklist com validação completa | EI-06 e EI-07 (lógica de validação + is_locked) |
| US-012 | Gerar e compartilhar PDF               | EO-01 (GET /pdf)                                |
| US-013 | Cancelar checklist                     | EI-08 (DELETE /checklists/{id})                 |
| US-014 | Navegar entre telas                    | Não gera elemento APF (navegação é UI, sem transação de dados) |
| —      | ILF Usuário                            | ILF-01                                          |
| —      | ILF Checklist                          | ILF-02                                          |
| —      | Logout                                 | EI-03 (POST /auth/logout)                       |

**Nota US-014:** Navegação entre telas (React Router, guardedNavigate, stepper) é comportamento de interface de usuário sem transação de dados elementar. Segundo IFPUG CPM 4.3.1, não configura EI, EO ou EQ.

**Nota US-006, US-007, US-009, US-010:** Os dados de avarias, assinaturas e observações são campos **dentro das transações** EI-06 e EI-07, não transações separadas. IFPUG proíbe contar a mesma transação elementar múltiplas vezes; os campos adicionais elevam os DETs da EI mas não criam novas EIs.

---

## 8. Consolidação dos Pontos de Função Não Ajustados (PFNA)

| Tipo | Complexidade | Qtd | Peso | PF    |
|------|-------------|-----|------|-------|
| ILF  | Baixa       | 1   | 7    | 7     |
| ILF  | Média       | 1   | 10   | 10    |
| EIF  | —           | 0   | —    | 0     |
| EI   | Baixa       | 8   | 3    | 24    |
| EI   | Média       | 0   | 4    | 0     |
| EI   | Alta        | 0   | 6    | 0     |
| EO   | Baixa       | 1   | 4    | 4     |
| EO   | Média       | 0   | 5    | 0     |
| EO   | Alta        | 0   | 7    | 0     |
| EQ   | Baixa       | 1   | 3    | 3     |
| EQ   | Média       | 2   | 4    | 8     |
| EQ   | Alta        | 0   | 6    | 0     |
| **TOTAL** |        |     |      | **56** |

---

## 9. Inventário Completo dos Elementos Funcionais

| Seq | Tipo | ID     | Nome                              | DETs | RET/FTR | Complexidade | PF |
|-----|------|--------|-----------------------------------|------|---------|--------------|-----|
| 1   | ILF  | ILF-01 | Usuário (tabela users)            | 8    | 1 RET   | Baixa        | 7  |
| 2   | ILF  | ILF-02 | Checklist (tabela checklists)     | 24   | 2 RETs  | Média        | 10 |
| 3   | EI   | EI-01  | Login                             | 2    | 1 FTR   | Baixa        | 3  |
| 4   | EI   | EI-02  | Refresh de Sessão                 | 1    | 1 FTR   | Baixa        | 3  |
| 5   | EI   | EI-03  | Logout                            | 1    | 0 FTR   | Baixa        | 3  |
| 6   | EI   | EI-04  | Cadastrar Usuário                 | 6    | 1 FTR   | Baixa        | 3  |
| 7   | EI   | EI-05  | Criar Novo Checklist              | 6    | 1 FTR   | Baixa        | 3  |
| 8   | EI   | EI-06  | Salvar Checklist de Entrega       | 11   | 1 FTR   | Baixa        | 3  |
| 9   | EI   | EI-07  | Salvar Checklist de Devolução     | 8    | 1 FTR   | Baixa        | 3  |
| 10  | EI   | EI-08  | Cancelar Checklist                | 1    | 1 FTR   | Baixa        | 3  |
| 11  | EO   | EO-01  | Gerar PDF do Checklist            | 2    | 1 FTR   | Baixa        | 4  |
| 12  | EQ   | EQ-01  | Consultar Usuário Logado (me)     | 6    | 1 FTR   | Baixa        | 3  |
| 13  | EQ   | EQ-02  | Buscar Checklists por Placa       | 24   | 1 FTR   | Média        | 4  |
| 14  | EQ   | EQ-03  | Consultar Checklist por ID        | 24   | 1 FTR   | Média        | 4  |
| **TOTAL** | | |                                   |      |         |              | **56** |

---

## 10. Rastreabilidade RN → Elementos APF

| RN     | Descrição resumida                                | Elemento APF     |
|--------|---------------------------------------------------|------------------|
| RN-001 | Autenticação obrigatória (JWT)                    | EI-01, EI-02     |
| RN-002 | Controle de sessão / expiração de token           | EI-02, EI-03     |
| RN-003 | Unicidade de matrícula no cadastro                | EI-04            |
| RN-004 | Política de senha (8+, maiúscula, minúscula, número) | EI-04         |
| RN-005 | Campos obrigatórios no novo checklist             | EI-05            |
| RN-006 | Formato de placa (Mercosul ou antigo)             | EI-05            |
| RN-007 | Matrícula do motorista numérica                   | EI-05            |
| RN-008 | Bloqueio de entrega duplicada por placa           | EI-05            |
| RN-009 | Busca de checklist por placa (LIKE)               | EQ-02, EQ-03     |
| RN-010 | Exatamente 20 itens com status ok/nao_ok          | EI-06, EI-07     |
| RN-011 | Nível de combustível obrigatório (1/4 a 4/4)      | EI-06, EI-07     |
| RN-012 | Data/hora obrigatória                             | EI-06, EI-07     |
| RN-013 | Registro de avarias no mapa gráfico               | EI-06            |
| RN-014 | Coordenadas x,y + vista + tipo de avaria          | EI-06            |
| RN-015 | Assinatura do responsável obrigatória (canvas PNG base64) | EI-06, EI-07 |
| RN-016 | Assinatura do motorista obrigatória (canvas PNG base64) | EI-06, EI-07 |
| RN-017 | Quilometragem final >= inicial                    | EI-07            |
| RN-018 | Data de devolução >= data de entrega              | EI-07            |
| RN-019 | Status muda para "devolvido" ao salvar devolução  | EI-07            |
| RN-020 | Observações em texto livre (entrega e devolução)  | EI-06, EI-07     |
| RN-021 | Confirmação antes de salvar (dialog modal)        | EI-06, EI-07     |
| RN-022 | Bloqueio após salvamento (is_locked=True)         | EI-06, EI-07     |
| RN-023 | Geração de PDF com dados completos do checklist   | EO-01            |
| RN-024 | Cancelamento apenas de checklists não bloqueados  | EI-08            |
| RN-025 | Guardar alterações não salvas ao navegar          | US-014 (sem APF) |

---

*Fim da contagem detalhada.*
