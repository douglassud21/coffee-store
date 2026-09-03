from database import db


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

    def __repr__(self):
        return f"<Reserva {self.id} - {self.nome_completo}>"