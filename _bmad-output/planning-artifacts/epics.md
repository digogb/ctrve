# Epics — CTRVE (Checklist de Transporte de Veículos)

---

## Epic 1: Autenticação e Gestão de Usuários

Capacidade de autenticar usuários no sistema, gerenciar sessões e cadastrar novos usuários com controle de perfis (Responsável/Motorista).

### Story 1.1: Login no Sistema

Como Responsável ou Motorista, quero realizar login com minhas credenciais, para que eu possa acessar as funcionalidades do sistema de acordo com meu perfil.

**Critérios de Aceitação:**

- [ ] Sistema exibe tela de login com campos de usuário e senha
- [ ] Login bem-sucedido redireciona para a tela principal com MSG-024
- [ ] Login com credenciais inválidas exibe MSG-001 sem revelar qual campo está incorreto
- [ ] Sessão expira após 30 minutos de inatividade com MSG-002

**Regras de Negócio:** RN-001, RN-002

---

### Story 1.2: Cadastro de Usuário

Como Responsável, quero cadastrar novos usuários no sistema, para que motoristas e outros responsáveis possam acessar o sistema.

**Critérios de Aceitação:**

- [ ] Formulário de cadastro com nome, matrícula, perfil (Responsável ou Motorista), usuário e senha
- [ ] Sistema impede cadastro com matrícula já existente (MSG-003)
- [ ] Cadastro bem-sucedido exibe MSG-023
- [ ] Senha deve atender requisitos mínimos (MSG-004): 8+ caracteres, maiúscula, minúscula e número

**Regras de Negócio:** RN-003, RN-004

---

## Epic 2: Informações Gerais e Busca

Capacidade de criar um novo checklist com dados do veículo e do motorista, e de buscar checklists existentes pela placa.

### Story 2.1: Criar Novo Checklist

Como Responsável, quero criar um novo checklist informando os dados gerais do veículo, para que o processo de entrega seja iniciado com todas as informações de identificação registradas.

**Critérios de Aceitação:**

- [ ] Formulário exibe campos: Nº de Controle, Placa, Unidade, Subunidade, Motorista, Matrícula, Quilometragem Inicial
- [ ] Campos obrigatórios: Placa, Unidade, Motorista, Matrícula, Quilometragem Inicial (MSG-005)
- [ ] Placa validada no formato Mercosul (ABC1D23) ou antigo (ABC-1234) — MSG-006
- [ ] Matrícula aceita apenas valor numérico (MSG-007)
- [ ] Sistema não permite criar entrega se já existe entrega aberta para o veículo (MSG-008)

**Regras de Negócio:** RN-005, RN-006, RN-007, RN-008

---

### Story 2.2: Buscar Checklist por Placa

Como Responsável ou Motorista, quero buscar checklists existentes pela placa do veículo, para que eu possa consultar o histórico ou continuar um checklist em andamento.

**Critérios de Aceitação:**

- [ ] Campo de busca aceita placa parcial ou completa
- [ ] Resultados exibem lista ordenada por data de entrega decrescente
- [ ] Cada resultado exibe: Nº de Controle, Placa, Data de Entrega, Status (Entregue/Devolvido)
- [ ] Busca sem resultados exibe MSG-009

**Regras de Negócio:** RN-009

---

## Epic 3: Checklist de Entrega

Capacidade de registrar a entrega de um veículo: verificação dos 20 itens, nível de combustível, data/horário, mapa de avarias e assinaturas digitais.

### Story 3.1: Preencher Checklist de Entrega

Como Responsável, quero verificar os 20 itens do checklist de entrega, registrar o nível de combustível e informar a data/horário, para que as condições do veículo no momento da entrega fiquem documentadas.

**Critérios de Aceitação:**

- [ ] Exibe 20 itens de verificação organizados em duas colunas (Documentação/Equipamentos e Condições do Veículo)
- [ ] Cada item deve ser marcado como OK ou Não OK — nenhum pode ficar sem resposta (MSG-010)
- [ ] Nível de combustível com seleção exclusiva: 1/4, 2/4, 3/4 ou 4/4 (MSG-011)
- [ ] Data e horário da entrega obrigatórios (MSG-012)

**Regras de Negócio:** RN-010, RN-011, RN-012

---

### Story 3.2: Registrar Avarias no Mapa do Veículo

Como Responsável, quero marcar no mapa gráfico do veículo os locais onde existem avarias e classificá-las por tipo, para que o estado físico do veículo na entrega fique documentado visualmente.

**Critérios de Aceitação:**

- [ ] Mapa SVG exibe 4 vistas do veículo (topo, lateral esquerda, lateral direita, frontal/traseira)
- [ ] Permite marcar múltiplos pontos de avaria via onClick
- [ ] Cada ponto marcado exige seleção do tipo: Risco, Amassado ou Trincado (MSG-013)
- [ ] Permite remover ponto de avaria marcado por engano
- [ ] Mapa de avarias é opcional e não exibido no checklist de devolução

**Regras de Negócio:** RN-013, RN-014

---

### Story 3.3: Coletar Assinaturas na Entrega

Como Responsável, quero coletar a assinatura digital do Responsável e do Motorista no checklist de entrega, para que ambas as partes confirmem as condições registradas.

**Critérios de Aceitação:**

- [ ] Dois campos de assinatura: Responsável e Motorista via canvas HTML5
- [ ] Botão "Limpar" permite refazer a assinatura
- [ ] Ambas as assinaturas são obrigatórias para salvar (MSG-014)
- [ ] Assinaturas armazenadas como base64 e não editáveis após salvar

**Regras de Negócio:** RN-015, RN-016

---

## Epic 4: Checklist de Devolução

Capacidade de registrar a devolução de um veículo: verificação dos 20 itens, quilometragem final, data/horário, observações e assinaturas — com dados herdados da entrega.

### Story 4.1: Preencher Checklist de Devolução

Como Responsável, quero verificar os 20 itens do checklist de devolução, registrar o nível de combustível, quilometragem final e data/horário, para que as condições do veículo na devolução fiquem documentadas e comparáveis com a entrega.

**Critérios de Aceitação:**

- [ ] Devolução só pode ser iniciada se existe entrega concluída para o mesmo Nº de Controle (MSG-015)
- [ ] Dados de Informações Gerais herdados da entrega e não editáveis
- [ ] Quilometragem Final obrigatória e >= Quilometragem Inicial (MSG-016)
- [ ] Data de Devolução >= Data de Entrega (MSG-017)
- [ ] Mesmos 20 itens de verificação e regras de combustível da entrega

**Regras de Negócio:** RN-010, RN-011, RN-012, RN-017, RN-018, RN-019

---

### Story 4.2: Coletar Assinaturas na Devolução

Como Responsável, quero coletar a assinatura digital do Responsável e do Motorista no checklist de devolução, para que ambas as partes confirmem as condições do veículo no momento da devolução.

**Critérios de Aceitação:**

- [ ] Mesma mecânica de assinatura da entrega (canvas + limpar)
- [ ] Ambas obrigatórias para salvar (MSG-014)
- [ ] Não editáveis após salvar

**Regras de Negócio:** RN-015, RN-016

---

### Story 4.3: Registrar Observações

Como Responsável, quero registrar observações em texto livre sobre avarias ou situações relevantes, para que informações complementares que não cabem nos itens do checklist fiquem documentadas.

**Critérios de Aceitação:**

- [ ] Campo de texto livre disponível tanto na entrega quanto na devolução
- [ ] Campo opcional (pode ser salvo vazio)
- [ ] Sem limite rígido de caracteres visível ao usuário

**Regras de Negócio:** RN-020

---

## Epic 5: Ações, PDF e Navegação

Capacidade de salvar checklists com validação completa, gerar PDF para compartilhamento/impressão, cancelar preenchimento e navegar com proteção contra perda de dados.

### Story 5.1: Salvar Checklist

Como Responsável, quero salvar o checklist preenchido, para que os dados sejam persistidos e possam ser consultados posteriormente.

**Critérios de Aceitação:**

- [ ] Botão "Salvar" executa todas as validações antes de persistir
- [ ] Validações exibem todas as mensagens de erro de uma vez (MSG-005 a MSG-014, MSG-016, MSG-017)
- [ ] Exibe MSG-018 de confirmação antes de persistir definitivamente
- [ ] Salvamento bem-sucedido exibe MSG-022
- [ ] Após salvar, checklist não pode ser editado

**Regras de Negócio:** RN-021, RN-022

---

### Story 5.2: Gerar e Compartilhar PDF

Como Responsável ou Motorista, quero gerar um PDF do checklist completo e compartilhá-lo, para que o documento possa ser enviado ou arquivado fora do sistema.

**Critérios de Aceitação:**

- [ ] PDF gerado com WeasyPrint contém: dados gerais, itens verificados, combustível, mapa de avarias (se entrega), assinaturas, observações
- [ ] Geração bem-sucedida exibe MSG-025
- [ ] PDF disponível para download e impressão
- [ ] Botões desabilitados antes de salvar com MSG-019

**Regras de Negócio:** RN-023

---

### Story 5.3: Cancelar Checklist

Como Responsável, quero cancelar o preenchimento de um checklist antes de salvá-lo, para que eu possa descartar um checklist iniciado por engano sem que dados incorretos sejam persistidos.

**Critérios de Aceitação:**

- [ ] Botão "Cancelar" disponível enquanto o checklist não foi salvo
- [ ] Sistema exibe MSG-020 antes de descartar
- [ ] Após confirmação, dados são descartados e usuário retorna à tela principal
- [ ] Se cancelamento negado, formulário é mantido com dados preservados

**Regras de Negócio:** RN-024

---

### Story 5.4: Navegar entre Telas

Como Responsável ou Motorista, quero voltar à tela anterior sem perder o contexto, para que eu possa navegar pelo sistema de forma fluida.

**Critérios de Aceitação:**

- [ ] Botão "Voltar" retorna à tela anterior
- [ ] Se houver dados não salvos, sistema exibe MSG-021 antes de sair
- [ ] Sem dados alterados, navegação ocorre sem alerta

**Regras de Negócio:** RN-025
