# Estórias de Usuário — CTRVE (Checklist de Transporte de Veículos)

## Autenticação e Acesso

Estórias relacionadas ao login, sessão e cadastro de usuários no sistema.

### US-001 — Login no sistema

Como Responsável ou Motorista, quero realizar login com minhas credenciais, para que eu possa acessar as funcionalidades do sistema de acordo com meu perfil.

**Critérios de Aceitação:**

- [ ] Sistema exibe tela de login com campos de usuário e senha
- [ ] Login bem-sucedido redireciona para a tela principal
- [ ] Login com credenciais inválidas exibe mensagem de erro sem revelar qual campo está incorreto
- [ ] Sessão expira após período de inatividade

**Regras de Negócio:** RN-001, RN-002

---

### US-002 — Cadastro de usuário

Como Responsável, quero cadastrar novos usuários no sistema, para que motoristas e outros responsáveis possam acessar o sistema.

**Critérios de Aceitação:**

- [ ] Formulário de cadastro com nome, matrícula, perfil (Responsável ou Motorista), usuário e senha
- [ ] Sistema impede cadastro com matrícula já existente
- [ ] Senha deve atender requisitos mínimos de segurança

**Regras de Negócio:** RN-003, RN-004

---

## Informações Gerais do Checklist

Estórias para criação de novo checklist, preenchimento de dados do veículo e busca.

### US-003 — Criar novo checklist

Como Responsável, quero criar um novo checklist informando os dados gerais do veículo, para que o processo de entrega seja iniciado com todas as informações de identificação registradas.

**Critérios de Aceitação:**

- [ ] Formulário exibe campos: Nº de Controle, Placa, Unidade, Subunidade, Motorista, Matrícula, Quilometragem Inicial
- [ ] Campos obrigatórios: Placa, Unidade, Motorista, Matrícula, Quilometragem Inicial
- [ ] Placa validada no formato Mercosul (ABC1D23) ou antigo (ABC-1234)
- [ ] Matrícula aceita apenas valor numérico
- [ ] Sistema não permite criar checklist de entrega se já existe entrega aberta (sem devolução) para o mesmo veículo

**Regras de Negócio:** RN-005, RN-006, RN-007, RN-008

---

### US-004 — Buscar checklist por placa

Como Responsável ou Motorista, quero buscar checklists existentes pela placa do veículo, para que eu possa consultar o histórico ou continuar um checklist em andamento.

**Critérios de Aceitação:**

- [ ] Campo de busca aceita placa parcial ou completa
- [ ] Resultados exibem lista de checklists vinculados à placa, ordenados por data (mais recente primeiro)
- [ ] Cada resultado exibe: Nº de Controle, Placa, Data de Entrega, Status (Entregue/Devolvido)
- [ ] Busca sem resultados exibe mensagem informativa

**Regras de Negócio:** RN-009

---

## Checklist de Entrega

Estórias para verificação dos 20 itens, mapa de avarias e coleta de assinaturas na entrega.

### US-005 — Preencher checklist de entrega

Como Responsável, quero verificar os 20 itens do checklist de entrega, registrar o nível de combustível e informar a data/horário, para que as condições do veículo no momento da entrega fiquem documentadas.

**Critérios de Aceitação:**

- [ ] Exibe 20 itens de verificação organizados em duas colunas (Documentação/Equipamentos e Condições do Veículo)
- [ ] Cada item deve ser marcado como OK ou Não OK — nenhum pode ficar sem resposta
- [ ] Nível de combustível com seleção exclusiva: 1/4, 2/4, 3/4 ou 4/4
- [ ] Data e horário da entrega registrados
- [ ] Não é possível salvar com itens pendentes de verificação

**Regras de Negócio:** RN-010, RN-011, RN-012

---

### US-006 — Registrar avarias no mapa do veículo

Como Responsável, quero marcar no mapa gráfico do veículo os locais onde existem avarias e classificá-las por tipo, para que o estado físico do veículo na entrega fique documentado visualmente.

**Critérios de Aceitação:**

- [ ] Mapa exibe 4 vistas do veículo (topo, lateral esquerda, lateral direita, frontal/traseira)
- [ ] Permite marcar múltiplos pontos de avaria no mapa
- [ ] Cada ponto marcado exige seleção do tipo: Risco, Amassado ou Trincado
- [ ] Permite remover ponto de avaria marcado por engano
- [ ] Mapa de avarias é opcional (veículo pode não ter avarias)

**Regras de Negócio:** RN-013, RN-014

---

### US-007 — Coletar assinaturas na entrega

Como Responsável, quero coletar a assinatura digital do Responsável e do Motorista no checklist de entrega, para que ambas as partes confirmem as condições registradas.

**Critérios de Aceitação:**

- [ ] Dois campos de assinatura: Responsável e Motorista
- [ ] Assinatura coletada via canvas (desenho na tela)
- [ ] Botão "Limpar" permite refazer a assinatura
- [ ] Ambas as assinaturas são obrigatórias para salvar o checklist de entrega
- [ ] Assinaturas não podem ser editadas após o checklist ser salvo

**Regras de Negócio:** RN-015, RN-016

---

## Checklist de Devolução

Estórias para verificação dos 20 itens e coleta de assinaturas na devolução do veículo.

### US-008 — Preencher checklist de devolução

Como Responsável, quero verificar os 20 itens do checklist de devolução, registrar o nível de combustível, quilometragem final e data/horário, para que as condições do veículo na devolução fiquem documentadas e comparáveis com a entrega.

**Critérios de Aceitação:**

- [ ] Devolução só pode ser iniciada se existe entrega concluída para o mesmo Nº de Controle
- [ ] Dados de Informações Gerais herdados da entrega (placa, motorista, unidade, etc.)
- [ ] Quilometragem Final obrigatória e deve ser >= Quilometragem Inicial da entrega
- [ ] Data de Devolução >= Data de Entrega
- [ ] Mesmos 20 itens de verificação e regra de combustível da entrega

**Regras de Negócio:** RN-010, RN-011, RN-012, RN-017, RN-018, RN-019

---

### US-009 — Coletar assinaturas na devolução

Como Responsável, quero coletar a assinatura digital do Responsável e do Motorista no checklist de devolução, para que ambas as partes confirmem as condições do veículo no momento da devolução.

**Critérios de Aceitação:**

- [ ] Mesma mecânica de assinatura da entrega (canvas + limpar)
- [ ] Ambas obrigatórias para salvar
- [ ] Não editáveis após salvar

**Regras de Negócio:** RN-015, RN-016

---

## Observações

Estória para registro de informações complementares em texto livre.

### US-010 — Registrar observações

Como Responsável, quero registrar observações em texto livre sobre avarias ou situações relevantes, para que informações complementares que não cabem nos itens do checklist fiquem documentadas.

**Critérios de Aceitação:**

- [ ] Campo de texto livre disponível tanto na entrega quanto na devolução
- [ ] Campo opcional (pode ser salvo vazio)
- [ ] Sem limite rígido de caracteres visível ao usuário

**Regras de Negócio:** RN-020

---

## Ações e Saída

Estórias para salvar, gerar PDF, cancelar e navegar entre telas.

### US-011 — Salvar checklist

Como Responsável, quero salvar o checklist preenchido, para que os dados sejam persistidos e possam ser consultados posteriormente.

**Critérios de Aceitação:**

- [ ] Botão "Salvar" executa todas as validações antes de persistir
- [ ] Se validação falha, exibe mensagens específicas dos campos com problema
- [ ] Após salvar com sucesso, checklist não pode ser editado
- [ ] Exibe confirmação antes de salvar definitivamente

**Regras de Negócio:** RN-021, RN-022

---

### US-012 — Gerar e compartilhar PDF

Como Responsável ou Motorista, quero gerar um PDF do checklist completo e compartilhá-lo, para que o documento possa ser enviado ou arquivado fora do sistema.

**Critérios de Aceitação:**

- [ ] PDF gerado contém todas as informações: dados gerais, itens verificados, combustível, mapa de avarias (se entrega), assinaturas, observações
- [ ] PDF disponível para download
- [ ] Botão "Compartilhar" permite envio por e-mail (ou abre diálogo de compartilhamento do navegador)
- [ ] Botão "Imprimir" abre diálogo de impressão do navegador

**Regras de Negócio:** RN-023

---

### US-013 — Cancelar checklist

Como Responsável, quero cancelar o preenchimento de um checklist antes de salvá-lo, para que eu possa descartar um checklist iniciado por engano sem que dados incorretos sejam persistidos.

**Critérios de Aceitação:**

- [ ] Botão "Cancelar" disponível enquanto o checklist não foi salvo
- [ ] Sistema solicita confirmação antes de descartar
- [ ] Após confirmação, dados preenchidos são descartados e o usuário retorna à tela principal

**Regras de Negócio:** RN-024

---

### US-014 — Navegar entre telas

Como Responsável ou Motorista, quero voltar à tela anterior sem perder o contexto, para que eu possa navegar pelo sistema de forma fluida.

**Critérios de Aceitação:**

- [ ] Botão "Voltar" retorna à tela anterior
- [ ] Se houver dados não salvos, sistema alerta antes de sair

**Regras de Negócio:** RN-025
