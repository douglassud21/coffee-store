# Capítulo 2: Arquitetura e Componentes Distribuídos

## 1. Visão Geral e Diagramas do Sistema

A documentação visual da arquitetura e modelagem do sistema encontra-se na pasta `./diagramas/`:
* **Arquitetura do Sistema:** `diagramas/arquitetura_sistema.png` (Visão geral de entrada de requisições, API Gateway, aplicação e banco).
* **Modelo Entidade-Relacionamento (DER):** `diagramas/der.png` (Mapeamento das entidades Usuario e Reserva com suas chaves e relacionamentos).
* **Diagrama de Componentes:** `diagramas/diagrama_componentes.png` (Divisão modular do backend, middlewares, cache e tarefas em segundo plano).

---

## 2. Inclusão dos Componentes Distribuídos

### API Gateway e Middlewares
* **Posicionamento:** O API Gateway/Middleware atua como a porta de entrada central do sistema, posicionado entre os clientes/navegadores e os controladores das rotas do ecossistema Flask.
* **Função no Sistema:** Centralizado na aplicação via interceptadores (`@app.before_request` e `@app.after_request`), o gateway realiza o registro unificado de requisições de entrada (*request logging*) e a injeção global de cabeçalhos de segurança (proteções contra *clickjacking* e *MIME-sniffing*).

### Estratégia de Cache
* **Tela/Função:** Rota do Catálogo e Cardápio de Produtos (`/catalogo`).
* **Tecnologia Utilizada:** `Flask-Caching` com armazenamento `SimpleCache` em memória.
* **Justificativa:** A listagem de produtos/serviços possui altíssimo volume de leitura e baixa frequência de alteração. O uso de cache com tempo de expiração (TTL de 60 segundos) elimina consultas repetitivas ao banco de dados, aumentando substancialmente a velocidade de carregamento e reduzindo o consumo de recursos do servidor.

---

## 3. Mapeamento dos Padrões de Comunicação

### Fluxo 1 — Comunicação Síncrona (API REST)
* **Funcionalidade:** Autenticação e Validação de Login do Usuário (`/login`).
* **Descrição do Fluxo:** O usuário envia suas credenciais via requisição HTTP POST. A aplicação suspende a resposta ao cliente enquanto consulta o banco de dados e valida o *hash* da senha. O acesso à interface do painel só é liberado imediatamente após essa confirmação direta no banco.

### Fluxo 2 — Comunicação Assíncrona (Threads / Background Worker)
* **Funcionalidade:** Processamento de Notificações de Reserva e Cadastro (`enviar_notificacao_assincrona`).
* **Descrição do Fluxo:** Ao concluir uma criação, alteração ou cancelamento de reserva, a rota do sistema persiste o dado no banco e devolve a resposta visual de confirmação ao usuário imediatamente. Em segundo plano, uma tarefa em paralelo (*Thread* assíncrona) processa a notificação/mensageria do evento sem bloquear nem desacelerar a navegação da aplicação.