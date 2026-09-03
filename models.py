from database import db


class Reserva(db.Model):
    __tablename__ = "reservas"

    # Identificador único
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Nome completo do cliente
    nome_completo = db.Column(
        db.String(150),
        nullable=False
    )

    # Data da reserva
    data = db.Column(
        db.Date,
        nullable=False
    )

    # Horário da reserva
    horario = db.Column(
        db.Time,
        nullable=False
    )

    # Quantidade de pessoas
    quantidade_pessoas = db.Column(
        db.Integer,
        nullable=False
    )

    # Categoria da reserva
    categoria_reserva = db.Column(
        db.String(100),
        nullable=False
    )

    # Observações
    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    # Status da reserva
    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pendente"
    )

    def __repr__(self):
        return f"<Reserva {self.id} - {self.nome_completo}>"