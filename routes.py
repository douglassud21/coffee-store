
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from datetime import datetime

from database import db
from models import Reserva


# ==========================================
# BLUEPRINT
# ==========================================

routes = Blueprint("routes", __name__)


# ==========================================
# PÁGINA INICIAL
# ==========================================

@routes.route("/")
def index():

    # Total de reservas cadastradas
    total_reservas = Reserva.query.count()

    # Total de reservas confirmadas
    reservas_confirmadas = Reserva.query.filter_by(
        status="Confirmada"
    ).count()

    # Soma da quantidade de pessoas
    total_pessoas = db.session.query(
        db.func.sum(Reserva.quantidade_pessoas)
    ).scalar()

    # Se não houver reservas, retorna 0
    if total_pessoas is None:
        total_pessoas = 0

    return render_template(
        "index.html",
        total_reservas=total_reservas,
        reservas_confirmadas=reservas_confirmadas,
        total_pessoas=total_pessoas
    )


# ==========================================
# PÁGINA DE RESERVA
# ==========================================

@routes.route("/reserva")
def reserva():

    return render_template(
        "reserva.html"
    )


# ==========================================
# CADASTRAR RESERVA
# ==========================================

@routes.route("/confirmacao", methods=["POST"])
def confirmacao():

    # --------------------------------------
    # RECEBER DADOS DO FORMULÁRIO
    # --------------------------------------

    nome_completo = request.form.get(
        "nome_completo",
        ""
    ).strip()

    telefone = request.form.get(
        "telefone",
        ""
    ).strip()

    data = request.form.get(
        "data",
        ""
    ).strip()

    horario = request.form.get(
        "horario",
        ""
    ).strip()

    quantidade_pessoas = request.form.get(
        "quantidade_pessoas",
        ""
    ).strip()

    categoria_reserva = request.form.get(
        "categoria_reserva",
        ""
    ).strip()

    observacoes = request.form.get(
        "observacoes",
        ""
    ).strip()


    # --------------------------------------
    # VALIDAR CAMPOS OBRIGATÓRIOS
    # --------------------------------------

    if not nome_completo:

        return render_template(
            "reserva.html",
            erro="Preencha o nome completo."
        )

    if not nome_completo:

        return render_template(
            "reserva.html",
            erro="Preencha o nome completo."
        )

    if not data:

        return render_template(
            "reserva.html",
            erro="Informe a data da reserva."
        )


    if not horario:

        return render_template(
            "reserva.html",
            erro="Informe o horário da reserva."
        )


    if not quantidade_pessoas:

        return render_template(
            "reserva.html",
            erro="Informe a quantidade de pessoas."
        )


    if not categoria_reserva:

        return render_template(
            "reserva.html",
            erro="Informe a categoria da reserva."
        )


    # --------------------------------------
    # VALIDAR NOME
    # --------------------------------------

    if len(nome_completo) < 2:

        return render_template(
            "reserva.html",
            erro="Digite um nome válido."
        )

    # --------------------------------------
    # remover os caracteres de formatação
    # --------------------------------------

    telefone_numeros = "".join(
        filtro for filtro in telefone
            if filtro.isdigit()
        )

    if len(telefone_numeros) not in (10, 11):
        return render_template(
            "reserva.html",
            erro="Informe um telefone válido com DDD."
        )

    # --------------------------------------
    # CONVERTER QUANTIDADE DE PESSOAS
    # --------------------------------------

    try:

        quantidade_pessoas = int(
            quantidade_pessoas
        )

    except ValueError:

        return render_template(
            "reserva.html",
            erro="A quantidade de pessoas deve ser um número válido."
        )


    # --------------------------------------
    # VALIDAR QUANTIDADE
    # --------------------------------------

    if quantidade_pessoas <= 0:

        return render_template(
            "reserva.html",
            erro="A quantidade de pessoas deve ser maior que zero."
        )


    if quantidade_pessoas > 20:

        return render_template(
            "reserva.html",
            erro="A reserva pode ter no máximo 20 pessoas."
        )


    # --------------------------------------
    # CONVERTER DATA
    # --------------------------------------

    try:

        data_reserva = datetime.strptime(
            data,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return render_template(
            "reserva.html",
            erro="A data informada é inválida."
        )


    # --------------------------------------
    # CONVERTER HORÁRIO
    # --------------------------------------

    try:

        horario_reserva = datetime.strptime(
            horario,
            "%H:%M"
        ).time()

    except ValueError:

        return render_template(
            "reserva.html",
            erro="O horário informado é inválido."
        )


    # --------------------------------------
    # VERIFICAR DATA/HORA PASSADA
    # --------------------------------------

    data_hora_reserva = datetime.combine(
        data_reserva,
        horario_reserva
    )


    if data_hora_reserva < datetime.now():

        return render_template(
            "reserva.html",
            erro="Não é possível realizar uma reserva para uma data ou horário passado."
        )


    # ======================================
    # CRIAR OBJETO ORM
    # ======================================

    nova_reserva = Reserva(

        nome_completo=nome_completo,

        telefone=telefone,

        data=data_reserva,

        horario=horario_reserva,

        quantidade_pessoas=quantidade_pessoas,

        categoria_reserva=categoria_reserva,

        observacoes=observacoes,

        status="Pendente"

    )


    # ======================================
    # SALVAR NO BANCO
    # ======================================

    try:

        db.session.add(
            nova_reserva
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        return render_template(
            "reserva.html",
            erro="Ocorreu um erro ao salvar a reserva."
        )


    # ======================================
    # PÁGINA DE CONFIRMAÇÃO
    # ======================================

    return render_template(
        "confirmacao.html",
        reserva=nova_reserva
    )


# ==========================================
# LISTAR RESERVAS
# ==========================================

@routes.route("/reservas")
def listar_reservas():

    # --------------------------------------
    # RECEBER TERMO DE BUSCA
    # --------------------------------------

    busca = request.args.get(
        "busca",
        ""
    ).strip().lower()


    # --------------------------------------
    # BUSCAR RESERVAS
    # --------------------------------------

    if busca:

        reservas = Reserva.query.filter(
            db.or_(
                Reserva.nome_completo.ilike(
                    f"%{busca}%"
                ),

                Reserva.telefone.ilike( 
                    f"%{busca}%" 
                ),

                Reserva.categoria_reserva.ilike(
                    f"%{busca}%"
                )
            )
        ).order_by(
            Reserva.data.asc(),
            Reserva.horario.asc()
        ).all()

    else:

        reservas = Reserva.query.order_by(
            Reserva.data.asc(),
            Reserva.horario.asc()
        ).all()


    return render_template(
        "lista_reservas.html",
        reservas=reservas,
        busca=busca
    )


# ==========================================
# ALTERAR STATUS
# ==========================================

@routes.route(
    "/mudar-status/<int:id>",
    methods=["POST"]
)
def mudar_status(id):

    # --------------------------------------
    # BUSCAR RESERVA PELO ID
    # --------------------------------------

    reserva = Reserva.query.get_or_404(
        id
    )


    # --------------------------------------
    # ALTERAR STATUS
    # --------------------------------------

    if reserva.status == "Pendente":

        reserva.status = "Confirmada"

    elif reserva.status == "Confirmada":

        reserva.status = "Concluída"

    else:

        reserva.status = "Pendente"


    # --------------------------------------
    # SALVAR ALTERAÇÃO
    # --------------------------------------

    db.session.commit()


    return redirect(
        url_for(
            "routes.listar_reservas"
        )
    )


# ==========================================
# EXCLUIR RESERVA
# ==========================================

@routes.route(
    "/excluir-reserva/<int:id>",
    methods=["POST"]
)
def excluir_reserva(id):

    # --------------------------------------
    # BUSCAR RESERVA PELO ID
    # --------------------------------------

    reserva = Reserva.query.get_or_404(
        id
    )


    # --------------------------------------
    # EXCLUIR REGISTRO
    # --------------------------------------

    db.session.delete(
        reserva
    )


    # --------------------------------------
    # CONFIRMAR EXCLUSÃO NO BANCO
    # --------------------------------------

    db.session.commit()


    # --------------------------------------
    # VOLTAR PARA LISTAGEM
    # --------------------------------------

    return redirect(
        url_for(
            "routes.listar_reservas"
        )
    )

