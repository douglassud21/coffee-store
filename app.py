from flask import Flask, render_template, request

app = Flask(__name__)


# ==========================================
# ROTA - PÁGINA INICIAL
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


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

    # Recebendo os dados enviados pelo formulário
    nome = request.form.get("nome")
    data = request.form.get("data")
    horario = request.form.get("horario")
    pessoas = request.form.get("pessoas")
    observacao = request.form.get("observacao")

    # Enviando os dados para a página de confirmação
    return render_template(
        "confirmacao.html",
        nome=nome,
        data=data,
        horario=horario,
        pessoas=pessoas,
        observacao=observacao
    )


# ==========================================
# INICIALIZAÇÃO DO SISTEMA
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)