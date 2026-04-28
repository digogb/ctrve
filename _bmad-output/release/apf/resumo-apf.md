# Resumo Executivo — Contagem de Pontos de Função

**Projeto:** CTRVE — Controle de Transporte e Recebimento de Veículos Externos  
**Versão:** 1.0.0 (implantação inicial)  
**Tipo de contagem:** Projeto de Desenvolvimento (Development Project FPC)  
**Método:** IFPUG CPM 4.3.1  
**Data da contagem:** 2026-04-28  

---

## Resultado da Contagem

### Pontos de Função Não Ajustados (PFNA)

| Categoria                  | Qtd Elementos | PF    |
|----------------------------|:-------------:|------:|
| Arquivos Lógicos Internos  | 2             | 17    |
| Arquivos de Interface Externa | 0          | 0     |
| Entradas Externas (EI)     | 8             | 24    |
| Saídas Externas (EO)       | 1             | 4     |
| Consultas Externas (EQ)    | 3             | 11    |
| **TOTAL**                  | **14**        | **56** |

### **Total PFNA: 56 Pontos de Função Não Ajustados**

---

## Distribuição por Complexidade

| Tipo | Baixa | Média | Alta | Total PF |
|------|------:|------:|-----:|---------:|
| ILF  | 7     | 10    | —    | 17       |
| EIF  | —     | —     | —    | 0        |
| EI   | 24    | —     | —    | 24       |
| EO   | 4     | —     | —    | 4        |
| EQ   | 3     | 8     | —    | 11       |
| **Total** | **38** | **18** | **—** | **56** |

---

## Elementos Funcionais Identificados

### Arquivos Lógicos Internos (ILF) — 17 PF

| ID      | Nome                    | DETs | RETs | Complexidade | PF  |
|---------|-------------------------|------|------|--------------|-----|
| ILF-01  | Usuário (tabela users)  | 8    | 1    | Baixa        | 7   |
| ILF-02  | Checklist (tabela checklists) | 24 | 2  | Média        | 10  |

### Entradas Externas (EI) — 24 PF

| ID     | Endpoint / Função                  | US vinculada    | PF |
|--------|------------------------------------|-----------------|-----|
| EI-01  | POST /v1/auth/login                | US-001          | 3  |
| EI-02  | POST /v1/auth/refresh              | US-001          | 3  |
| EI-03  | POST /v1/auth/logout               | US-001          | 3  |
| EI-04  | POST /v1/users                     | US-002          | 3  |
| EI-05  | POST /v1/checklists                | US-003          | 3  |
| EI-06  | PATCH /v1/checklists/{id}/entrega  | US-005–007, US-010–011 | 3 |
| EI-07  | PATCH /v1/checklists/{id}/devolucao | US-008–011     | 3  |
| EI-08  | DELETE /v1/checklists/{id}         | US-013          | 3  |

### Saídas Externas (EO) — 4 PF

| ID     | Endpoint / Função               | US vinculada | PF |
|--------|---------------------------------|--------------|-----|
| EO-01  | GET /v1/checklists/{id}/pdf     | US-012       | 4  |

### Consultas Externas (EQ) — 11 PF

| ID     | Endpoint / Função               | US vinculada | PF |
|--------|---------------------------------|--------------|-----|
| EQ-01  | GET /v1/users/me                | US-001       | 3  |
| EQ-02  | GET /v1/checklists?placa=...    | US-004       | 4  |
| EQ-03  | GET /v1/checklists/{id}         | US-004       | 4  |

---

## Cobertura de Requisitos

- **User Stories cobertas:** 13 de 14 (US-014 não gera elemento APF — navegação é comportamento de UI sem transação de dados)
- **Regras de Negócio cobertas:** 25 de 25
- **Endpoints analisados:** 11 de 11

---

## Notas Metodológicas

1. **Tipo de contagem:** Development Project — todos os elementos são novos (sem baseline anterior).
2. **Fronteira:** sistema CTRVE isolado; nenhum EIF identificado (sem integração com sistemas externos).
3. **ILF-02 (Checklist):** classificado com 2 RETs pois a tabela `checklists` contém dois subgrupos lógicos distintos e reconhecíveis pelo usuário: dados de **Entrega** e dados de **Devolução**, com campos e validações independentes.
4. **EI vs. EO vs. EQ para PDF:** o endpoint GET /pdf foi classificado como EO (e não EQ) porque realiza **lógica de processamento adicional** — transformação HTML→PDF, validação de segurança de assinaturas via regex, geração dinâmica do documento — além da simples recuperação de dados.
5. **US-014 (Navegar entre telas):** navegação SPA com React Router e hook `useUnsavedChanges` não configura transação de dados elementar segundo IFPUG; nenhum ILF é mantido ou consultado exclusivamente por essa user story.
6. **Login/Logout:** tratados como EIs por envolverem validação e processamento de dados de autenticação. Logout incluído conforme escopo declarado do projeto, mesmo sem implementação verificada no código analisado.
7. **Fator de Ajuste:** não aplicado. O total apresentado é o **PFNA (Pontos de Função Não Ajustados)**, que é o valor padrão para fins de medição de tamanho funcional segundo IFPUG CPM 4.3.1.

---

## Uso Recomendado

O valor de **56 PFNA** deve ser utilizado para:
- Estimativa de esforço de desenvolvimento (via modelos como COCOMO II ou tabelas históricas do TJCE)
- Cálculo do custo por Ponto de Função (conforme tabela de preços vigente)
- Baseline de tamanho para futuras contagens de enhancement (CFP em manutenções corretivas e evolutivas)
- Documentação no processo de contratação e aceite da entrega v1.0.0
