# Manual do Usuário — CTRVE v1.0.0
**Checklist de Transporte de Veículos — Tribunal de Justiça do Estado do Ceará**

*Versão 1.0.0 | Abril de 2026*
*Elaborado em conformidade com a Resolução nº 641/2025*

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Perfis de Usuário](#2-perfis-de-usuário)
3. [Acessando o Sistema](#3-acessando-o-sistema)
   - 3.1 [Como fazer login](#31-como-fazer-login)
   - 3.2 [Sessão e inatividade](#32-sessão-e-inatividade)
   - 3.3 [Como sair do sistema (logout)](#33-como-sair-do-sistema-logout)
4. [Cadastro de Usuário](#4-cadastro-de-usuário)
5. [Tela Inicial (Dashboard)](#5-tela-inicial-dashboard)
6. [Fluxo Completo: do Novo Checklist ao PDF](#6-fluxo-completo-do-novo-checklist-ao-pdf)
   - 6.1 [Etapa 1 — Criar novo checklist (Informações Gerais)](#61-etapa-1--criar-novo-checklist-informações-gerais)
   - 6.2 [Etapa 2 — Preencher o checklist de entrega](#62-etapa-2--preencher-o-checklist-de-entrega)
   - 6.3 [Etapa 3 — Registrar avarias no mapa do veículo](#63-etapa-3--registrar-avarias-no-mapa-do-veículo)
   - 6.4 [Etapa 4 — Coletar assinaturas na entrega](#64-etapa-4--coletar-assinaturas-na-entrega)
   - 6.5 [Etapa 5 — Salvar o checklist de entrega](#65-etapa-5--salvar-o-checklist-de-entrega)
   - 6.6 [Etapa 6 — Preencher o checklist de devolução](#66-etapa-6--preencher-o-checklist-de-devolução)
   - 6.7 [Etapa 7 — Coletar assinaturas na devolução](#67-etapa-7--coletar-assinaturas-na-devolução)
   - 6.8 [Etapa 8 — Salvar o checklist de devolução](#68-etapa-8--salvar-o-checklist-de-devolução)
   - 6.9 [Etapa 9 — Gerar, compartilhar e imprimir o PDF](#69-etapa-9--gerar-compartilhar-e-imprimir-o-pdf)
7. [Como Buscar Checklists por Placa](#7-como-buscar-checklists-por-placa)
8. [Cancelar o Preenchimento](#8-cancelar-o-preenchimento)
9. [Navegar entre Telas](#9-navegar-entre-telas)
10. [Mensagens do Sistema](#10-mensagens-do-sistema)
11. [Perguntas Frequentes](#11-perguntas-frequentes)

---

## 1. Visão Geral do Sistema

O **CTRVE** (Checklist de Transporte de Veículos) é o sistema web do TJCE para formalizar, de forma digital, a entrega e a devolução de veículos oficiais. Ele substitui as fichas em papel, garantindo rastreabilidade, segurança das informações e conformidade com a Resolução nº 641/2025.

### O que o sistema permite fazer

| Funcionalidade | Quem pode usar |
|---|---|
| Criar e preencher checklist de entrega | Responsável |
| Registrar avarias no mapa do veículo | Responsável |
| Coletar assinaturas digitais | Responsável |
| Preencher checklist de devolução | Responsável |
| Gerar e baixar PDF do checklist | Responsável e Motorista |
| Compartilhar e imprimir PDF | Responsável e Motorista |
| Buscar checklists por placa | Responsável e Motorista |
| Cadastrar novos usuários | Responsável |

### O que o sistema não faz

- Não integra com o sistema SEI ou com outros sistemas do TJCE nesta versão.
- Não tira fotos do veículo.
- Não emite relatórios gerenciais ou dashboards estatísticos.
- Não controla cadastro de frota ou contratos de locação.

### Como acessar

O CTRVE é um sistema web. Acesse pelo navegador de qualquer dispositivo (computador, tablet ou celular) conectado à rede do TJCE ou à internet. Não é necessário instalar nenhum aplicativo.

---

## 2. Perfis de Usuário

O sistema possui dois perfis com permissões distintas.

### Responsável

Servidor do TJCE que realiza a vistoria física do veículo. O perfil Responsável tem acesso completo: cria checklists, preenche todos os campos, registra avarias, coleta assinaturas, salva e gera PDF. Também é o único perfil que pode cadastrar novos usuários.

### Motorista

Servidor ou terceiro que recebe ou devolve o veículo. O perfil Motorista pode consultar checklists existentes (buscando pela placa) e gerar/compartilhar o PDF de um checklist já salvo. O Motorista não pode criar nem preencher checklists.

---

## 3. Acessando o Sistema

### 3.1 Como fazer login

1. Abra o navegador e acesse o endereço do CTRVE fornecido pela TI do TJCE.
2. Na tela de login, informe seu **Usuário** e sua **Senha**.
3. Clique em **Entrar**.
4. Se as credenciais estiverem corretas, você será redirecionado para a tela inicial.

> **Atenção:** Se o login falhar, o sistema exibirá a mensagem "Usuário ou senha inválidos." sem indicar qual dos dois campos está errado. Isso é intencional para proteger a segurança da conta. Verifique ambos os campos e tente novamente.

### 3.2 Sessão e inatividade

Por segurança, a sessão é encerrada automaticamente após **30 minutos de inatividade**. Quando isso ocorrer, o sistema exibirá a mensagem:

> *"Sua sessão expirou por inatividade. Realize o login novamente para continuar."*

Você será redirecionado para a tela de login. Nenhum dado já salvo é perdido.

> **Dica:** Se estiver preenchendo um checklist longo, interaja com a tela periodicamente (clique em um item, por exemplo) para manter a sessão ativa.

### 3.3 Como sair do sistema (logout)

Clique no botão **Sair**, localizado no canto superior direito da barra de navegação. Você será desconectado e redirecionado para a tela de login.

---

## 4. Cadastro de Usuário

Somente o perfil **Responsável** pode cadastrar novos usuários.

1. Estando logado como Responsável, acesse o menu ou o endereço `/register` no navegador.
2. Preencha os campos do formulário:

| Campo | Descrição |
|---|---|
| Nome Completo | Nome do usuário a ser cadastrado |
| Matrícula | Número de matrícula funcional (somente números) |
| Usuário | Nome de login que o usuário utilizará para acessar o sistema |
| Perfil | Selecione "Responsável" ou "Motorista" |
| Senha | Senha de acesso (veja requisitos abaixo) |
| Confirmar Senha | Repita a senha para confirmação |

3. Clique em **Cadastrar**.
4. Se o cadastro for bem-sucedido, aparecerá a mensagem "Usuário cadastrado com sucesso" e o sistema retornará à tela de login.

### Requisitos da senha

A senha deve ter:
- No mínimo **8 caracteres**
- Pelo menos **uma letra maiúscula** (ex.: A, B, C...)
- Pelo menos **uma letra minúscula** (ex.: a, b, c...)
- Pelo menos **um número** (ex.: 1, 2, 3...)

Exemplos de senha válida: `Tjce2026!`, `Motorista1`, `AcessoCTRVE9`

### Regras de cadastro

- A **matrícula deve ser única**: o sistema não permite duas contas com a mesma matrícula.
- Se a matrícula já estiver em uso, aparecerá a mensagem "A matrícula informada já está cadastrada no sistema."

---

## 5. Tela Inicial (Dashboard)

Após o login, você verá a tela inicial com:

- **Saudação personalizada** com o seu nome e a data atual.
- **Contadores rápidos**:
  - *Em preenchimento* — checklists ainda não salvos definitivamente.
  - *Total do mês* — checklists criados no mês corrente.
  - *Total geral* — todos os checklists registrados no sistema.
- **Atalhos**:
  - Botão **Novo Checklist** (apenas para Responsável) — inicia o preenchimento.
  - Botão **Buscar por Placa** — abre a tela de busca.
- **Recentes** — lista dos três checklists mais recentes com placa, Nº de controle e status.

Clique em qualquer item da lista de recentes para abri-lo.

---

## 6. Fluxo Completo: do Novo Checklist ao PDF

O processo de registrar a entrega e devolução de um veículo segue as etapas abaixo. Todas as etapas de criação e preenchimento são exclusivas do perfil **Responsável**.

---

### 6.1 Etapa 1 — Criar novo checklist (Informações Gerais)

1. Na tela inicial, clique em **Novo Checklist**.
2. Preencha o formulário de **Informações Gerais**:

| Campo | Obrigatório | Observação |
|---|---|---|
| Nº de Controle | Sim | Número sequencial informado pelo Responsável |
| Placa | Sim | Formato Mercosul (ex.: `ABC1D23`) ou antigo (ex.: `ABC-1234`) |
| Unidade | Sim | Unidade do TJCE responsável pelo veículo |
| Subunidade | Não | Preenchimento opcional |
| Motorista | Sim | Nome do motorista que receberá o veículo |
| Matrícula | Sim | Matrícula numérica do motorista |
| Quilometragem Inicial | Sim | Leitura do hodômetro no momento da entrega |

3. Clique em **Continuar** (ou equivalente).
4. O sistema validará os dados. Se houver erros, mensagens específicas serão exibidas ao lado de cada campo.

> **Importante:** O sistema não permite criar um novo checklist de entrega se já existe uma entrega aberta para o mesmo veículo (mesma placa) sem devolução concluída. Nesse caso, aparecerá a mensagem: *"Já existe um checklist de entrega aberto para o veículo de placa {placa}. Conclua a devolução antes de registrar nova entrega."*

---

### 6.2 Etapa 2 — Preencher o checklist de entrega

Após criar o checklist, você avança para o preenchimento. O formulário é dividido em etapas indicadas pela barra de progresso no topo da tela (Itens → Condições → Assinaturas).

#### Itens de Verificação

Você verá **20 itens** distribuídos em duas colunas:

**Coluna esquerda — Documentação e Equipamentos:**

| Nº | Item |
|---|---|
| 1 | Documento Veicular |
| 2 | Chave de Roda |
| 3 | Macaco |
| 4 | Triângulo de Sinalização |
| 5 | Estepe |
| 6 | Extintor de Incêndio |
| 7 | Cintos de Segurança |
| 8 | Luzes de Freios |
| 9 | Nível de água (aditivo) |
| 10 | Óleo de motor |

**Coluna direita — Condições do Veículo:**

| Nº | Item |
|---|---|
| 11 | Luzes de Posição (faroletes) |
| 12 | Faróis (alto e baixo) |
| 13 | Luzes de Seta (pisca-alerta) |
| 14 | Luz de Placa |
| 15 | Luz de Ré |
| 16 | Ar Condicionado |
| 17 | Buzina |
| 18 | Rádio/Multimídia |
| 19 | Fluidos de Freios |
| 20 | Limpadores de Para-brisa |

Para cada item, toque ou clique em:
- **OK** — item verificado e em conformidade (o card fica verde).
- **Não OK** — item verificado com problema (o card fica vermelho).

Todos os 20 itens são **obrigatórios**. O contador no topo da seção mostra quantos já foram respondidos (ex.: "15 / 20 verificados").

#### Nível de Combustível

Selecione uma das opções: **1/4**, **2/4**, **3/4** ou **4/4**. Somente uma opção pode ser selecionada. Este campo é obrigatório.

#### Data e Horário da Entrega

Informe a data e o horário em que o veículo está sendo entregue ao motorista. Ambos são obrigatórios.

#### Observações

Campo de texto livre, **opcional**. Use para registrar informações que não se encaixam nos 20 itens — por exemplo, detalhes sobre avarias encontradas ou situações específicas do veículo.

---

### 6.3 Etapa 3 — Registrar avarias no mapa do veículo

O mapa de avarias é **opcional**. Se o veículo não tiver avarias visíveis, você pode pular esta etapa.

1. O mapa exibe **4 vistas do veículo**: topo, lateral esquerda, lateral direita e frontal/traseira.
2. Clique ou toque no ponto exato onde há uma avaria.
3. Para cada ponto marcado, selecione o tipo de avaria:
   - **Risco**
   - **Amassado**
   - **Trincado**
4. Para remover um ponto marcado por engano, clique sobre ele novamente.

> O mapa de avarias **só existe no checklist de entrega**. No checklist de devolução, esta seção não é exibida.

---

### 6.4 Etapa 4 — Coletar assinaturas na entrega

1. Dois campos de assinatura serão exibidos: **Assinatura do Responsável** e **Assinatura do Motorista**.
2. Usando o dedo (celular/tablet) ou o mouse (computador), desenhe a assinatura dentro do campo correspondente.
3. Se precisar refazer a assinatura, clique no botão **Limpar** abaixo do campo e assine novamente.
4. **Ambas as assinaturas são obrigatórias** para salvar o checklist.

> Após o checklist ser salvo, as assinaturas ficam bloqueadas e não podem ser alteradas.

---

### 6.5 Etapa 5 — Salvar o checklist de entrega

1. Após preencher todos os campos obrigatórios e coletar as assinaturas, clique em **Salvar**.
2. O sistema executará todas as validações. Se algum campo obrigatório estiver faltando, mensagens de erro serão exibidas indicando o que falta corrigir.
3. Se tudo estiver correto, aparecerá uma caixa de confirmação com a mensagem:
   > *"Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados."*
4. Clique em **Confirmar** para salvar definitivamente, ou em **Cancelar** para voltar ao formulário.
5. Após o salvamento bem-sucedido, aparecerá a mensagem "Checklist salvo com sucesso." O checklist ficará **bloqueado para edição**.

---

### 6.6 Etapa 6 — Preencher o checklist de devolução

Quando o motorista devolver o veículo, o Responsável deve registrar a devolução no mesmo checklist.

1. Localize o checklist de entrega (pela busca por placa ou pelos recentes na tela inicial).
2. Abra o checklist — ele estará com status **Entregue**.
3. Clique em **Iniciar Devolução** (ou equivalente).

Os dados de Informações Gerais (Placa, Unidade, Subunidade, Motorista, Matrícula, Quilometragem Inicial) são **herdados automaticamente** da entrega e não podem ser editados.

Preencha os campos exclusivos da devolução:

| Campo | Obrigatório | Observação |
|---|---|---|
| Quilometragem Final | Sim | Deve ser maior ou igual à Quilometragem Inicial |
| Data e Horário da Devolução | Sim | Deve ser igual ou posterior à Data de Entrega |
| 20 itens de verificação | Sim | Mesmos itens da entrega, todos obrigatórios |
| Nível de Combustível | Sim | Leitura no momento da devolução |
| Observações | Não | Campo de texto livre opcional |

---

### 6.7 Etapa 7 — Coletar assinaturas na devolução

O procedimento é idêntico ao da entrega (ver [Etapa 4](#64-etapa-4--coletar-assinaturas-na-entrega)): ambas as assinaturas (Responsável e Motorista) são obrigatórias.

---

### 6.8 Etapa 8 — Salvar o checklist de devolução

O procedimento é idêntico ao da entrega (ver [Etapa 5](#65-etapa-5--salvar-o-checklist-de-entrega)). Após salvar, o status do checklist muda de **Entregue** para **Devolvido**.

---

### 6.9 Etapa 9 — Gerar, compartilhar e imprimir o PDF

Após salvar o checklist (entrega ou devolução), é possível gerar um PDF com todos os dados registrados.

1. Abra o checklist salvo.
2. Utilize os botões disponíveis:

| Botão | Ação |
|---|---|
| **Baixar PDF** | Faz o download do arquivo PDF para o seu dispositivo |
| **Compartilhar** | Abre o menu de compartilhamento do dispositivo (permite enviar por e-mail, WhatsApp etc.) |
| **Imprimir** | Abre o diálogo de impressão do navegador |

O PDF contém: dados gerais do veículo, os 20 itens verificados com seus status, nível de combustível, mapa de avarias (quando houver, apenas da entrega), assinaturas e observações.

> Os botões **Compartilhar** e **Imprimir** ficam desabilitados enquanto o checklist não estiver salvo definitivamente.

---

## 7. Como Buscar Checklists por Placa

Qualquer usuário logado pode buscar checklists.

1. Clique em **Buscar** no menu superior ou no botão **Buscar por Placa** na tela inicial.
2. No campo **Placa**, informe a placa do veículo — pode ser parcial (ex.: `ABC`) ou completa (ex.: `ABC1D23`).
3. Clique em **Buscar**.
4. Os resultados serão exibidos em ordem do mais recente para o mais antigo.

Cada resultado mostra:
- **Placa** do veículo
- **Nº de Controle** e **Unidade**
- **Data de criação**
- **Status**: Entregue, Devolvido ou Em preenchimento

Clique em qualquer resultado para abrir o checklist completo.

Se não houver resultados, aparecerá a mensagem: *"Nenhum checklist encontrado para a placa informada. Verifique o número da placa e tente novamente."*

---

## 8. Cancelar o Preenchimento

Se você iniciou um checklist por engano ou precisa descartar os dados preenchidos:

1. Clique em **Cancelar** (disponível enquanto o checklist não foi salvo).
2. O sistema solicitará confirmação com a mensagem:
   > *"Deseja cancelar o preenchimento? Todos os dados informados serão descartados."*
3. Clique em **Confirmar** para descartar e retornar à tela inicial, ou em **Não** para continuar o preenchimento.

> Atenção: após confirmar o cancelamento, os dados preenchidos são descartados permanentemente e não podem ser recuperados.

---

## 9. Navegar entre Telas

- Use o botão **Voltar** para retornar à tela anterior sem salvar.
- Se houver dados não salvos no formulário, o sistema exibirá um alerta:
  > *"Existem dados não salvos neste formulário. Deseja sair sem salvar?"*
- Escolha **Sair sem salvar** para descartar, ou **Continuar editando** para permanecer na tela.
- Também é possível navegar pelo menu superior clicando em **Início** ou **Buscar**.

---

## 10. Mensagens do Sistema

Esta seção descreve as principais mensagens que o sistema pode exibir e o que fazer em cada caso.

### Mensagens de Erro

| Código | Mensagem | O que fazer |
|---|---|---|
| MSG-001 | Usuário ou senha inválidos. Verifique suas credenciais e tente novamente. | Confira usuário e senha. Se não lembrar, entre em contato com o administrador do sistema. |
| MSG-002 | Sua sessão expirou por inatividade. Realize o login novamente para continuar. | Faça login novamente. Dados já salvos não são perdidos. |
| MSG-003 | A matrícula informada já está cadastrada no sistema. Verifique o número e tente novamente. | Use uma matrícula diferente ou consulte o administrador. |
| MSG-008 | Já existe um checklist de entrega aberto para o veículo de placa {placa}. Conclua a devolução antes de registrar nova entrega. | Localize o checklist em aberto para este veículo e registre a devolução antes de criar um novo. |
| MSG-015 | Não é possível iniciar a devolução. Não foi encontrada entrega concluída para o Nº de Controle {número}. | Verifique se o Nº de Controle está correto. A devolução só pode ser iniciada após a entrega ser salva. |
| MSG-016 | A Quilometragem Final não pode ser inferior à Quilometragem Inicial. | Corrija a Quilometragem Final para um valor igual ou maior à Quilometragem Inicial. |
| MSG-017 | A Data de Devolução não pode ser anterior à Data de Entrega. | Informe uma data de devolução igual ou posterior à data registrada na entrega. |
| MSG-026 | Acesso negado. Seu perfil de usuário não tem permissão para esta operação. | Esta funcionalidade não está disponível para o seu perfil. Contate o Responsável. |

### Mensagens de Validação

| Código | Mensagem | O que fazer |
|---|---|---|
| MSG-004 | A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número. | Defina uma nova senha seguindo os requisitos indicados. |
| MSG-005 | Os seguintes campos obrigatórios não foram preenchidos: {lista}. Preencha-os para continuar. | Preencha os campos indicados na mensagem e tente salvar novamente. |
| MSG-006 | Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234). | Corrija a placa para um dos formatos aceitos. |
| MSG-007 | O campo Matrícula aceita apenas valores numéricos. | Informe somente números no campo Matrícula. |
| MSG-009 | Nenhum checklist encontrado para a placa informada. Verifique o número da placa e tente novamente. | Tente novamente com uma placa diferente ou parcialmente diferente. |
| MSG-010 | Os seguintes itens do checklist ainda não foram verificados: {lista}. Todos os 20 itens devem ser respondidos. | Verifique os itens pendentes marcando OK ou Não OK para cada um. |
| MSG-011 | Selecione o nível de combustível do veículo (1/4, 2/4, 3/4 ou 4/4). | Selecione uma das opções de nível de combustível. |
| MSG-012 | Informe a data e o horário da entrega/devolução. | Preencha os campos de data e horário. |
| MSG-013 | Selecione o tipo de avaria (Risco, Amassado ou Trincado) para cada ponto marcado no mapa do veículo. | Para cada ponto marcado no mapa, selecione o tipo de avaria correspondente. |
| MSG-014 | A assinatura do Responsável/Motorista é obrigatória. Assine no campo correspondente para continuar. | Colete a assinatura indicada antes de salvar. |
| MSG-019 | As opções de compartilhamento e impressão estarão disponíveis após o salvamento do checklist. | Salve o checklist antes de compartilhar ou imprimir. |

### Mensagens de Confirmação

| Código | Mensagem | Ação esperada |
|---|---|---|
| MSG-018 | Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados. | Clique em Confirmar para salvar definitivamente, ou Cancelar para revisar. |
| MSG-020 | Deseja cancelar o preenchimento? Todos os dados informados serão descartados. | Clique em Confirmar para descartar, ou Não para continuar preenchendo. |
| MSG-021 | Existem dados não salvos neste formulário. Deseja sair sem salvar? | Escolha entre sair sem salvar ou continuar editando. |

### Mensagens de Sucesso

| Código | Mensagem | Significado |
|---|---|---|
| MSG-022 | Checklist salvo com sucesso. | O checklist foi registrado definitivamente e não pode mais ser editado. |
| MSG-023 | Usuário cadastrado com sucesso. | O novo usuário foi criado e já pode fazer login. |
| MSG-024 | Login realizado com sucesso. | Autenticação concluída com sucesso. |
| MSG-025 | PDF gerado com sucesso. | O arquivo PDF está pronto para download, compartilhamento ou impressão. |

---

## 11. Perguntas Frequentes

**Posso alterar um checklist depois de salvá-lo?**
Não. Após confirmar o salvamento, o checklist fica bloqueado para edição. Isso é uma medida de segurança para garantir a integridade do registro oficial. As assinaturas coletadas também ficam imutáveis.

**Esqueci minha senha. O que faço?**
Entre em contato com o Responsável da sua unidade ou com a equipe de TI do TJCE para que uma nova conta ou senha seja criada.

**Posso criar um novo checklist de entrega para um veículo que ainda está em uso?**
Não. Se já existe um checklist de entrega aberto para determinada placa (sem devolução registrada), o sistema bloqueia a criação de uma nova entrega para o mesmo veículo. Finalize primeiro a devolução do checklist anterior.

**O sistema funciona em celular?**
Sim. O CTRVE é responsivo e funciona em computadores, tablets e celulares. No celular, os 20 itens do checklist possuem área de toque generosa para facilitar o uso durante a vistoria no pátio.

**O mapa de avarias é obrigatório?**
Não. O mapa de avarias é opcional. Se o veículo não apresentar avarias, basta não marcar nenhum ponto. Se marcar um ponto, é obrigatório selecionar o tipo (Risco, Amassado ou Trincado).

**O mapa de avarias aparece na devolução?**
Não. O mapa de avarias é exibido apenas no checklist de entrega. No checklist de devolução, essa seção não está disponível.

**Posso compartilhar o PDF antes de salvar o checklist?**
Não. Os botões de compartilhamento e impressão ficam desabilitados enquanto o checklist não for salvo definitivamente.

**O que acontece se minha sessão expirar enquanto estou preenchendo um checklist?**
A sessão expira após 30 minutos de inatividade e você será redirecionado para a tela de login. Dados de checklists que ainda não foram salvos definitivamente podem ser perdidos. Para evitar isso, salve os dados com mais frequência ou interaja com a tela periodicamente.

**Posso usar o CTRVE sem conexão com a internet?**
Não. O sistema exige conexão com a rede do TJCE ou com a internet para funcionar. Se a conexão for interrompida durante o preenchimento, os dados não salvos podem ser perdidos.

**Quem pode cadastrar novos usuários?**
Somente o perfil Responsável pode acessar a tela de cadastro de usuários. O Motorista não tem permissão para essa operação.

**Como saber se um checklist já foi salvo definitivamente?**
Um checklist salvo definitivamente é identificado por um ícone de cadeado e pelo status **Entregue** ou **Devolvido** na lista de resultados. Checklists ainda em preenchimento aparecem com status diferente e podem ser editados.

**O campo de observações tem limite de caracteres?**
Não há limite visível imposto pelo sistema. Use o campo para registrar todas as informações relevantes que não se encaixem nos 20 itens padronizados.

---

*Manual do Usuário — CTRVE v1.0.0*
*Tribunal de Justiça do Estado do Ceará — TJCE*
*Documento gerado em conformidade com a Resolução nº 641/2025*
