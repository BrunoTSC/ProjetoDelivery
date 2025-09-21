from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "chave_secreta_segura"  # Necessário para Flask-WTF

# Formulário com validações
class ClienteForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])
    telefone = StringField("Telefone", validators=[DataRequired(), Length(min=11, max=11)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField("Cadastrar")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = ClienteForm()
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
