
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from datetime import datetime
from functools import wraps

from database import db
from models import Reserva, Usuario

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ==========================================
# BLUEPRINT
# ==========================================

routes = Blueprint(
    "routes",
    __name__
)


# ==========================================
# DECORADOR - LOGIN OBRIGATÓRIO
# ==========================================

def login_required(func):

    @wraps(func)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:

            return redirect(
                url_for("routes.login")
            )

        return func(
            *args,
            **kwargs
        )

    return decorated_function


# ==========================================
# DECORADOR - CLIENTE
# ==========================================

def cliente_required(func):

    @wraps(func)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:

            return redirect(
                url_for("routes.login")
            )

        if session.get("tipo") != "cliente":

            return redirect(
                url_for("routes.index")
            )

        return func(
            *args,
            **kwargs
        )

    return decorated_function


# ==========================================
# DECORADOR - ADMINISTRADOR
# ==========================================

def admin_required(func):

    @wraps(func)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:

            return redirect(
                url_for("routes.login")
            )

        if session.get("tipo") != "admin":

            return redirect(
                url_for("routes.index")
            )

        return func(
            *args,
            **kwargs
        )

    return decorated_function


# ==========================================
# LOGIN
# ==========================================

@routes.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # --------------------------------------
    # SE JÁ ESTIVER LOGADO
    # --------------------------------------

    if "usuario_id" in session:

        return redirect(
            url_for("routes.index")
        )

    erro = None

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        # ----------------------------------
        # VALIDAÇÕES
        # ----------------------------------

        if not email or not senha:

            erro = (
                "Preencha o e-mail e a senha."
            )

        else:

            usuario = Usuario.query.filter_by(
                email=email
            ).first()

            if not usuario:

                erro = (
                    "E-mail ou senha incorretos."
                )

            elif not check_password_hash(
                usuario.senha,
                senha
            ):

                erro = (
                    "E-mail ou senha incorretos."
                )

            else:

                # ------------------------------
                # CRIA SESSÃO
                # ------------------------------

                session["usuario_id"] = usuario.id
                session["nome"] = usuario.nome
                session["tipo"] = usuario.tipo

                return redirect(
                    url_for("routes.index")
                )

    return render_template(
        "login.html",
        erro=erro
    )


# ==========================================
# LOGOUT
# ==========================================

@routes.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("routes.login")
    )


# ==========================================
# CADASTRO
# ==========================================

@routes.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    if "usuario_id" in session:

        return redirect(
            url_for("routes.index")
        )

    erro = None

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        # ----------------------------------
        # VALIDAÇÕES
        # ----------------------------------

        if not nome:

            erro = "Informe seu nome."

        elif len(nome) < 2:

            erro = (
                "O nome deve possuir pelo menos "
                "2 caracteres."
            )

        elif not email or "@" not in email:

            erro = (
                "Informe um e-mail válido."
            )

        elif not telefone:

            erro = (
                "Informe seu telefone."
            )

        else:

            telefone_limpo = "".join(
                c for c in telefone
                if c.isdigit()
            )

            if len(telefone_limpo) not in [10, 11]:

                erro = (
                    "Informe um telefone válido."
                )

            elif not senha:

                erro = (
                    "Informe uma senha."
                )

            elif len(senha) < 6:

                erro = (
                    "A senha deve possuir pelo menos "
                    "6 caracteres."
                )

            elif senha != confirmar_senha:

                erro = (
                    "As senhas não coincidem."
                )

            else:

                usuario_existente = (
                    Usuario.query.filter_by(
                        email=email
                    ).first()
                )

                if usuario_existente:

                    erro = (
                        "Este e-mail já está cadastrado."
                    )

                else:

                    novo_usuario = Usuario(
                        nome=nome,
                        email=email,
                        telefone=telefone_limpo,
                        senha=generate_password_hash(
                            senha
                        ),
                        tipo="cliente"
                    )

                    db.session.add(
                        novo_usuario
                    )

                    db.session.commit()

                    # ------------------------------
                    # LOGIN AUTOMÁTICO
                    # ------------------------------

                    session["usuario_id"] = (
                        novo_usuario.id
                    )

                    session["nome"] = (
                        novo_usuario.nome
                    )

                    session["tipo"] = (
                        novo_usuario.tipo
                    )

                    return redirect(
                        url_for("routes.index")
                    )

    return render_template(
        "cadastro.html",
        erro=erro
    )


# ==========================================
# PÁGINA INICIAL
# ==========================================

@routes.route("/")
@login_required
def index():

    total_reservas = 0
    reservas_confirmadas = 0
    total_pessoas = 0

    # --------------------------------------
    # MÉTRICAS DO ADMIN
    # --------------------------------------

    if session.get("tipo") == "admin":

        total_reservas = (
            Reserva.query.count()
        )

        reservas_confirmadas = (
            Reserva.query.filter_by(
                status="Confirmada"
            ).count()
        )

        total_pessoas = (
            db.session.query(
                db.func.sum(
                    Reserva.quantidade_pessoas
                )
            ).scalar() or 0
        )

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
@cliente_required
def reserva():

    usuario = Usuario.query.get(
        session["usuario_id"]
    )

    return render_template(
        "reserva.html",
        usuario=usuario
    )


# ==========================================
# CONFIRMAÇÃO DA RESERVA
# ==========================================

@routes.route(
    "/confirmacao",
    methods=["POST"]
)
@cliente_required
def confirmacao():

    nome_completo = request.form.get(
        "nome_completo",
        ""
    ).strip()

    telefone = request.form.get(
        "telefone",
        ""
    ).strip()

    data_str = request.form.get(
        "data",
        ""
    ).strip()

    horario_str = request.form.get(
        "horario",
        ""
    ).strip()

    quantidade_str = request.form.get(
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

    erro = None

    # --------------------------------------
    # NOME
    # --------------------------------------

    if not nome_completo:

        erro = (
            "Informe o nome completo."
        )

    elif len(nome_completo) < 2:

        erro = (
            "Informe um nome válido."
        )

    # --------------------------------------
    # TELEFONE
    # --------------------------------------

    telefone_limpo = "".join(
        c for c in telefone
        if c.isdigit()
    )

    if not erro:

        if len(telefone_limpo) not in [10, 11]:

            erro = (
                "Informe um telefone válido."
            )

    # --------------------------------------
    # DATA
    # --------------------------------------

    data = None

    if not erro:

        if not data_str:

            erro = (
                "Informe a data da reserva."
            )

        else:

            try:

                data = datetime.strptime(
                    data_str,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                erro = (
                    "Informe uma data válida."
                )

    # --------------------------------------
    # HORÁRIO
    # --------------------------------------

    horario = None

    if not erro:

        if not horario_str:

            erro = (
                "Informe o horário da reserva."
            )

        else:

            try:

                horario = datetime.strptime(
                    horario_str,
                    "%H:%M"
                ).time()

            except ValueError:

                erro = (
                    "Informe um horário válido."
                )

    # --------------------------------------
    # DATA/HORA PASSADAS
    # --------------------------------------

    if not erro:

        agora = datetime.now()

        data_hora_reserva = datetime.combine(
            data,
            horario
        )

        if data_hora_reserva < agora:

            erro = (
                "A data e o horário da reserva "
                "não podem estar no passado."
            )

    # --------------------------------------
    # QUANTIDADE
    # --------------------------------------

    quantidade_pessoas = None

    if not erro:

        if not quantidade_str:

            erro = (
                "Informe a quantidade de pessoas."
            )

        else:

            try:

                quantidade_pessoas = int(
                    quantidade_str
                )

            except ValueError:

                erro = (
                    "A quantidade de pessoas "
                    "deve ser um número."
                )

        if not erro:

            if quantidade_pessoas < 1:

                erro = (
                    "A quantidade de pessoas "
                    "deve ser maior que zero."
                )

            elif quantidade_pessoas > 20:

                erro = (
                    "A quantidade máxima é de "
                    "20 pessoas."
                )

    # --------------------------------------
    # CATEGORIA
    # --------------------------------------

    if not erro:

        if not categoria_reserva:

            erro = (
                "Selecione uma categoria de reserva."
            )

    # --------------------------------------
    # ERRO
    # --------------------------------------

    if erro:

        usuario = Usuario.query.get(
            session["usuario_id"]
        )

        return render_template(
            "reserva.html",
            usuario=usuario,
            erro=erro
        )

    # --------------------------------------
    # CRIA RESERVA
    # --------------------------------------

    try:

        nova_reserva = Reserva(
            nome_completo=nome_completo,
            telefone=telefone_limpo,
            data=data,
            horario=horario,
            quantidade_pessoas=quantidade_pessoas,
            categoria_reserva=categoria_reserva,
            observacoes=observacoes,
            status="Pendente",
            usuario_id=session["usuario_id"]
        )

        db.session.add(
            nova_reserva
        )

        db.session.commit()

    except Exception:

        db.session.rollback()

        usuario = Usuario.query.get(
            session["usuario_id"]
        )

        return render_template(
            "reserva.html",
            usuario=usuario,
            erro=(
                "Não foi possível realizar a reserva. "
                "Tente novamente."
            )
        )

    return render_template(
        "confirmacao.html",
        reserva=nova_reserva
    )


# ==========================================
# MINHAS RESERVAS
# ==========================================

@routes.route("/minhas-reservas")
@cliente_required
def minhas_reservas():

    reservas = (
        Reserva.query
        .filter_by(
            usuario_id=session["usuario_id"]
        )
        .order_by(
            Reserva.data.asc(),
            Reserva.horario.asc()
        )
        .all()
    )

    return render_template(
        "minhas_reservas.html",
        reservas=reservas
    )


# ==========================================
# EDITAR RESERVA
# ==========================================

@routes.route(
    "/editar-reserva/<int:id>",
    methods=["GET", "POST"]
)
@cliente_required
def editar_reserva(id):

    # --------------------------------------
    # BUSCA RESERVA DO CLIENTE
    # --------------------------------------

    reserva = Reserva.query.filter_by(
        id=id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    # --------------------------------------
    # SOMENTE PENDENTE
    # --------------------------------------

    if reserva.status != "Pendente":

        return redirect(
            url_for("routes.minhas_reservas")
        )

    erro = None

    # --------------------------------------
    # POST
    # --------------------------------------

    if request.method == "POST":

        nome_completo = request.form.get(
            "nome_completo",
            ""
        ).strip()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        data_str = request.form.get(
            "data",
            ""
        ).strip()

        horario_str = request.form.get(
            "horario",
            ""
        ).strip()

        quantidade_str = request.form.get(
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

        # ----------------------------------
        # NOME
        # ----------------------------------

        if not nome_completo:

            erro = (
                "Informe o nome completo."
            )

        elif len(nome_completo) < 2:

            erro = (
                "Informe um nome válido."
            )

        # ----------------------------------
        # TELEFONE
        # ----------------------------------

        telefone_limpo = "".join(
            c for c in telefone
            if c.isdigit()
        )

        if not erro:

            if len(telefone_limpo) not in [10, 11]:

                erro = (
                    "Informe um telefone válido."
                )

        # ----------------------------------
        # DATA
        # ----------------------------------

        data = None

        if not erro:

            if not data_str:

                erro = (
                    "Informe a data da reserva."
                )

            else:

                try:

                    data = datetime.strptime(
                        data_str,
                        "%Y-%m-%d"
                    ).date()

                except ValueError:

                    erro = (
                        "Informe uma data válida."
                    )

        # ----------------------------------
        # HORÁRIO
        # ----------------------------------

        horario = None

        if not erro:

            if not horario_str:

                erro = (
                    "Informe o horário da reserva."
                )

            else:

                try:

                    horario = datetime.strptime(
                        horario_str,
                        "%H:%M"
                    ).time()

                except ValueError:

                    erro = (
                        "Informe um horário válido."
                    )

        # ----------------------------------
        # DATA/HORA PASSADAS
        # ----------------------------------

        if not erro:

            agora = datetime.now()

            data_hora_reserva = datetime.combine(
                data,
                horario
            )

            if data_hora_reserva < agora:

                erro = (
                    "A data e o horário da reserva "
                    "não podem estar no passado."
                )

        # ----------------------------------
        # QUANTIDADE
        # ----------------------------------

        quantidade_pessoas = None

        if not erro:

            if not quantidade_str:

                erro = (
                    "Informe a quantidade de pessoas."
                )

            else:

                try:

                    quantidade_pessoas = int(
                        quantidade_str
                    )

                except ValueError:

                    erro = (
                        "A quantidade de pessoas "
                        "deve ser um número."
                    )

            if not erro:

                if quantidade_pessoas < 1:

                    erro = (
                        "A quantidade de pessoas "
                        "deve ser maior que zero."
                    )

                elif quantidade_pessoas > 20:

                    erro = (
                        "A quantidade máxima é de "
                        "20 pessoas."
                    )

        # ----------------------------------
        # CATEGORIA
        # ----------------------------------

        if not erro:

            if not categoria_reserva:

                erro = (
                    "Selecione uma categoria de reserva."
                )

        # ----------------------------------
        # ATUALIZA
        # ----------------------------------

        if not erro:

            try:

                reserva.nome_completo = (
                    nome_completo
                )

                reserva.telefone = (
                    telefone_limpo
                )

                reserva.data = data
                reserva.horario = horario

                reserva.quantidade_pessoas = (
                    quantidade_pessoas
                )

                reserva.categoria_reserva = (
                    categoria_reserva
                )

                reserva.observacoes = (
                    observacoes
                )

                # Continua pendente após edição
                reserva.status = "Pendente"

                db.session.commit()

                return redirect(
                    url_for(
                        "routes.minhas_reservas"
                    )
                )

            except Exception:

                db.session.rollback()

                erro = (
                    "Não foi possível atualizar "
                    "a reserva. Tente novamente."
                )

    return render_template(
        "editar_reserva.html",
        reserva=reserva,
        erro=erro
    )


# ==========================================
# CANCELAR RESERVA
# ==========================================

@routes.route(
    "/cancelar-reserva/<int:id>",
    methods=["POST"]
)
@cliente_required
def cancelar_reserva(id):

    reserva = Reserva.query.filter_by(
        id=id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    if reserva.status == "Pendente":

        reserva.status = "Cancelada"

        db.session.commit()

    return redirect(
        url_for(
            "routes.minhas_reservas"
        )
    )


# ==========================================
# MEU CADASTRO
# ==========================================

@routes.route(
    "/meu-cadastro",
    methods=["GET", "POST"]
)
@cliente_required
def meu_cadastro():

    usuario = Usuario.query.get(
        session["usuario_id"]
    )

    erro = None
    sucesso = None

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        nova_senha = request.form.get(
            "senha",
            ""
        )

        # ----------------------------------
        # VALIDAÇÃO
        # ----------------------------------

        if not nome:

            erro = "Informe seu nome."

        elif len(nome) < 2:

            erro = (
                "O nome deve possuir pelo menos "
                "2 caracteres."
            )

        elif not email or "@" not in email:

            erro = (
                "Informe um e-mail válido."
            )

        elif not telefone:

            erro = (
                "Informe seu telefone."
            )

        else:

            telefone_limpo = "".join(
                c for c in telefone
                if c.isdigit()
            )

            if len(telefone_limpo) not in [10, 11]:

                erro = (
                    "Informe um telefone válido."
                )

        # ----------------------------------
        # E-MAIL
        # ----------------------------------

        if not erro:

            outro_usuario = Usuario.query.filter(
                Usuario.email == email,
                Usuario.id != usuario.id
            ).first()

            if outro_usuario:

                erro = (
                    "Este e-mail já está sendo utilizado."
                )

        # ----------------------------------
        # SENHA
        # ----------------------------------

        if not erro and nova_senha:

            if len(nova_senha) < 6:

                erro = (
                    "A nova senha deve possuir "
                    "pelo menos 6 caracteres."
                )

        # ----------------------------------
        # ATUALIZA
        # ----------------------------------

        if not erro:

            usuario.nome = nome
            usuario.email = email
            usuario.telefone = telefone_limpo

            if nova_senha:

                usuario.senha = (
                    generate_password_hash(
                        nova_senha
                    )
                )

            db.session.commit()

            session["nome"] = usuario.nome

            sucesso = (
                "Seus dados foram atualizados "
                "com sucesso."
            )

    return render_template(
        "meu_cadastro.html",
        usuario=usuario,
        erro=erro,
        sucesso=sucesso
    )


# ==========================================
# LISTA DE RESERVAS - ADMIN
# ==========================================

@routes.route("/reservas")
@admin_required
def lista_reservas():

    busca = request.args.get(
        "busca",
        ""
    ).strip()

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
# MUDAR STATUS - ADMIN
# ==========================================

@routes.route(
    "/mudar-status/<int:id>",
    methods=["POST"]
)
@admin_required
def mudar_status(id):

    reserva = Reserva.query.get_or_404(id)

    # --------------------------------------
    # CANCELADA NÃO PODE SER REATIVADA
    # --------------------------------------

    if reserva.status == "Cancelada":

        return redirect(
            url_for(
                "routes.lista_reservas"
            )
        )

    # --------------------------------------
    # CICLO
    # --------------------------------------

    if reserva.status == "Pendente":

        reserva.status = "Confirmada"

    elif reserva.status == "Confirmada":

        reserva.status = "Concluída"

    else:

        reserva.status = "Pendente"

    db.session.commit()

    return redirect(
        url_for(
            "routes.lista_reservas"
        )
    )


# ==========================================
# EXCLUIR RESERVA - ADMIN
# ==========================================

@routes.route(
    "/excluir-reserva/<int:id>",
    methods=["POST"]
)
@admin_required
def excluir_reserva(id):

    reserva = Reserva.query.get_or_404(id)

    db.session.delete(
        reserva
    )

    db.session.commit()

    return redirect(
        url_for(
            "routes.lista_reservas"
        )
    )

