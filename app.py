from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from config import get_db_connection
from forms import ClientForm, RestauranteForm


app = Flask(__name__)
app.secret_key = "chave_secreta_segura"  # Necessário para Flask-WTF


@app.route("/cadastro-restaurante", methods=["GET", "POST"])
def cadastro_restaurante():
    form = RestauranteForm()
    if form.validate_on_submit():
        nome = form.nome.data
        cnpj = form.cnpj.data
        telefone = form.telefone.data
        endereco = form.endereco.data
        categoria = form.categoria.data

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO restaurantes (nome, cnpj, telefone, endereco, categoria) VALUES (%s, %s, %s, %s, %s)",
                (nome, cnpj, telefone, endereco, categoria)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Restaurante cadastrado com sucesso!", "success")
            return redirect(url_for("lista_restaurantes"))
        except Exception as e:
            flash(f"Erro ao cadastrar restaurante: {e}", "danger")
    
    return render_template("cadastro_restaurante.html", form=form)

@app.route("/restaurantes")
def lista_restaurantes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurantes ORDER BY data_cadastro DESC")
        restaurantes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("restaurantes.html", restaurantes=restaurantes)
    except Exception as e:
        flash(f"Erro ao carregar restaurantes: {e}", "danger")
        return render_template("restaurantes.html", restaurantes=[])
    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = ClientForm()
    if form.validate_on_submit():
        nome = form.nome.data
        telefone = form.telefone.data
        email = form.email.data

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s)",
                           (nome, telefone, email))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("sucesso"))
        except Exception as e:
            flash(f"Erro ao cadastrar: {e}", "danger")
    return render_template("cadastro.html", form=form)

@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

if __name__ == "__main__":
    app.run(debug=True)
