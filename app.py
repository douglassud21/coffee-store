from flask import Flask

from database import db
from routes import routes


# ==========================================
# CONFIGURAÇÃO DA APLICAÇÃO
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
# INICIALIZAÇÃO DO BANCO
# ==========================================

db.init_app(app)


# ==========================================
# REGISTRAR BLUEPRINT
# ==========================================

app.register_blueprint(
    routes
)


# ==========================================
# CRIAR BANCO E TABELAS
# ==========================================

with app.app_context():

    db.create_all()


# ==========================================
# INICIAR SISTEMA
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )