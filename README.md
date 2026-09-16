# ☕ Café & Sabor — Sistema de Reservas

Sistema web desenvolvido para uma atividade acadêmica com o objetivo de simular o processo de reserva de mesas em uma cafeteria.

O projeto utiliza **Python com Flask** no backend e **HTML e CSS** no frontend, seguindo uma **arquitetura monolítica**.

---

## 📌 Sobre o projeto

O sistema permite que o usuário:

* Acesse a página inicial da cafeteria;
* Acesse a página de reservas;
* Preencha seus dados cadastrais;
* Informe a data e o horário da reserva;
* Informe a quantidade de pessoas;
* Adicione observações, caso necessário;
* Envie a reserva através de um formulário `POST`;
* Visualize uma tela de confirmação com os dados informados;
* Visualize a lista de reservas cadastradas;
* Pesquise reservas pelo nome do cliente ou categoria;
* Altere o status das reservas cadastradas;
* Exclua reservas definitivamente do sistema.

---

## 📝 Descrição Geral

O objetivo do sistema **Café & Sabor** é auxiliar no gerenciamento de reservas de mesas em uma cafeteria, permitindo que os usuários realizem reservas e consultem suas informações de forma organizada.

A aplicação centraliza o cadastro, validação, armazenamento, consulta, exclusão e alteração do status das reservas, facilitando o controle das informações pela cafeteria.

---

## 📋 Requisitos Funcionais

| Código | Descrição |
| :---: | :--- |
| **RF01** | **Realizar reserva:** o sistema deve permitir cadastrar uma reserva informando nome completo, data, horário, quantidade de pessoas, categoria e observações. |
| **RF02** | **Confirmar reserva:** o sistema deve permitir visualizar os dados cadastrados e confirmar a realização da reserva. |
| **RF03** | **Listar reservas:** o sistema deve exibir as reservas cadastradas, incluindo o ID, nome, categoria, data, horário, quantidade de pessoas e status. |
| **RF04** | **Alterar status:** o sistema deve permitir alterar o status da reserva entre **Pendente**, **Confirmada** e **Concluída**. |
| **RF05** | **Excluir reserva:** o sistema deve permitir excluir definitivamente uma reserva pelo seu ID. |
| **RF06** | **Pesquisar reservas:** o sistema deve permitir pesquisar reservas pelo nome do cliente ou categoria da reserva. |
| **RF07** | **Validar reservas:** o sistema deve impedir o cadastro de informações inválidas, como campos obrigatórios vazios, quantidade de pessoas menor ou igual a zero, data/horário inválidos ou data passada. |
| **RF08** | **Exibir informações gerais:** a página inicial deve apresentar indicadores como total de reservas, reservas confirmadas e total de pessoas. |
| **RF09** | **Persistir dados:** o sistema deve armazenar as reservas em banco de dados SQLite, mantendo os dados mesmo após o encerramento e reinício do servidor. |

---

## ⚡ Requisitos Não Funcionais

| Código | Descrição |
| :---: | :--- |
| **RNF01** | **Desempenho:** o sistema deve realizar consultas, cadastros, alterações, exclusões e pesquisas de reservas de forma rápida e eficiente. |
| **RNF02** | **Disponibilidade:** o sistema deve poder permanecer em execução continuamente, permitindo acesso às funcionalidades durante o período em que o servidor estiver disponível. |
| **RNF03** | **Persistência:** os dados devem ser armazenados em banco de dados SQLite, não dependendo de listas ou variáveis temporárias em memória. |
| **RNF04** | **Segurança dos dados:** informações dos usuários e das reservas devem ser armazenadas de forma adequada, evitando o versionamento do banco de dados e de arquivos `.env` no Git. |
| **RNF05** | **Manutenibilidade:** o sistema deve utilizar uma estrutura organizada, separando aplicação, rotas, modelos, banco de dados e templates. |
| **RNF06** | **Usabilidade:** as mensagens de validação e erro devem ser claras para facilitar o preenchimento e a utilização do sistema. |
| **RNF07** | **Portabilidade:** cada máquina deve conseguir criar seu próprio banco de dados local por meio do `db.create_all()`, sem depender do arquivo de banco enviado pelo GitHub. |

---

## 🛡️ Proteção de Dados dos Usuários

O sistema deve proteger principalmente os dados pessoais utilizados no cadastro e nas reservas, como:

* Nome completo;
* E-mail;
* Telefone;
* Dados e histórico relacionados às reservas realizadas.

> 🔒 **Aviso de Segurança:** Arquivos de banco de dados locais (`*.db`, `*.sqlite`) e configurações sensíveis (`.env`) contendo informações de usuários não devem ser versionados ou enviados ao repositório do GitHub.

---

## ⏱️ Eventos do Sistema

| Evento | Ator | Ação | Resposta do Sistema |
| :--- | :--- | :--- | :--- |
| **E01 – Acessar página inicial** | Usuário | Acessa `/` | Sistema carrega o painel e apresenta os indicadores de reservas. |
| **E02 – Iniciar reserva** | Usuário | Clica em **Reservar** | Sistema apresenta o formulário de reserva. |
| **E03 – Enviar reserva** | Usuário | Preenche o formulário e envia | Sistema recebe os dados via `POST` e inicia as validações. |
| **E04 – Dados inválidos** | Sistema | Identifica campo vazio ou informação inválida | Sistema impede o cadastro e apresenta uma mensagem de erro. |
| **E05 – Reserva válida** | Sistema | Valida todos os dados corretamente | Sistema cria um novo registro `Reserva` com status **Pendente**. |
| **E06 – Salvar reserva** | Sistema | Executa a persistência dos dados | Reserva é armazenada no banco SQLite. |
| **E07 – Confirmar cadastro** | Sistema | Reserva foi salva com sucesso | Sistema apresenta a página de confirmação com os dados da reserva. |
| **E08 – Consultar reservas** | Usuário | Acessa a lista de reservas | Sistema consulta os registros e apresenta a tabela. |
| **E09 – Pesquisar reserva** | Usuário | Digita um nome ou categoria | Sistema realiza a pesquisa e apresenta os resultados correspondentes. |
| **E10 – Alterar status** | Usuário | Clica no botão de alteração de status | Sistema altera o status da reserva e salva a alteração no banco. |
| **E11 – Concluir reserva** | Usuário | Altera uma reserva Confirmada | Sistema muda o status para **Concluída**. |
| **E12 – Excluir reserva** | Usuário | Clica em excluir | Sistema solicita confirmação da exclusão. |
| **E13 – Confirmar exclusão** | Usuário | Confirma a exclusão | Sistema localiza a reserva pelo ID, exclui o registro e salva a alteração. |
| **E14 – Cancelar exclusão** | Usuário | Cancela a exclusão | Sistema mantém a reserva cadastrada. |
| **E15 – Reiniciar servidor** | Sistema | Aplicação é executada novamente | Sistema utiliza o banco SQLite existente e mantém os dados cadastrados. |

---

## 🎯 Objetivo

Desenvolver uma aplicação web simples aplicando conceitos de:

* Desenvolvimento Web Backend com **Flask / Python**;
* Gerenciamento de Rotas e Requisições HTTP (`GET`, `POST`);
* Formulários HTML, Validação de Dados e Processamento de Entradas;
* Renderização de Templates e Exibição de Métricas;
* Manipulação de Estados e Banco de Dados Relacional (**SQLite**);
* Pesquisa, Filtragem e Operações CRUD (Create, Read, Update, Delete);
* Arquitetura Monolítica e Padrões de Projeto;
* Componentes de Comunicação (API REST, Síncrona vs Assíncrona, Fila/Mensageria);
* Estratégias de Cache para otimização de performance;
* Versionamento e colaboração com **Git e GitHub**.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3, Flask, Flask-SQLAlchemy
* **Frontend:** HTML5, CSS3
* **Banco de Dados:** SQLite
* **Ferramentas:** Git, GitHub, Visual Studio Code

---

# 🏗️ Arquitetura

O projeto utiliza uma **arquitetura monolítica**, na qual os principais componentes da aplicação estão concentrados em um único projeto.

Para a evolução da arquitetura apresentada nesta entrega, são considerados componentes de comunicação que permitem melhorar a organização, o desempenho e a comunicação entre o usuário e a aplicação:

* **API Gateway:** Utilizado como ponto de entrada único das requisições, direcionando as solicitações para os componentes responsáveis pelo processamento.
* **Cache:** Estratégia de otimização para informações consultadas frequentemente, reduzindo a carga de leituras repetitivas no banco de dados.
* **Fila/Mensageria:** Mecanismo desacoplado para executar tarefas assíncronas (ex.: envio de notificações) sem bloquear o fluxo principal do usuário.

### Componentes Principais

* **Usuário:** Realiza as interações com o sistema através do navegador web.
* **API Gateway:** Atua como ponto de entrada das requisições e direciona as solicitações para a aplicação.
* **Aplicação Flask:** Responsável pelas rotas, regras de negócio e processamento das requisições.
* **Banco de Dados SQLite:** Responsável pela persistência relacional das informações.
* **Cache:** Armazena temporariamente informações de alta leitura para otimizar o tempo de resposta.
* **Fila/Mensageria:** Processa tarefas em segundo plano de forma assíncrona.

### Fluxo Principal de Processamento

```text
Usuário
   │
   ▼
API Gateway
   │
   ▼
Aplicação Flask
   │
   ├──────────────► Cache (Otimização de Métricas)
   │
   ▼
Banco de Dados SQLite


🗂️ Estratégia de Cache
O Cache é utilizado para armazenar temporariamente informações de alta rotatividade de leitura que não necessitam ser consultadas no banco de dados a cada nova requisição.

No sistema Café & Sabor, esta estratégia é aplicada nas métricas da página inicial:

Total de reservas;
Total de reservas confirmadas;
Total de pessoas.

Fluxo de Funcionamento do Cache:

Usuário
   │
   ▼
API Gateway
   │
   ▼
Aplicação Flask
   │
   ▼
Verifica Cache
   │
   ├── [Cache HIT]  ────► Retorna Informação Rapidamente
   │
   └── [Cache MISS] ────► Consulta Banco de Dados ────► Atualiza Cache ────► Retorna Informação

📌 Nota: A implementação do Cache representa uma proposta de evolução arquitetural projetada no documento do sistema.


🔄 Fluxos de Comunicação
1. Comunicação Síncrona — API REST
A comunicação síncrona é utilizada em funcionalidades onde o usuário necessita do retorno imediato da aplicação para dar prosseguimento à sua ação, como no cadastro de uma reserva.

Fluxo Síncrono:

Usuário ──(POST /confirmacao)──► API Gateway ──► Aplicação Flask ──► Validação ──► Banco de Dados
  ▲                                                                                      │
  └─────────────────────────────── Resposta HTTP (Confirmação) ──────────────────────────┘

Nesse fluxo, a conexão permanece aberta até que o registro seja gravado e a página de confirmação seja devolvida.

2. Comunicação Assíncrona — Fila/Mensageria
A comunicação assíncrona é utilizada para tarefas de segundo plano que não devem travar a navegação do usuário, como o envio de e-mail ou SMS de confirmação.

Fluxo Assíncrono:

Usuário ──► API Gateway ──► Aplicação Flask ──► Salva no Banco
                               │
                               ├─► Retorna Confirmação ao Usuário (Imediato)
                               │
                               └─► Publica Mensagem na Fila ──► Worker em Segundo Plano ──► Envia Notificação

📌 Nota: O componente de Fila/Mensageria representa uma proposta de evolução arquitetural para suportar grande volume de notificações.


🚀 Funcionalidades
🏠 Página Inicial (Dashboard)
Apresenta informações sobre a cafeteria e exibe o painel estatístico em tempo real:

Total de reservas cadastradas;

Quantidade de reservas confirmadas;

Soma total de pessoas esperadas.

📝 Formulário de Reserva
Permite a entrada dos dados da reserva:

Nome completo do responsável;

Data e Horário da reserva;

Quantidade de pessoas (limite de 1 a 20);

Categoria da reserva (ex.: Aniversário, Reunião, Evento, Comum);

Observações e solicitações especiais.

✅ Tela de Confirmação
Exibe o resumo detalhado dos dados informados logo após o envio bem-sucedido do formulário.

📑 Lista e Consulta de Reservas
Página administrativa que exibe todas as reservas armazenadas em uma tabela organizada com filtros.

🔎 Pesquisa Dinâmica
Permite a busca e filtragem rápida de reservas cadastradas através do nome do cliente ou da categoria informada via parâmetro GET.

🔄 Gerenciamento de Status
Permite alterar o ciclo de vida da reserva entre os estados:

Pendente (Status padrão ao criar)

Confirmada

Concluída

🗑️ Exclusão de Reservas
Permite remover registros do banco de dados definitivamente via confirmação do usuário.



# 📂 Estrutura do Projeto

```text
coffee-store/
│
├── docs/                       # Documentações, diagramas e especificações
│   ├── api_endpoints.md        # Documentação dos endpoints da API
│   ├── arquitetura_sistema.jpeg# Diagrama/imagem da arquitetura do sistema
│   ├── arquitetura.md          # Documentação detalhada da arquitetura
│   ├── Der.png                 # Diagrama Entidade-Relacionamento
│   └── diagrama_componentes.png# Diagrama de componentes e visão geral
│
├── instance/                   # Pasta de instâncias locais (ex: banco de dados SQLite)
│
├── static/                     # Arquivos estáticos (Estilos CSS)
│   ├── base.css                # Estilo base/global da aplicação
│   ├── cadastro.css            # Estilo da página de cadastro de usuários
│   ├── confirmacao.css         # Estilo da tela de confirmação de reserva
│   ├── editar_reserva.css      # Estilo da tela de edição de reserva
│   ├── index.css               # Estilo da página inicial (Dashboard)
│   ├── lista_reservas.css      # Estilo da tabela de listagem de reservas
│   ├── login.css               # Estilo da tela de login
│   ├── meu_cadastro.css        # Estilo do perfil do usuário
│   ├── minhas_reservas.css     # Estilo da tela de reservas do usuário
│   └── reserva.css             # Estilo do formulário de reserva
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── cadastro.html           # Página de cadastro de novos usuários
│   ├── confirmacao.html        # Página de confirmação da reserva
│   ├── editar_reserva.html     # Formulário para edição de reserva
│   ├── index.html              # Página inicial / Dashboard de métricas
│   ├── lista_reservas.html     # Painel administrativo de reservas
│   ├── login.html              # Página de login/autenticação
│   ├── meu_cadastro.html       # Visualização e edição dos dados cadastrais
│   ├── minhas_reservas.html    # Lista de reservas do usuário logado
│   └── reserva.html            # Formulário de criação de novas reservas
│
├── .gitignore                  # Arquivos e pastas ignorados pelo Git
├── app.py                      # Ponto de entrada e inicialização da aplicação Flask
├── database.py                 # Configurações e conexões com o banco de dados
├── Login_Adm.txt               # Credenciais/instruções para acesso administrativo
├── models.py                   # Modelos do banco de dados (SQLAlchemy)
├── README.md                   # Documentação principal do repositório
├── requirements.txt            # Dependências e bibliotecas Python do projeto
└── routes.py                   # Definição e gerenciamento das rotas do sistema



⚙️ Como Executar o Projeto
1. Clonar o repositório

git clone [https://github.com/douglassud21/coffee-store.git](https://github.com/douglassud21/coffee-store.git)
cd coffee-store

2. Criar e ativar o ambiente virtual
No Windows:

python -m venv venv
venv\Scripts\activate

No Linux/macOS:

python3 -m venv venv
source venv/bin/activate

3. Instalar as dependências

pip install -r requirements.txt

4. Executar a aplicação

python app.py

5. Acessar no navegador
Acesse http://127.0.0.1:5000/ no seu navegador.

🔄 Rotas do SistemaMétodoRotaFunção / ObjetivoGET/Carrega a página inicial e exibe o dashboard de métricas.GET/reservaExibe o formulário para cadastro de nova reserva.POST/confirmacaoProcessa os dados do formulário, valida e salva a reserva.GET/reservasLista todas as reservas e permite filtragem/pesquisa via parâmetro ?busca=.POST/mudar-status/<int:id>Atualiza o status da reserva no banco de dados.POST/excluir/<int:id>Exclui permanentemente a reserva do banco de dados pelo seu ID.

🛡️ Regras de Validação
Antes de realizar a gravação no banco de dados SQLite, o backend executa as seguintes verificações de integridade:

Campos Obrigatórios: Nome, data, horário e quantidade de pessoas não podem estar vazios.

Validação de Nome: Impede nomes muito curtos ou contendo caracteres inválidos.

Quantidade de Pessoas:

Deve ser obrigatoriamente um número inteiro.

Não pode ser menor ou igual a 0.

Não pode exceder o limite de 20 pessoas por mesa.

Data e Horário:

Impede o agendamento em datas passadas em relação ao dia atual.

Garante o formato correto de data e hora.

Em caso de inconsistência, a aplicação cancela o cadastro e exibe alertas explicativos ao usuário.

🧪 Roteiro de Testes
Para homologar as funcionalidades do sistema, siga o roteiro de testes:

Acesso: Navegue até a página inicial (/) e verifique os indicadores zerados ou iniciais.

Cadastro Válido: Clique em Reservar, preencha os dados corretamente e envie.

Confirmação: Confirme se os dados preenchidos aparecem corretamente na tela /confirmacao.

Listagem: Acesse /reservas e confirme se o novo registro consta na tabela com status Pendente.

Busca: Digite o nome do cliente no campo de pesquisa e verifique se o filtro funciona corretamente.

Alteração de Status: Clique no botão de alterar status e verifique a transição para Confirmada e Concluída.

Teste de Validação (Inválido): Tente cadastrar uma reserva com 0 pessoas ou com data no passado e confirme se o sistema exibe o erro e bloqueia a gravação.

Exclusão: Remova uma reserva de teste e confirme sua remoção da listagem e do banco de dados.

Métricas: Volte à página inicial (/) e verifique se o contador de reservas e pessoas refletiu as mudanças.

📐 Documentação Técnica
Diagrama Entidade-Relacionamento (DER)
Abaixo é apresentada a estrutura conceitual do banco de dados relacional SQLite:

Diagrama de Componentes e Comunicação
Visão geral da arquitetura monolítica com a proposta de evolução integrando API Gateway, Cache e Fila de Mensagens:

Integrante                  |RM                 |Responsabilidade Principal
Douglas Silva Nascimento    |22873              |"Backend Flask, gerenciamento de rotas, integração com banco de dados e regras de negócio."
Allan Gabriel Sousa Palma   |22544              |"Desenvolvedor Frontend (HTML/CSS), estrutura de layouts e usabilidade das páginas."
Vitória de Carvalho Esteves |21684              |"Arquitetura de software, diagramas, mapeamento de eventos do sistema e fluxos de comunicação."
Gustavo Gomes Pecora        |22767              |"Gestão do repositório Git/GitHub, documentação do projeto, modelagem DER e testes."

#Nome do Grupo: Coders
