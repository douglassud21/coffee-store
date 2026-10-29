import logging
import os
import secrets
from flask import Flask, request
from flask_caching import Cache
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

from database import db
from models import Usuario
from routes import routes, cache

# ==========================================
# CONFIGURAÇÃO DO FLASK
# ==========================================

app = Flask(__name__)

# Configurações para upload de fotos
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.static_folder, "uploads"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

# ==========================================
# CONFIGURAÇÕES DA APLICAÇÃO E CACHE
# ==========================================

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuração do Cache (SimpleCache em memória para ambiente Flask)
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

# Inicialização das Extensões
db.init_app(app)
cache.init_app(app)

# Registra as Rotas
app.register_blueprint(routes)

# Logging Básico
logging.basicConfig(level=logging.INFO)


# ==========================================
# MIDDLEWARE / API GATEWAY (FILTROS DE REQUISIÇÃO)
# ==========================================


@app.before_request
def middleware_gateway():
    # Exemplo de Middleware: Log de requisições de entrada
    app.logger.info(f"[API Gateway] Requisição: {request.method} {request.path}")


@app.after_request
def middleware_headers(response):
    # Adiciona cabeçalhos globais de segurança e CORS básico
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# ==========================================
# CRIAÇÃO DO BANCO & CRIAÇÃO INICIAL
# ==========================================

with app.app_context():
    db.create_all()

    inspector = inspect(db.engine)
    tabelas = inspector.get_table_names()

    # Adiciona a coluna de foto aos usuários existentes
    if "usuarios" in tabelas:
        colunas_usuarios = [
            coluna["name"]
            for coluna in inspector.get_columns("usuarios")
        ]

        if "foto" not in colunas_usuarios:
            with db.engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE usuarios "
                        "ADD COLUMN foto VARCHAR(255) "
                        "NOT NULL DEFAULT 'padrao.png'"
                    )
                )

        # Garante que a tabela reservas tenha as colunas necessárias
    if "reservas" in tabelas:
        colunas_reservas = [
            coluna["name"] for coluna in inspector.get_columns("reservas")
        ]

        # Adiciona usuario_id, caso ainda não exista
        if "usuario_id" not in colunas_reservas:
            with db.engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE reservas ADD COLUMN usuario_id INTEGER")
                )

        # Adiciona ativo, caso ainda não exista
        if "ativo" not in colunas_reservas:
            with db.engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE reservas "
                        "ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"
                    )
                )

    # Cria Administrador Padrão
    admin = Usuario.query.filter_by(email="admin@cafeesabor.com").first()
    if not admin:
        admin = Usuario(
            nome="Administrador",
            email="admin@cafeesabor.com",
            telefone="00000000000",
            senha=generate_password_hash(os.environ.get("ADMIN_PASSWORD", "Admin@123")),
            tipo="admin",
        )
        db.session.add(admin)
        db.session.commit()

# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
