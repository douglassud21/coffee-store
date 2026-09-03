
from flask import Flask
from sqlalchemy import inspect, text

from database import db
from routes import routes
from models import Usuario

from werkzeug.security import generate_password_hash


# ==========================================
# CONFIGURAÇÃO DO FLASK
# ==========================================

app = Flask(__name__)


# ==========================================
# CONFIGURAÇÕES
# ==========================================

app.config["SECRET_KEY"] = "chave-secreta-do-projeto"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# BANCO DE DADOS
# ==========================================

db.init_app(app)


# ==========================================
# BLUEPRINT
# ==========================================

app.register_blueprint(routes)


# ==========================================
# CRIAÇÃO DO BANCO
# ==========================================

with app.app_context():

    db.create_all()

    inspector = inspect(
        db.engine
    )

    tabelas = inspector.get_table_names()

    # --------------------------------------
    # GARANTE usuario_id NA TABELA RESERVAS
    # --------------------------------------

    if "reservas" in tabelas:

        colunas_reservas = [
            coluna["name"]
            for coluna in inspector.get_columns(
                "reservas"
            )
        ]

        if "usuario_id" not in colunas_reservas:

            with db.engine.begin() as connection:

                connection.execute(
                    text(
                        "ALTER TABLE reservas "
                        "ADD COLUMN usuario_id INTEGER"
                    )
                )

    # --------------------------------------
    # CRIA ADMIN PADRÃO
    # --------------------------------------

    admin = Usuario.query.filter_by(
        email="admin@cafeesabor.com"
    ).first()

    if not admin:

        admin = Usuario(
            nome="Administrador",
            email="admin@cafeesabor.com",
            telefone="00000000000",
            senha=generate_password_hash(
                "Admin@123"
            ),
            tipo="admin"
        )

        db.session.add(admin)

        db.session.commit()


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

