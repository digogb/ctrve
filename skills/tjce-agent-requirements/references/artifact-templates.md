---
name: artifact-templates
type: reference
description: Exact markdown templates for the four PDS Unificado requirement artifacts. Ensures format consistency across TJCE projects.
---

# Templates dos Artefatos PDS Unificado

Use these templates exactly. Do not alter headers, column order, or section structure.

---

## 1. Visao do Produto (`product-vision.md`)

```markdown
# Visao do Produto — {Nome do Sistema}

## Escopo

{Descricao do que o sistema faz e quais problemas resolve. Lista de funcionalidades principais incluidas.}

### Funcionalidades Incluidas

- {Funcionalidade 1}
- {Funcionalidade 2}

## Fora de Escopo

- {Item explicitamente excluido 1}
- {Item explicitamente excluido 2}

## Premissas

- {Premissa 1 — condicao assumida como verdadeira para este projeto}
- {Premissa 2}

## Restricoes

- {Restricao 1 — limitacao tecnica, legal ou organizacional}
- {Restricao 2}
```

---

## 2. Estorias de Usuario (`user-stories.md`)

```markdown
# Estorias de Usuario — {Nome do Sistema}

## {Area Funcional 1}

### US-001 — {Titulo descritivo}

**Como** {perfil/ator}, **quero** {acao que deseja realizar}, **para que** {valor/beneficio obtido}.

**Criterios de Aceitacao:**

- [ ] {Criterio verificavel 1}
- [ ] {Criterio verificavel 2}

**Regras de Negocio:** RN-001, RN-002

---

### US-002 — {Titulo descritivo}

...
```

**Convencoes:**
- IDs sequenciais: US-001, US-002, US-003
- Agrupar por area funcional
- Cada estoria lista suas regras de negocio associadas
- Criterios de aceitacao sao verificaveis (testavel com sim/nao), devem cobrir o caminho feliz e pelo menos um caso excepcional
- Minimo 2, maximo 7 criterios por estoria — se precisar de mais, a estoria deve ser dividida

---

## 3. Regras de Negocio (`business-rules.md`)

```markdown
# Regras de Negocio — {Nome do Sistema}

| ID | Descricao | Condicao | Acao | Excecao | Estoria |
|----|-----------|----------|------|---------|---------|
| RN-001 | {O que a regra determina} | {Quando se aplica} | {O que o sistema faz} | {O que acontece no caso excepcional, ou "N/A — {justificativa}"} | US-001 |
| RN-002 | ... | ... | ... | ... | US-001, US-002 |
```

**Convencoes:**
- IDs sequenciais: RN-001, RN-002, RN-003
- Coluna Estoria: lista todas as US vinculadas, separadas por virgula
- Coluna Excecao: nunca vazia. Se nao ha excecao, usar "N/A — {motivo breve}"
- Cada regra deve ser especifica o suficiente para derivar pelo menos um caso de teste a partir de Condicao + Acao + Excecao

---

## 4. Mensagens do Sistema (`messages.md`)

```markdown
# Mensagens do Sistema — {Nome do Sistema}

| Codigo | Tipo | Texto | Regra |
|--------|------|-------|-------|
| MSG-001 | erro | {Texto exato exibido ao usuario} | RN-001 |
| MSG-002 | sucesso | {Texto exato exibido ao usuario} | RN-002 |
| MSG-003 | validacao | {Texto exato exibido ao usuario} | RN-003 |
| MSG-004 | confirmacao | {Texto exato exibido ao usuario} | RN-001 |
```

**Convencoes:**
- IDs sequenciais: MSG-001, MSG-002, MSG-003
- Tipos validos (exatamente estes): `erro`, `sucesso`, `validacao`, `confirmacao`
- Coluna Texto: texto final exibido ao usuario, em portugues formal
- Coluna Regra: lista todas as RN vinculadas, separadas por virgula
- O conjunto completo de mensagens DEVE conter pelo menos um exemplo de cada tipo
- Mensagens de erro devem ser claras sobre o que deu errado e o que o usuario pode fazer
- Mensagens de confirmacao usam tom neutro: "Deseja confirmar {acao}?"

---

## 5. Matriz de Rastreabilidade (`traceability-matrix.md`)

```markdown
# Matriz de Rastreabilidade — {Nome do Sistema}

| US | Titulo | RNs Vinculadas | MSGs Vinculadas | Cobertura |
|----|--------|----------------|-----------------|-----------|
| US-001 | {Titulo da estoria} | RN-001, RN-002 | MSG-001, MSG-002, MSG-003 | Completa |
| US-002 | {Titulo da estoria} | RN-003 | MSG-004 | Completa |
```

**Convencoes:**
- Uma linha por User Story
- Coluna Cobertura: "Completa" se todas as RNs tem MSGs vinculadas, "Parcial" caso contrario
- Serve como visao consolidada para revisao com stakeholders
