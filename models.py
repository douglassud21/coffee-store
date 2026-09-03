from database import db


# ==========================================
# MODELO DE USUÁRIO
# ==========================================

class Usuario(db.Model):

    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    tipo = db.Column(
        db.String(20),
        nullable=False,
        default="cliente"
    )

    # --------------------------------------
    # RELACIONAMENTO COM RESERVAS
    # --------------------------------------

    reservas = db.relationship(
        "Reserva",
        backref="usuario",
        lazy=True
    )

    def __repr__(self):

        return f"<Usuario {self.id} - {self.email}>"


# ==========================================
# MODELO DE RESERVA
# ==========================================

class Reserva(db.Model):

    __tablename__ = "reservas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome_completo = db.Column(
        db.String(150),
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    horario = db.Column(
        db.Time,
        nullable=False
    )

    quantidade_pessoas = db.Column(
        db.Integer,
        nullable=False
    )

    categoria_reserva = db.Column(
        db.String(100),
        nullable=False
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pendente"
    )

    # --------------------------------------
    # USUÁRIO RESPONSÁVEL PELA RESERVA
    # --------------------------------------

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    def __repr__(self):

        return f"<Reserva {self.id} - {self.nome_completo}>"