from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ==========================================
# LISTA DE RESERVAS
# ==========================================

reservas = []


# ==========================================
# ROTA - PÁGINA INICIAL
# ==========================================

@app.route("/")
def index():

    # Total de reservas
    total_reservas = len(reservas)

    # Reservas confirmadas
    reservas_confirmadas = sum(
        1 for reserva in reservas
        if reserva["status"] == "Confirmada"
    )

    # Total de pessoas
    total_pessoas = sum(
        reserva["pessoas"] for reserva in reservas
    )

    return render_template(
        "index.html",
        total_reservas=total_reservas,
        reservas_confirmadas=reservas_confirmadas,
        total_pessoas=total_pessoas
    )


# ==========================================
# ROTA - PÁGINA DE RESERVA
# ==========================================

@app.route("/reserva")
def reserva():
    return render_template("reserva.html")


# ==========================================
# ROTA - RECEBIMENTO DA RESERVA
# ==========================================

@app.route("/confirmacao", methods=["POST"])
def confirmacao():

    # Recebendo os dados do formulário
    nome = request.form.get("nome", "").strip()
    data = request.form.get("data", "").strip()
    horario = request.form.get("horario", "").strip()
    pessoas = request.form.get("pessoas", "").strip()
    observacao = request.form.get("observacao", "").strip()

    # ==========================================
    # VALIDAÇÕES
    # ==========================================

    # Campos obrigatórios
    if not nome or not data or not horario or not pessoas:
        return render_template(
            "reserva.html",
            erro="Preencha todos os campos obrigatórios."
        )

    # Nome válido
    if len(nome) < 2:
        return render_template(
            "reserva.html",
            erro="Digite um nome válido."
        )

    # Verificar se pessoas é um número
    try:
        pessoas = int(pessoas)

    except ValueError:
        return render_template(
            "reserva.html",
            erro="O número de pessoas deve ser um valor válido."
        )

    # Não permitir zero ou números negativos
    if pessoas <= 0:
        return render_template(
            "reserva.html",
            erro="O número de pessoas deve ser maior que zero."
        )

    # Limite máximo
    if pessoas > 20:
        return render_template(
            "reserva.html",
            erro="A reserva pode ter no máximo 20 pessoas."
        )

    # ==========================================
    # CRIANDO A RESERVA
    # ==========================================

    nova_reserva = {
        "id": len(reservas) + 1,
        "nome": nome,
        "data": data,
        "horario": horario,
        "pessoas": pessoas,
        "observacao": observacao,
        "status": "Confirmada"
    }

    # Adiciona a reserva à memória
    reservas.append(nova_reserva)

    # ==========================================
    # PÁGINA DE CONFIRMAÇÃO
    # ==========================================

    return render_template(
        "confirmacao.html",
        nome=nome,
        data=data,
        horario=horario,
        pessoas=pessoas,
        observacao=observacao
    )


# ==========================================
# ROTA - LISTA DE RESERVAS
# ==========================================

@app.route("/reservas")
def listar_reservas():

    # Recebe o texto da busca
    busca = request.args.get("busca", "").strip().lower()

    # Se houver busca, filtra pelo nome
    if busca:

        reservas_filtradas = [
            reserva for reserva in reservas
            if busca in reserva["nome"].lower()
        ]

    else:

        reservas_filtradas = reservas

    return render_template(
        "lista_reservas.html",
        reservas=reservas_filtradas,
        busca=busca
    )


# ==========================================
# ROTA - ALTERAR STATUS
# ==========================================

@app.route("/mudar-status/<int:id>", methods=["POST"])
def mudar_status(id):

    for reserva in reservas:

        if reserva["id"] == id:

            if reserva["status"] == "Confirmada":
                reserva["status"] = "Concluída"

            else:
                reserva["status"] = "Confirmada"

            break

    return redirect(url_for("listar_reservas"))


# ==========================================
# INICIALIZAÇÃO DO SISTEMA
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)