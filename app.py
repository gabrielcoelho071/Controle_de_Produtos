from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Produto, Estoque, db_session, init_db
from sqlalchemy import select

app = Flask(__name__)
app.secret_key = "meusegredo"  # troque depois


# ============================
# PROTEGER ROTAS
# ============================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login primeiro.", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


# ============================
# LOGIN
# ============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        stmt = select(Usuario).where(Usuario.email == email)
        usuario = db_session.execute(stmt).scalar()

        if not usuario or not check_password_hash(usuario.senha, senha):
            flash("E-mail ou senha incorretos!", "danger")
            return redirect("/login")

        session["usuario_id"] = usuario.id_usuario
        session["usuario_nome"] = usuario.nome

        flash("Login realizado!", "success")
        return redirect("/")

    return render_template("login.html")


# ============================
# LOGOUT
# ============================
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "info")
    return redirect("/login")


# ============================
# CADASTRAR USUÁRIO
# ============================
@app.route("/usuario/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        stmt = select(Usuario).where(Usuario.email == email)
        existe = db_session.execute(stmt).scalar()

        if existe:
            flash("Email já cadastrado!", "danger")
            return redirect("/usuario/cadastrar")

        novo = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )
        novo.save()

        flash("Usuário cadastrado!", "success")
        return redirect("/login")

    return render_template("cadastrar_usuario.html")


# ============================
# HOME
# ============================
@app.route("/")
@login_required
def home():
    return render_template("index.html")


# ============================
# LISTAR PRODUTOS
# ============================
@app.route("/produtos")
@login_required
def produtos():
    lista = db_session.execute(select(Produto)).scalars().all()
    return render_template("lista_produtos.html", produtos=lista)


# ============================
# CADASTRAR PRODUTO
# ============================
@app.route("/produto/cadastrar", methods=["GET", "POST"])
@login_required
def cadastrar_produto():
    if request.method == "POST":
        p = Produto(
            nome=request.form["nome"],
            preco=float(request.form["preco"]),
            categoria=request.form["categoria"]
        )
        p.save()

        flash("Produto cadastrado!", "success")
        return redirect("/produtos")

    return render_template("cadastro_produto.html")


# ============================
# EDITAR PRODUTO
# ============================
@app.route("/produto/<int:id>", methods=["GET", "POST"])
@login_required
def editar_produto(id):
    produto = db_session.get(Produto, id)

    if not produto:
        flash("Produto não encontrado!", "danger")
        return redirect("/produtos")

    if request.method == "POST":
        produto.nome = request.form["nome"]
        produto.preco = float(request.form["preco"])
        produto.categoria = request.form["categoria"]
        produto.save()

        flash("Produto atualizado!", "success")
        return redirect("/produtos")

    return render_template("editar_produto.html", produto=produto)


# ============================
# DELETAR PRODUTO
# ============================
@app.route("/produto/<int:id>/delete")
@login_required
def deletar_produto(id):
    produto = db_session.get(Produto, id)

    if not produto:
        flash("Produto inexistente.", "danger")
        return redirect("/produtos")

    produto.delete()
    flash("Produto removido!", "danger")
    return redirect("/produtos")


# ============================
# HISTÓRICO DE ESTOQUE
# ============================
@app.route("/estoque/<int:id_produto>")
@login_required
def historico_estoque(id_produto):
    produto = db_session.get(Produto, id_produto)

    if not produto:
        flash("Produto não encontrado!", "danger")
        return redirect("/produtos")

    return render_template("historico_estoque.html", produto=produto)


# ============================
# MOVIMENTAR ESTOQUE
# ============================
@app.route('/estoque/<int:id_produto>/movimentar', methods=['GET', 'POST'])
@login_required
def movimentar_estoque(id_produto):
    produto = db_session.get(Produto, id_produto)

    if not produto:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("listar_produtos"))

    if request.method == "POST":
        quantidade = int(request.form["quantidade"])
        status = request.form["status"]

        # alerta de estoque insuficiente
        if status == "saida" and quantidade > produto.quantidade:
            flash(
                f"⚠️ Não é possível remover {quantidade} itens. "
                f"Estoque atual: {produto.quantidade}.",
                "warning"
            )
            return redirect(f"/estoque/{id_produto}")

        mov = Estoque(
            quantidade_movimentada=quantidade,
            status=status,
            produto=produto
        )

        mov.save()

        flash("Movimentação registrada com sucesso!", "success")
        return redirect(f"/estoque/{id_produto}")

    return render_template("movimentar_estoque.html", produto=produto)


# ============================
# INICIAR
# ============================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
