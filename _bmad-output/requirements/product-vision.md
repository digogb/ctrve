# Visão do Produto — CTRVE (Checklist de Transporte de Veículos)

## Escopo

Sistema digital para controle de entrega e devolução de veículos oficiais do Tribunal de Justiça do Estado do Ceará (TJCE). Substitui o processo manual em papel por um formulário digital com checklist padronizado de 20 itens de segurança e equipamentos, registro de avarias em mapa gráfico do veículo, coleta de assinaturas digitais, e geração de PDF para compartilhamento.

Desenvolvido em conformidade com a Resolução nº 641/2025, que dispõe sobre a política de sustentabilidade no âmbito do Poder Judiciário. Referência: Documento SEI 8527796-55.2025.8.06.0000 (Requerimento Administrativo 0456448).

### Funcionalidades Incluídas

- Cadastro e autenticação de usuários com perfis Responsável e Motorista
- Registro de informações gerais do veículo (Nº de Controle, Placa, Unidade, Subunidade, Motorista, Matrícula, Quilometragem)
- Checklist de Entrega com 20 itens de verificação, nível de combustível, mapa de avarias gráfico e assinaturas
- Checklist de Devolução com 20 itens de verificação, nível de combustível e assinaturas
- Mapa de avarias interativo com 4 vistas do veículo e classificação por tipo (Risco, Amassado, Trincado)
- Campo de observações em texto livre para registro de avarias e situações relevantes
- Busca de checklists por placa do veículo
- Geração e compartilhamento de PDF do checklist completo
- Impressão do checklist
- Validações de campos obrigatórios, consistência de dados e regras de fluxo

## Fora de Escopo

- Módulo de fotos do veículo
- Integração com sistemas externos (SEI, sistema de frota, DETRAN)
- Gestão de contratos de locação ou manutenção de veículos
- Cadastro de frota (veículos são identificados pela placa no momento do checklist)
- Cadastro de unidades/subunidades (preenchimento livre)
- Relatórios gerenciais e dashboards
- Aplicativo mobile nativo (sistema web responsivo)
- Mapa de avarias no checklist de devolução

## Premissas

- Usuários possuem acesso à rede do TJCE ou à internet para acessar o sistema
- A assinatura digital é realizada via canvas na tela (desenho), não por certificado ICP-Brasil
- O Nº de Controle é informado manualmente pelo Responsável, não gerado automaticamente
- Os 20 itens do checklist são fixos e idênticos para entrega e devolução (conforme modelo aprovado)
- O sistema será acessado via navegador web (desktop e dispositivos móveis)

## Restrições

- Stack tecnológica definida: React (frontend) + FastAPI (backend) + PostgreSQL (banco de dados)
- Autenticação própria do sistema (não integrada a LDAP/AD do TJCE nesta versão)
- O fluxo de devolução só pode ser iniciado após a conclusão de uma entrega para o mesmo Nº de Controle
- Todos os 20 itens do checklist devem ser verificados antes de salvar (nenhum item pode ficar sem resposta)
