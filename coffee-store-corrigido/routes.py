import os
import uuid

import hmac
import secrets

from flask import abort, current_app, flash
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

import time                        # Controle de tempo e pausas
import threading                   # Execução de tarefas em segundo plano
from datetime import datetime      # Manipulação e formatação de datas/horários
from functools import wraps        # Garante que os decoradores criados funcionem bem

from flask import (
    Blueprint,                     # Organização de rotas em módulos separados
    render_template,               # Renderiza as páginas HTML na tela
    request,                       # Captura dados enviados pelo usuário (formulários/URLs)
    redirect,                      # Redireciona o usuário para outra página
    url_for,                       # Gera os endereços das rotas dinamicamente
    session,                       # Guarda dados do usuário logado
    jsonify,                       # Converte respostas do código para o formato JSON
)
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from models import Reserva, Usuario
from utils import (
    CATEGORIAS,
    email_valido,
    nome_valido,
    processar_imagem,
    telefone_valido,
)

# Instância compartilhada de Cache
cache = Cache()

routes = Blueprint("routes", __name__)

# ==========================================
# GERENCIAMENTO DE FOTOS DE PERFIL
# ==========================================

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp"}


def extensao_permitida(nome_arquivo):
    # usa o nome ORIGINAL: secure_filename("日本.png") vira "png" e perdia a extensão
    return os.path.splitext(nome_arquivo)[1].lstrip(".").lower() in EXTENSOES_PERMITIDAS


def salvar_foto(arquivo):
    if not extensao_permitida(arquivo.filename or ""):
        raise ValueError("Formato inválido! Envie PNG, JPG, JPEG ou WEBP.")

    # valida pelo conteúdo real, remove EXIF/GPS e reduz a imagem
    dados, extensao = processar_imagem(arquivo.stream)
    nome_novo = f"{uuid.uuid4().hex}.{extensao}"
    caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], nome_novo)
    with open(caminho, "wb") as f:
        f.write(dados)
    return nome_novo


def excluir_foto(nome_arquivo):
    if not nome_arquivo or nome_arquivo == "padrao.png":
        return

    # Impede caminhos fora da pasta de uploads
    if os.path.basename(nome_arquivo) != nome_arquivo:
        return

    caminho = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        nome_arquivo
    )

    if os.path.isfile(caminho):
        os.remove(caminho)


# ==========================================
# SISTEMA DE TAREFAS ASSÍNCRONAS (BACKGROUND WORKER)
# ==========================================


def enviar_notificacao_assincrona(tipo_evento, detalhes):
    """
    Função assíncrona executada em segundo plano para envio de notificações/e-mails sem travar a resposta da API.
    """

    def worker():
        # Simula o processamento demorado de um serviço de mensageria / e-mail
        time.sleep(2)
        print(
            f"[ASYNC WORKER] Evento '{tipo_evento}' processado com sucesso. Detalhes: {detalhes}"
        )

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()


def reserva_duplicada(usuario_id, data, horario, ignorar_id=None):
    consulta = Reserva.query.filter(
        Reserva.usuario_id == usuario_id,
        Reserva.data == data,
        Reserva.horario == horario,
        Reserva.ativo.is_(True),
        Reserva.status != "Cancelada",
    )
    if ignorar_id:
        consulta = consulta.filter(Reserva.id != ignorar_id)
    return consulta.first() is not None


# ==========================================
# PROTEÇÃO CSRF E TRATAMENTO DE ERROS
# ==========================================


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


@routes.app_context_processor
def injetar_csrf():
    return {"csrf_token": csrf_token}


@routes.before_app_request
def verificar_csrf():
    if request.method == "POST":
        enviado = request.form.get("csrf_token", "")
        if not hmac.compare_digest(enviado, session.get("_csrf", "")):
            abort(400)


@routes.app_errorhandler(400)
def requisicao_invalida(_e):
    return "Sessão expirada ou requisição inválida. Volte e recarregue a página.", 400


@routes.app_errorhandler(413)
def arquivo_grande(_e):
    flash("Arquivo muito grande. O limite é 5 MB.", "erro")
    if "usuario_id" in session:
        return redirect(url_for("routes.meu_cadastro"))
    return redirect(url_for("routes.login"))


# ==========================================
# DECORADORES DE AUTENTICAÇÃO
# ==========================================


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("routes.login"))
        return func(*args, **kwargs)

    return decorated_function


def cliente_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("routes.login"))
        if session.get("tipo") != "cliente":
            return redirect(url_for("routes.index"))
        return func(*args, **kwargs)

    return decorated_function


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("routes.login"))
        if session.get("tipo") != "admin":
            return redirect(url_for("routes.index"))
        return func(*args, **kwargs)

    return decorated_function


# ==========================================
# ROTA DE CACHE (CATÁLOGO DE PRODUTOS / CARDÁPIO)
# ==========================================


@routes.route("/catalogo")
@cache.cached(
    timeout=60,
    make_cache_key=lambda: f"catalogo:{session.get('tipo', 'anonimo')}",
)  # cache separado por perfil (o menu depende da sessão)
def catalogo():
    """
    Exemplo de rota otimizada com Cache para consulta de catálogo/produtos.
    """
    # Dados simulados do catálogo de produtos do café
    produtos = [

    # =========================
    # CAFÉS
    # =========================

    {
        "id": 1,
        "nome": "Café Espresso",
        "preco": "R$ 6,00",
        "categoria": "Cafés"
    },
    {
        "id": 2,
        "nome": "Café Espresso Duplo",
        "preco": "R$ 8,00",
        "categoria": "Cafés"
    },
    {
        "id": 3,
        "nome": "Cappuccino Tradicional",
        "preco": "R$ 10,00",
        "categoria": "Cafés"
    },
    {
        "id": 4,
        "nome": "Cappuccino de Chocolate",
        "preco": "R$ 12,00",
        "categoria": "Cafés"
    },
    {
        "id": 5,
        "nome": "Café com Leite",
        "preco": "R$ 8,00",
        "categoria": "Cafés"
    },
    {
        "id": 6,
        "nome": "Mocha",
        "preco": "R$ 13,00",
        "categoria": "Cafés"
    },
    {
        "id": 7,
        "nome": "Latte",
        "preco": "R$ 11,00",
        "categoria": "Cafés"
    },
    {
        "id": 8,
        "nome": "Latte Caramelo",
        "preco": "R$ 13,00",
        "categoria": "Cafés"
    },

    # =========================
    # BEBIDAS
    # =========================

    {
        "id": 9,
        "nome": "Chocolate Quente",
        "preco": "R$ 10,00",
        "categoria": "Bebidas"
    },
    {
        "id": 10,
        "nome": "Chocolate Quente Especial",
        "preco": "R$ 14,00",
        "categoria": "Bebidas"
    },
    {
        "id": 11,
        "nome": "Chá de Camomila",
        "preco": "R$ 7,00",
        "categoria": "Bebidas"
    },
    {
        "id": 12,
        "nome": "Chá de Frutas Vermelhas",
        "preco": "R$ 8,00",
        "categoria": "Bebidas"
    },
    {
        "id": 13,
        "nome": "Suco de Laranja",
        "preco": "R$ 9,00",
        "categoria": "Bebidas"
    },
    {
        "id": 14,
        "nome": "Suco de Morango",
        "preco": "R$ 10,00",
        "categoria": "Bebidas"
    },
    {
        "id": 15,
        "nome": "Limonada Suíça",
        "preco": "R$ 11,00",
        "categoria": "Bebidas"
    },
    {
        "id": 16,
        "nome": "Água Mineral",
        "preco": "R$ 4,00",
        "categoria": "Bebidas"
    },

    # =========================
    # DOCES
    # =========================

    {
        "id": 17,
        "nome": "Torta de Maçã",
        "preco": "R$ 14,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 18,
        "nome": "Cheesecake de Frutas Vermelhas",
        "preco": "R$ 16,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 19,
        "nome": "Brownie com Chocolate",
        "preco": "R$ 12,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 20,
        "nome": "Bolo de Chocolate",
        "preco": "R$ 10,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 21,
        "nome": "Bolo de Cenoura",
        "preco": "R$ 9,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 22,
        "nome": "Cookie de Chocolate",
        "preco": "R$ 7,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 23,
        "nome": "Cookie de Baunilha",
        "preco": "R$ 7,00",
        "categoria": "Sobremesas"
    },
    {
        "id": 24,
        "nome": "Pudim de Leite",
        "preco": "R$ 11,00",
        "categoria": "Sobremesas"
    },

    # =========================
    # SALGADOS
    # =========================

    {
        "id": 25,
        "nome": "Pão de Queijo",
        "preco": "R$ 5,00",
        "categoria": "Salgados"
    },
    {
        "id": 26,
        "nome": "Pão de Queijo Recheado",
        "preco": "R$ 8,00",
        "categoria": "Salgados"
    },
    {
        "id": 27,
        "nome": "Coxinha de Frango",
        "preco": "R$ 9,00",
        "categoria": "Salgados"
    },
    {
        "id": 28,
        "nome": "Coxinha com Catupiry",
        "preco": "R$ 10,00",
        "categoria": "Salgados"
    },
    {
        "id": 29,
        "nome": "Empada de Frango",
        "preco": "R$ 9,00",
        "categoria": "Salgados"
    },
    {
        "id": 30,
        "nome": "Empada de Palmito",
        "preco": "R$ 9,00",
        "categoria": "Salgados"
    },
    {
        "id": 31,
        "nome": "Croissant de Presunto e Queijo",
        "preco": "R$ 13,00",
        "categoria": "Salgados"
    },
    {
        "id": 32,
        "nome": "Quiche de Queijo",
        "preco": "R$ 14,00",
        "categoria": "Salgados"
    },

    # =========================
    # LANCHES
    # =========================

    {
        "id": 33,
        "nome": "Misto Quente",
        "preco": "R$ 12,00",
        "categoria": "Lanches"
    },
    {
        "id": 34,
        "nome": "Sanduíche Natural de Frango",
        "preco": "R$ 15,00",
        "categoria": "Lanches"
    },
    {
        "id": 35,
        "nome": "Sanduíche de Presunto e Queijo",
        "preco": "R$ 14,00",
        "categoria": "Lanches"
    },
    {
        "id": 36,
        "nome": "Tostex Especial",
        "preco": "R$ 16,00",
        "categoria": "Lanches"
    },

    # =========================
    # COMBOS
    # =========================

    {
        "id": 37,
        "nome": "Combo Café da Manhã",
        "preco": "R$ 22,00",
        "categoria": "Combos"
    },
    {
        "id": 38,
        "nome": "Combo Cappuccino + Brownie",
        "preco": "R$ 20,00",
        "categoria": "Combos"
    },
    {
        "id": 39,
        "nome": "Combo Café + Pão de Queijo",
        "preco": "R$ 12,00",
        "categoria": "Combos"
    },
    {
        "id": 40,
        "nome": "Combo Croissant + Café",
        "preco": "R$ 18,00",
        "categoria": "Combos"
    }
]
    return render_template("catalogo.html", produtos=produtos)


# ==========================================
# AUTHENTICATION (LOGIN, LOGOUT, CADASTRO)
# ==========================================


@routes.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("routes.index"))

    erro = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            erro = "Preencha o e-mail e a senha."
        else:
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario or not check_password_hash(usuario.senha, senha):
                erro = "E-mail ou senha incorretos."
            else:
                session["usuario_id"] = usuario.id
                session["nome"] = usuario.nome
                session["tipo"] = usuario.tipo
                return redirect(url_for("routes.index"))

    return render_template("login.html", erro=erro)


@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))


@routes.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if "usuario_id" in session:
        return redirect(url_for("routes.index"))

    erro = None
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        telefone_limpo = "".join(c for c in telefone if c.isdigit())

        if not nome_valido(nome):
            erro = "O nome deve possuir pelo menos 2 caracteres."
        elif not email_valido(email):
            erro = "Informe um e-mail válido."
        elif not telefone_valido(telefone_limpo):
            erro = "Informe um telefone válido."
        elif not senha or len(senha) < 6:
            erro = "A senha deve possuir pelo menos 6 caracteres."
        elif senha != confirmar_senha:
            erro = "As senhas não coincidem."
        elif Usuario.query.filter_by(email=email).first():
            erro = "Este e-mail já está cadastrado."
        else:
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                telefone=telefone_limpo,
                senha=generate_password_hash(senha),
                tipo="cliente",
            )
            db.session.add(novo_usuario)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_template(
                    "cadastro.html", erro="Este e-mail já está cadastrado."
                )

            # Disparo Assíncrono de Boas-Vindas
            enviar_notificacao_assincrona("NOVO_USUARIO", f"Usuário {email} criado.")

            session["usuario_id"] = novo_usuario.id
            session["nome"] = novo_usuario.nome
            session["tipo"] = novo_usuario.tipo
            return redirect(url_for("routes.index"))

    return render_template("cadastro.html", erro=erro)


# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================


@routes.route("/")
@login_required
def index():
    total_reservas = 0
    reservas_confirmadas = 0
    total_pessoas = 0

    if session.get("tipo") == "admin":
        ativas = Reserva.query.filter_by(ativo=True)
        total_reservas = ativas.count()
        reservas_confirmadas = ativas.filter_by(status="Confirmada").count()
        total_pessoas = (
            db.session.query(db.func.sum(Reserva.quantidade_pessoas))
            .filter(Reserva.ativo.is_(True), Reserva.status != "Cancelada")
            .scalar()
            or 0
        )

    return render_template(
        "index.html",
        total_reservas=total_reservas,
        reservas_confirmadas=reservas_confirmadas,
        total_pessoas=total_pessoas,
    )


# ==========================================
# GESTÃO DE RESERVAS (CLIENTE)
# ==========================================


@routes.route("/reserva")
@cliente_required
def reserva():
    usuario = Usuario.query.get(session["usuario_id"])
    return render_template("reserva.html", usuario=usuario)


@routes.route("/confirmacao", methods=["POST"])
@cliente_required
def confirmacao():
    nome_completo = request.form.get("nome_completo", "").strip()
    telefone = request.form.get("telefone", "").strip()
    data_str = request.form.get("data", "").strip()
    horario_str = request.form.get("horario", "").strip()
    quantidade_str = request.form.get("quantidade_pessoas", "").strip()
    categoria_reserva = request.form.get("categoria_reserva", "").strip()
    observacoes = request.form.get("observacoes", "").strip()

    telefone_limpo = "".join(c for c in telefone if c.isdigit())
    erro = None

    if not nome_valido(nome_completo):
        erro = "Informe um nome válido."
    elif not telefone_valido(telefone_limpo):
        erro = "Informe um telefone válido."

    data = None
    if not erro:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            erro = "Informe uma data válida."

    horario = None
    if not erro:
        try:
            horario = datetime.strptime(horario_str, "%H:%M").time()
        except ValueError:
            erro = "Informe um horário válido."

    if not erro and datetime.combine(data, horario) < datetime.now():
        erro = "A data e o horário da reserva não podem estar no passado."

    quantidade_pessoas = None
    if not erro:
        try:
            quantidade_pessoas = int(quantidade_str)
            if quantidade_pessoas < 1 or quantidade_pessoas > 20:
                erro = "A quantidade de pessoas deve ser entre 1 e 20."
        except ValueError:
            erro = "A quantidade de pessoas deve ser um número."

    if not erro and categoria_reserva not in CATEGORIAS:
        erro = "Selecione uma categoria de reserva válida."

    if not erro and reserva_duplicada(session["usuario_id"], data, horario):
        erro = "Você já possui uma reserva para esta data e horário."

    if erro:
        usuario = Usuario.query.get(session["usuario_id"])
        return render_template("reserva.html", usuario=usuario, erro=erro)

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
            usuario_id=session["usuario_id"],
        )
        db.session.add(nova_reserva)
        db.session.commit()

        # Dispara notificação assíncrona
        enviar_notificacao_assincrona(
            "NOVA_RESERVA", f"Reserva #{nova_reserva.id} criada por {nome_completo}."
        )

    except Exception:
        db.session.rollback()
        usuario = Usuario.query.get(session["usuario_id"])
        return render_template(
            "reserva.html",
            usuario=usuario,
            erro="Não foi possível realizar a reserva. Tente novamente.",
        )

    # Post/Redirect/Get: F5 não recria a reserva
    return redirect(url_for("routes.ver_confirmacao", id=nova_reserva.id))


@routes.route("/confirmacao/<int:id>")
@cliente_required
def ver_confirmacao(id):
    reserva = Reserva.query.filter_by(
        id=id, usuario_id=session["usuario_id"], ativo=True
    ).first_or_404()
    return render_template("confirmacao.html", reserva=reserva)


@routes.route("/minhas-reservas")
@cliente_required
def minhas_reservas():
    reservas = (
        Reserva.query.filter_by(usuario_id=session["usuario_id"], ativo=True)
        .order_by(Reserva.data.asc(), Reserva.horario.asc())
        .all()
    )
    usuario = db.session.get(Usuario, session["usuario_id"])

    return render_template("minhas_reservas.html", reservas=reservas, usuario=usuario
)


@routes.route("/editar-reserva/<int:id>", methods=["GET", "POST"])
@cliente_required
def editar_reserva(id):
    reserva = Reserva.query.filter_by(
        id=id, usuario_id=session["usuario_id"], ativo=True
    ).first_or_404()

    if reserva.status != "Pendente":
        return redirect(url_for("routes.minhas_reservas"))

    erro = None
    if request.method == "POST":
        nome_completo = request.form.get("nome_completo", "").strip()
        telefone = request.form.get("telefone", "").strip()
        data_str = request.form.get("data", "").strip()
        horario_str = request.form.get("horario", "").strip()
        quantidade_str = request.form.get("quantidade_pessoas", "").strip()
        categoria_reserva = request.form.get("categoria_reserva", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        telefone_limpo = "".join(c for c in telefone if c.isdigit())

        if not nome_valido(nome_completo):
            erro = "Informe um nome válido."
        elif not telefone_valido(telefone_limpo):
            erro = "Informe um telefone válido."

        data, horario = None, None
        if not erro:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d").date()
                horario = datetime.strptime(horario_str, "%H:%M").time()
            except ValueError:
                erro = "Data ou horário inválido."

        if not erro and datetime.combine(data, horario) < datetime.now():
            erro = "A data e o horário não podem estar no passado."

        quantidade_pessoas = None
        if not erro:
            try:
                quantidade_pessoas = int(quantidade_str)
                if quantidade_pessoas < 1 or quantidade_pessoas > 20:
                    erro = "A quantidade deve ser entre 1 e 20."
            except ValueError:
                erro = "Quantidade de pessoas inválida."

        if not erro and categoria_reserva not in CATEGORIAS:
            erro = "Selecione uma categoria de reserva válida."

        if not erro and reserva_duplicada(
            session["usuario_id"], data, horario, ignorar_id=reserva.id
        ):
            erro = "Você já possui uma reserva para esta data e horário."

        if not erro:
            try:
                reserva.nome_completo = nome_completo
                reserva.telefone = telefone_limpo
                reserva.data = data
                reserva.horario = horario
                reserva.quantidade_pessoas = quantidade_pessoas
                reserva.categoria_reserva = categoria_reserva
                reserva.observacoes = observacoes
                reserva.status = "Pendente"

                db.session.commit()
                return redirect(url_for("routes.minhas_reservas"))
            except Exception:
                db.session.rollback()
                erro = "Não foi possível atualizar a reserva."

    return render_template("editar_reserva.html", reserva=reserva, erro=erro)


@routes.route("/cancelar-reserva/<int:id>", methods=["POST"])
@cliente_required
def cancelar_reserva(id):
    reserva = Reserva.query.filter_by(
        id=id, usuario_id=session["usuario_id"], ativo=True
    ).first_or_404()

    if reserva.status == "Pendente":
        reserva.status = "Cancelada"
        db.session.commit()

        # Dispara notificação assíncrona
        enviar_notificacao_assincrona("CANCELAMENTO", f"Reserva #{id} cancelada.")

    return redirect(url_for("routes.minhas_reservas"))


@routes.route("/meu-cadastro", methods=["GET", "POST"])
@cliente_required
def meu_cadastro():
    usuario = db.session.get(Usuario, session["usuario_id"])

    erro = None
    sucesso = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        nova_senha = request.form.get("senha", "")

        foto = request.files.get("campo_imagem")
        remover_foto = request.form.get("remover_foto") == "1"

        telefone_limpo = "".join(
            c for c in telefone if c.isdigit()
        )

        # Validação dos dados
        if not nome_valido(nome):
            erro = "O nome deve possuir pelo menos 2 caracteres."

        elif not email_valido(email):
            erro = "Informe um e-mail válido."

        elif not telefone_valido(telefone_limpo):
            erro = "Informe um telefone válido."

        if not erro:
            outro = Usuario.query.filter(
                Usuario.email == email,
                Usuario.id != usuario.id
            ).first()

            if outro:
                erro = "Este e-mail já está sendo utilizado."

        if not erro and nova_senha and len(nova_senha) < 6:
            erro = "A nova senha deve possuir pelo menos 6 caracteres."

        # Validação da foto
        if not erro and foto and foto.filename:
            if not extensao_permitida(foto.filename):
                erro = (
                    "Formato inválido! "
                    "Envie PNG, JPG, JPEG ou WEBP."
                )

        if erro:
            flash(erro, "erro")

        else:
            foto_antiga = usuario.foto or "padrao.png"
            nova_foto = None

            try:
                if foto and foto.filename and not remover_foto:
                    nova_foto = salvar_foto(foto)

                usuario.nome = nome
                usuario.email = email
                usuario.telefone = telefone_limpo

                if nova_senha:
                    usuario.senha = generate_password_hash(
                        nova_senha
                    )

                if nova_foto:
                    usuario.foto = nova_foto

                elif remover_foto:
                    usuario.foto = "padrao.png"

                db.session.commit()

                session["nome"] = usuario.nome

                # Apaga a foto antiga somente após salvar
                if foto_antiga != usuario.foto:
                    excluir_foto(foto_antiga)

                sucesso = "Perfil atualizado com sucesso!"
                flash(sucesso, "sucesso")

                return redirect(
                    url_for("routes.meu_cadastro")
                )

            except ValueError as e:
                db.session.rollback()

                if nova_foto:
                    excluir_foto(nova_foto)

                erro = str(e)
                flash(erro, "erro")

            except Exception:
                db.session.rollback()

                if nova_foto:
                    excluir_foto(nova_foto)

                erro = "Não foi possível atualizar seu perfil."
                flash(erro, "erro")

    return render_template(
        "meu_cadastro.html",
        usuario=usuario,
        erro=erro,
        sucesso=sucesso
    )


# ==========================================
# PAINEL ADMINISTRATIVO
# ==========================================


@routes.route("/reservas")
@admin_required
def lista_reservas():
    busca = request.args.get("busca", "").strip()

    if busca:
        reservas = (
            Reserva.query.filter(
                Reserva.ativo.is_(True),
                db.or_(
                    Reserva.nome_completo.ilike(f"%{busca}%"),
                    Reserva.telefone.ilike(f"%{busca}%"),
                    Reserva.categoria_reserva.ilike(f"%{busca}%"),
                )
            )
            .order_by(Reserva.data.asc(), Reserva.horario.asc())
            .all()
        )
    else:
        reservas = (
            Reserva.query.filter_by(ativo=True)
            .order_by(Reserva.data.asc(), Reserva.horario.asc())
            .all()
        )

    return render_template(
        "lista_reservas.html",
        reservas=reservas,
        busca=busca
    )


@routes.route("/mudar-status/<int:id>", methods=["POST"])
@admin_required
def mudar_status(id):
    reserva = Reserva.query.filter_by(id=id, ativo=True).first_or_404()

    if reserva.status != "Cancelada":
        if reserva.status == "Pendente":
            reserva.status = "Confirmada"
        elif reserva.status == "Confirmada":
            reserva.status = "Concluída"
        else:
            reserva.status = "Pendente"

        db.session.commit()

        # Notificação assíncrona de atualização
        enviar_notificacao_assincrona(
            "MUDANCA_STATUS", f"Reserva #{id} mudou para {reserva.status}."
        )

    return redirect(url_for("routes.lista_reservas"))


@routes.route("/excluir-reserva/<int:id>", methods=["POST"])
@admin_required
def excluir_reserva(id):
    reserva = db.get_or_404(Reserva, id)

    reserva.ativo = False
    db.session.commit()

    flash("Reserva excluída com sucesso!", "sucesso")

    return redirect(url_for("routes.lista_reservas"))


@routes.route("/excluir-minha-conta", methods=["POST"])
@cliente_required
def excluir_minha_conta():
    usuario = db.session.get(Usuario, session["usuario_id"])

    if not usuario:
        flash("Usuário não encontrado.", "erro")
        return redirect(url_for("routes.login"))

    foto_antiga = usuario.foto

    try:
        # Preserva as reservas, mas desvincula o usuário
        Reserva.query.filter_by(
            usuario_id=usuario.id
        ).update({"usuario_id": None})

        # Exclui o usuário do banco
        db.session.delete(usuario)
        db.session.commit()

    except Exception:
        db.session.rollback()
        flash("Erro ao excluir a conta.", "erro")
        return redirect(url_for("routes.meu_cadastro"))

    # Exclui a foto somente após confirmar no banco
    excluir_foto(foto_antiga)

    session.clear()

    flash("Sua conta foi excluída com sucesso!", "sucesso")

    return redirect(url_for("routes.login"))