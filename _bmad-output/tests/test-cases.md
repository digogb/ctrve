# Casos de Teste — CTRVE (Checklist de Transporte de Veículos)

Documento gerado a partir das 25 Regras de Negócio (RN-001 a RN-025) do CTRVE.
Rastreabilidade: cada caso de teste está vinculado a pelo menos uma RN, indicada no título.

---

## Autenticação e Acesso

Casos de teste para login, expiração de sessão e cadastro de usuários.

### CT-001 — Login com credenciais válidas (RN-001)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário cadastrado com credenciais ativas |
| **Passos** | 1. Acessar tela de login; 2. Informar usuário e senha válidos; 3. Submeter formulário |
| **Resultado Esperado** | Sistema cria sessão autenticada, exibe MSG-024 ("Login realizado com sucesso") e redireciona à tela principal |
| **Tipo** | integração |

### CT-002 — Login com credenciais inválidas (RN-001)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Tela de login acessível |
| **Passos** | 1. Informar usuário existente com senha incorreta; 2. Submeter formulário |
| **Resultado Esperado** | Sistema exibe MSG-001 ("Usuário ou senha inválidos") sem indicar qual campo está incorreto. Nenhuma sessão é criada |
| **Tipo** | integração |

### CT-003 — Login com usuário inexistente (RN-001)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Tela de login acessível |
| **Passos** | 1. Informar usuário que não existe na base; 2. Submeter formulário |
| **Resultado Esperado** | Sistema exibe MSG-001 (mesma mensagem de credenciais inválidas). Tempo de resposta similar ao cenário de senha incorreta para evitar enumeração de usuários |
| **Tipo** | integração |

### CT-004 — Expiração de sessão por inatividade (RN-002)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Usuário autenticado com sessão ativa |
| **Passos** | 1. Autenticar no sistema; 2. Aguardar período de inatividade configurado (30 min); 3. Tentar acessar funcionalidade protegida |
| **Resultado Esperado** | Sistema encerra sessão, redireciona à tela de login e exibe MSG-002 ("Sua sessão expirou por inatividade") |
| **Tipo** | integração |

### CT-005 — Cadastro de usuário com matrícula única (RN-003)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Responsável autenticado; matrícula a ser cadastrada não existe na base |
| **Passos** | 1. Acessar formulário de cadastro; 2. Preencher nome, matrícula nova, perfil, usuário e senha válida; 3. Submeter |
| **Resultado Esperado** | Sistema persiste o cadastro e exibe MSG-023 ("Usuário cadastrado com sucesso") |
| **Tipo** | integração |

### CT-006 — Cadastro de usuário com matrícula duplicada (RN-003)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Responsável autenticado; matrícula alvo já existe na base |
| **Passos** | 1. Acessar formulário de cadastro; 2. Informar matrícula já cadastrada; 3. Submeter |
| **Resultado Esperado** | Sistema impede o cadastro e exibe MSG-003 ("A matrícula informada já está cadastrada no sistema") |
| **Tipo** | integração |

### CT-007 — Senha atende requisitos (RN-004)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de cadastro aberto |
| **Passos** | 1. Informar senha "Senha123"; 2. Submeter formulário com demais campos válidos |
| **Resultado Esperado** | Sistema aceita a senha e prossegue com o cadastro |
| **Tipo** | unitário |

### CT-008 — Senha sem letra maiúscula é rejeitada (RN-004)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de cadastro aberto |
| **Passos** | 1. Informar senha "senha123" (sem maiúscula); 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-004 indicando que é necessária ao menos uma letra maiúscula |
| **Tipo** | unitário |

### CT-009 — Senha com menos de 8 caracteres é rejeitada (RN-004)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de cadastro aberto |
| **Passos** | 1. Informar senha "Se1" (3 caracteres); 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-004 indicando o mínimo de 8 caracteres |
| **Tipo** | unitário |

### CT-010 — Senha sem número é rejeitada (RN-004)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de cadastro aberto |
| **Passos** | 1. Informar senha "SenhaForte" (sem número); 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-004 indicando que é necessário ao menos um número |
| **Tipo** | unitário |

---

## Informações Gerais do Checklist

Casos de teste para campos obrigatórios, validação de placa/matrícula, bloqueio de duplicata e busca.

### CT-011 — Campos obrigatórios preenchidos corretamente (RN-005)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Responsável autenticado; formulário de novo checklist de entrega aberto |
| **Passos** | 1. Preencher Placa, Unidade, Motorista, Matrícula e Quilometragem Inicial; 2. Prosseguir |
| **Resultado Esperado** | Sistema aceita os dados e avança para a próxima seção do checklist |
| **Tipo** | integração |

### CT-012 — Campos obrigatórios com lacunas exibem erro (RN-005)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Responsável autenticado; formulário de novo checklist de entrega aberto |
| **Passos** | 1. Deixar campo "Placa" e "Quilometragem Inicial" vazios; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-005 listando "Placa" e "Quilometragem Inicial" como não preenchidos |
| **Tipo** | integração |

### CT-013 — Placa formato Mercosul válida (RN-006)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de informações gerais aberto |
| **Passos** | 1. Informar placa "ABC1D23"; 2. Submeter |
| **Resultado Esperado** | Sistema aceita a placa sem erro |
| **Tipo** | unitário |

### CT-014 — Placa formato antigo válida (RN-006)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de informações gerais aberto |
| **Passos** | 1. Informar placa "ABC-1234"; 2. Submeter |
| **Resultado Esperado** | Sistema aceita a placa sem erro |
| **Tipo** | unitário |

### CT-015 — Placa formato inválido rejeitada (RN-006)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de informações gerais aberto |
| **Passos** | 1. Informar placa "12345"; 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-006 ("Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234)") |
| **Tipo** | unitário |

### CT-016 — Matrícula numérica aceita (RN-007)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de informações gerais aberto |
| **Passos** | 1. Informar matrícula "123456"; 2. Submeter |
| **Resultado Esperado** | Sistema aceita o valor sem erro |
| **Tipo** | unitário |

### CT-017 — Matrícula não numérica rejeitada (RN-007)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Formulário de informações gerais aberto |
| **Passos** | 1. Informar matrícula "ABC123"; 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-007 ("O campo Matrícula aceita apenas valores numéricos") |
| **Tipo** | unitário |

### CT-018 — Bloqueio de entrega duplicada para mesma placa (RN-008)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Veículo com placa "XYZ1A23" já possui checklist de entrega sem devolução concluída |
| **Passos** | 1. Tentar criar novo checklist de entrega para placa "XYZ1A23"; 2. Submeter |
| **Resultado Esperado** | Sistema impede a criação e exibe MSG-008 ("Já existe um checklist de entrega aberto para o veículo de placa XYZ1A23") |
| **Tipo** | integração |

### CT-019 — Entrega permitida após devolução concluída (RN-008)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Veículo com placa "XYZ1A23" teve entrega e devolução concluídas |
| **Passos** | 1. Criar novo checklist de entrega para placa "XYZ1A23" |
| **Resultado Esperado** | Sistema permite a criação do novo checklist de entrega |
| **Tipo** | integração |

### CT-020 — Busca por placa completa retorna resultados (RN-009)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Existem checklists cadastrados para placa "ABC1D23" |
| **Passos** | 1. Informar "ABC1D23" no campo de busca; 2. Submeter |
| **Resultado Esperado** | Sistema retorna lista de checklists cuja placa contenha "ABC1D23", ordenados por data de entrega decrescente |
| **Tipo** | integração |

### CT-021 — Busca por placa parcial retorna resultados (RN-009)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Existem checklists para placas "ABC1D23" e "ABC2E45" |
| **Passos** | 1. Informar "ABC" no campo de busca; 2. Submeter |
| **Resultado Esperado** | Sistema retorna checklists cuja placa contenha "ABC" |
| **Tipo** | integração |

### CT-022 — Busca sem resultado exibe mensagem (RN-009)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Nenhum checklist cadastrado para placa "ZZZ9Z99" |
| **Passos** | 1. Informar "ZZZ9Z99" no campo de busca; 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-009 ("Nenhum checklist encontrado para a placa informada") |
| **Tipo** | integração |

---

## Checklist de Entrega

Casos de teste para verificação dos 20 itens, combustível, data/horário, avarias e assinaturas na entrega.

### CT-023 — Todos os 20 itens verificados permite salvamento (RN-010)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com informações gerais preenchidas |
| **Passos** | 1. Marcar os 20 itens como OK ou Não OK; 2. Preencher demais campos obrigatórios; 3. Salvar |
| **Resultado Esperado** | Sistema aceita o checklist e prossegue com o salvamento |
| **Tipo** | integração |

### CT-024 — Itens não verificados bloqueiam salvamento (RN-010)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com 18 de 20 itens respondidos |
| **Passos** | 1. Deixar 2 itens sem resposta; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-010 listando os 2 itens não verificados |
| **Tipo** | integração |

### CT-025 — Seleção exclusiva de nível de combustível (RN-011)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega aberto na seção de combustível |
| **Passos** | 1. Selecionar "2/4"; 2. Selecionar "3/4" |
| **Resultado Esperado** | Sistema desmarca "2/4" e mantém apenas "3/4" selecionado |
| **Tipo** | unitário |

### CT-026 — Combustível não selecionado bloqueia salvamento (RN-011)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega preenchido exceto combustível |
| **Passos** | 1. Não selecionar nenhum nível de combustível; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-011 ("Selecione o nível de combustível do veículo") |
| **Tipo** | integração |

### CT-027 — Data e horário registrados corretamente (RN-012)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega aberto |
| **Passos** | 1. Informar data "22/04/2026" e horário "14:30"; 2. Prosseguir |
| **Resultado Esperado** | Sistema aceita os valores e os associa ao checklist |
| **Tipo** | unitário |

### CT-028 — Data ou horário ausente bloqueia salvamento (RN-012)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega preenchido exceto data/horário |
| **Passos** | 1. Deixar campo de data vazio; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-012 ("Informe a data e o horário da entrega") |
| **Tipo** | integração |

### CT-029 — Ponto de avaria com tipo selecionado é aceito (RN-013)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega aberto na seção de mapa de avarias |
| **Passos** | 1. Clicar em ponto no mapa do veículo; 2. Selecionar tipo "Amassado"; 3. Confirmar |
| **Resultado Esperado** | Sistema registra o ponto com coordenadas (x, y), vista e tipo "Amassado" |
| **Tipo** | unitário |

### CT-030 — Ponto de avaria sem tipo bloqueia salvamento (RN-013)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com ponto marcado no mapa sem tipo selecionado |
| **Passos** | 1. Marcar ponto no mapa; 2. Não selecionar tipo; 3. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-013 ("Selecione o tipo de avaria para cada ponto marcado no mapa do veículo") |
| **Tipo** | integração |

### CT-031 — Mapa de avarias não exibido na devolução (RN-014)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de devolução aberto |
| **Passos** | 1. Acessar checklist de devolução; 2. Verificar seções disponíveis |
| **Resultado Esperado** | Seção de mapa de avarias não é exibida na interface |
| **Tipo** | e2e |

### CT-032 — Ambas as assinaturas preenchidas permitem salvamento (RN-015)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega preenchido; campos de assinatura disponíveis |
| **Passos** | 1. Assinar no canvas do Responsável; 2. Assinar no canvas do Motorista; 3. Salvar |
| **Resultado Esperado** | Sistema aceita as assinaturas e prossegue com o salvamento |
| **Tipo** | e2e |

### CT-033 — Assinatura do Responsável ausente bloqueia salvamento (RN-015)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com assinatura do Motorista preenchida, Responsável vazia |
| **Passos** | 1. Assinar apenas o canvas do Motorista; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-014 indicando que a assinatura do Responsável é obrigatória |
| **Tipo** | e2e |

### CT-034 — Assinatura do Motorista ausente bloqueia salvamento (RN-015)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com assinatura do Responsável preenchida, Motorista vazia |
| **Passos** | 1. Assinar apenas o canvas do Responsável; 2. Tentar salvar |
| **Resultado Esperado** | Sistema exibe MSG-014 indicando que a assinatura do Motorista é obrigatória |
| **Tipo** | e2e |

### CT-035 — Assinatura bloqueada após salvar (RN-016)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega salvo com sucesso |
| **Passos** | 1. Abrir checklist salvo; 2. Tentar interagir com os campos de assinatura |
| **Resultado Esperado** | Campos de assinatura não permitem edição. Assinaturas são exibidas como imagem |
| **Tipo** | e2e |

---

## Checklist de Devolução

Casos de teste para pré-requisito de entrega, herança de dados e consistência de quilometragem/data.

### CT-036 — Devolução permitida com entrega prévia concluída (RN-017)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega salvo para Nº de Controle 001 |
| **Passos** | 1. Iniciar checklist de devolução para Nº de Controle 001 |
| **Resultado Esperado** | Sistema permite iniciar a devolução e carrega dados da entrega |
| **Tipo** | integração |

### CT-037 — Devolução bloqueada sem entrega prévia (RN-017)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Nenhuma entrega registrada para Nº de Controle 999 |
| **Passos** | 1. Tentar iniciar checklist de devolução para Nº de Controle 999 |
| **Resultado Esperado** | Sistema exibe MSG-015 ("Não é possível iniciar a devolução. Não foi encontrada entrega concluída para o Nº de Controle 999") |
| **Tipo** | integração |

### CT-038 — Dados herdados da entrega na devolução (RN-018)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Entrega concluída com Placa "ABC1D23", Unidade "SECLOG", Motorista "João Silva", Matrícula "123456", Km Inicial "50000" |
| **Passos** | 1. Iniciar devolução para o mesmo Nº de Controle |
| **Resultado Esperado** | Sistema preenche automaticamente Placa, Unidade, Subunidade, Motorista, Matrícula e Quilometragem Inicial com os valores da entrega. Campos herdados não são editáveis |
| **Tipo** | integração |

### CT-039 — Campos herdados não são editáveis na devolução (RN-018)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de devolução aberto com dados herdados |
| **Passos** | 1. Tentar editar o campo "Placa" herdado; 2. Tentar editar o campo "Motorista" herdado |
| **Resultado Esperado** | Campos herdados estão desabilitados para edição |
| **Tipo** | e2e |

### CT-040 — Quilometragem Final válida (RN-019)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Devolução aberta com Quilometragem Inicial de entrega = 50000 |
| **Passos** | 1. Informar Quilometragem Final = 50500; 2. Submeter |
| **Resultado Esperado** | Sistema aceita o valor sem erro |
| **Tipo** | unitário |

### CT-041 — Quilometragem Final menor que Inicial rejeitada (RN-019)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Devolução aberta com Quilometragem Inicial de entrega = 50000 |
| **Passos** | 1. Informar Quilometragem Final = 49000; 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-016 ("A Quilometragem Final (49000) não pode ser inferior à Quilometragem Inicial (50000)") |
| **Tipo** | unitário |

### CT-042 — Data de Devolução válida (RN-019)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Devolução aberta com Data de Entrega = 20/04/2026 |
| **Passos** | 1. Informar Data de Devolução = 22/04/2026; 2. Submeter |
| **Resultado Esperado** | Sistema aceita a data sem erro |
| **Tipo** | unitário |

### CT-043 — Data de Devolução anterior à Entrega rejeitada (RN-019)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Devolução aberta com Data de Entrega = 20/04/2026 |
| **Passos** | 1. Informar Data de Devolução = 19/04/2026; 2. Submeter |
| **Resultado Esperado** | Sistema exibe MSG-017 ("A Data de Devolução não pode ser anterior à Data de Entrega (20/04/2026)") |
| **Tipo** | unitário |

---

## Observações

Casos de teste para campo de observações em texto livre.

### CT-044 — Observação preenchida é persistida (RN-020)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega preenchido e válido |
| **Passos** | 1. Preencher campo de observações com "Veículo com arranhão no para-choque dianteiro"; 2. Salvar checklist |
| **Resultado Esperado** | Sistema persiste a observação associada ao checklist |
| **Tipo** | integração |

### CT-045 — Observação vazia é aceita (RN-020)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega preenchido e válido |
| **Passos** | 1. Deixar campo de observações vazio; 2. Salvar checklist |
| **Resultado Esperado** | Sistema salva o checklist sem erro, campo de observações permanece vazio |
| **Tipo** | integração |

---

## Ações e Saída

Casos de teste para salvamento, confirmação, geração de PDF, cancelamento e navegação.

### CT-046 — Validação completa executada ao salvar (RN-021)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega com múltiplos campos inválidos (placa inválida, itens não verificados, assinatura ausente) |
| **Passos** | 1. Preencher placa com formato inválido; 2. Deixar 3 itens sem verificação; 3. Não assinar; 4. Clicar em "Salvar" |
| **Resultado Esperado** | Sistema exibe MSG-006, MSG-010 e MSG-014 simultaneamente. Checklist não é persistido |
| **Tipo** | e2e |

### CT-047 — Salvamento bem-sucedido exibe MSG-022 (RN-021)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega completamente preenchido e válido |
| **Passos** | 1. Preencher campos corretamente; 2. Clicar em "Salvar"; 3. Confirmar na caixa de diálogo |
| **Resultado Esperado** | Sistema persiste os dados e exibe MSG-022 ("Checklist salvo com sucesso") |
| **Tipo** | e2e |

### CT-048 — Confirmação antes de salvar (RN-022)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega válido, botão Salvar acionado |
| **Passos** | 1. Clicar em "Salvar"; 2. Observar diálogo de confirmação |
| **Resultado Esperado** | Sistema exibe MSG-018 ("Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados") |
| **Tipo** | e2e |

### CT-049 — Cancelamento da confirmação de salvamento (RN-022)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Diálogo de confirmação de salvamento exibido |
| **Passos** | 1. Clicar em "Cancelar" no diálogo de confirmação |
| **Resultado Esperado** | Sistema fecha o diálogo e retorna ao formulário com dados preservados. Checklist não é persistido |
| **Tipo** | e2e |

### CT-050 — Geração de PDF com dados completos (RN-023)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega salvo com dados gerais, itens, combustível, avarias, assinaturas e observações |
| **Passos** | 1. Abrir checklist salvo; 2. Clicar em "Compartilhar" ou "Imprimir" |
| **Resultado Esperado** | Sistema gera PDF contendo: dados gerais, itens verificados com status, nível de combustível, mapa de avarias, assinaturas, observações. Exibe MSG-025 ("PDF gerado com sucesso") |
| **Tipo** | e2e |

### CT-051 — PDF indisponível para checklist não salvo (RN-023)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega em preenchimento (não salvo) |
| **Passos** | 1. Verificar estado dos botões "Compartilhar" e "Imprimir" |
| **Resultado Esperado** | Botões desabilitados. Se hover/tooltip exibido, mostra MSG-019 |
| **Tipo** | e2e |

### CT-052 — Cancelamento com confirmação descarta dados (RN-024)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega em preenchimento com dados parciais |
| **Passos** | 1. Clicar em "Cancelar"; 2. Sistema exibe MSG-020; 3. Confirmar o cancelamento |
| **Resultado Esperado** | Sistema descarta dados preenchidos e redireciona à tela principal |
| **Tipo** | e2e |

### CT-053 — Cancelamento negado mantém dados (RN-024)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega em preenchimento; diálogo de cancelamento exibido |
| **Passos** | 1. Clicar em "Cancelar"; 2. Sistema exibe MSG-020; 3. Negar o cancelamento |
| **Resultado Esperado** | Sistema fecha o diálogo e retorna ao formulário com dados preservados |
| **Tipo** | e2e |

### CT-054 — Alerta ao navegar com dados não salvos (RN-025)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Checklist de entrega em preenchimento com dados alterados |
| **Passos** | 1. Preencher pelo menos um campo; 2. Clicar em "Voltar" |
| **Resultado Esperado** | Sistema exibe MSG-021 ("Existem dados não salvos neste formulário. Deseja sair sem salvar?") com opções de continuar editando ou sair |
| **Tipo** | e2e |

### CT-055 — Navegação sem dados alterados não exibe alerta (RN-025)

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Tela de checklist aberta sem nenhum campo alterado |
| **Passos** | 1. Clicar em "Voltar" sem preencher nenhum campo |
| **Resultado Esperado** | Sistema navega para a tela anterior sem exibir alerta |
| **Tipo** | e2e |
