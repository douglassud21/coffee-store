# Mapeamento de Endpoints da API

|     Rota                   |     Método              |     Acesso              |     Descrição                                        |     Padrão / Recurso                   |
| :---                       |  :---                   |  :---                   |    :---                                              |       :---                             |
| `/login`                   | `GET`, `POST`           | Público                 | Autenticação do usuário na plataforma.               | Síncrono (API REST)                    |
| `/cadastro`                | `GET`, `POST`           | Público                 | Registro de novos clientes no sistema.               | Síncrono + Worker Assíncrono           |
| `/logout`                  | `GET`                   | Autenticado             | Encerramento da sessão ativa do usuário.             | Síncrono                               |
| `/catalogo`                | `GET`                   | Público                 | Exibição de produtos e cardápio.                     | **Cache Habilitado (TTL 60s)**         |
| `/`                        | `GET`                   | Autenticado             | Dashboard principal do sistema.                      | Síncrono                               |
| `/reserva`                 | `GET`                   | Cliente                 | Formulario de criação de reservas.                   | Síncrono                               |
| `/confirmacao`             | `POST`                  | Cliente                 | Processamento e criação de reservas.                 | Síncrono + Worker Assíncrono           |
| `/minhas-reservas`         | `GET`                   | Cliente                 | Listagem de reservas efetuadas pelo usuário logado.  | Síncrono                               |
| `/editar-reserva/<id>`     | `GET`, `POST`           | Cliente                 | Edição de reserva existente.                         | Síncrono                               |
| `/cancelar-reserva/<id>`   | `POST`                  | Cliente                 | Cancelamento de reserva pendente.                    | Síncrono + Worker Assíncrono           |
| `/reservas`                | `GET`                   | Admin                   | Listagem geral e busca de reservas.                  | Síncrono                               |
| `/mudar-status/<id>`       | `POST`                  | Admin                   | Alteração de status da reserva.                      | Síncrono + Worker Assíncrono           |
| `/excluir-reserva/<id>`    | `POST`                  | Admin                   | Remoção definitiva de uma reserva.                   | Síncrono                               |