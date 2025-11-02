from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from config import get_db_connection
from forms import ClientForm, RestauranteForm, PratoForm


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

@app.route("/cadastro-prato", methods=["GET", "POST"])
def cadastro_prato():
    # Carregar restaurantes e categorias para os selects
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nome FROM restaurantes ORDER BY nome")
    restaurantes = cursor.fetchall()
    
    cursor.execute("SELECT id, nome FROM categorias_pratos ORDER BY nome")
    categorias = cursor.fetchall()
    
    cursor.close()
    conn.close()

    form = PratoForm()
    
    # Popular os selects
    form.restaurante_id.choices = [(0, 'Selecione um restaurante')] + [(r['id'], r['nome']) for r in restaurantes]
    form.categoria_id.choices = [(0, 'Selecione uma categoria')] + [(c['id'], c['nome']) for c in categorias]
    
    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        preco = float(form.preco.data)
        categoria_id = form.categoria_id.data
        restaurante_id = form.restaurante_id.data
        tempo_preparo = form.tempo_preparo.data
        disponivel = form.disponivel.data

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO pratos (nome, descricao, preco, categoria_id, restaurante_id, tempo_preparo, disponivel) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (nome, descricao, preco, categoria_id, restaurante_id, tempo_preparo, disponivel)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Prato cadastrado com sucesso!", "success")
            return redirect(url_for("lista_pratos"))
        except Exception as e:
            flash(f"Erro ao cadastrar prato: {e}", "danger")
    
    return render_template("cadastro_prato.html", form=form, restaurantes=restaurantes, categorias=categorias)

@app.route("/pratos")
def lista_pratos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, r.nome as restaurante_nome, c.nome as categoria_nome 
            FROM pratos p 
            LEFT JOIN restaurantes r ON p.restaurante_id = r.id 
            LEFT JOIN categorias_pratos c ON p.categoria_id = c.id 
            ORDER BY p.data_cadastro DESC
        """)
        pratos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("pratos.html", pratos=pratos)
    except Exception as e:
        flash(f"Erro ao carregar pratos: {e}", "danger")
        return render_template("pratos.html", pratos=[])

@app.route("/cardapio/<int:restaurante_id>")
def cardapio_restaurante(restaurante_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar informações do restaurante
        cursor.execute("SELECT * FROM restaurantes WHERE id = %s", (restaurante_id,))
        restaurante = cursor.fetchone()
        
        # Buscar pratos do restaurante
        cursor.execute("""
            SELECT p.*, c.nome as categoria_nome 
            FROM pratos p 
            LEFT JOIN categorias_pratos c ON p.categoria_id = c.id 
            WHERE p.restaurante_id = %s AND p.disponivel = TRUE 
            ORDER BY c.nome, p.nome
        """, (restaurante_id,))
        pratos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("cardapio.html", restaurante=restaurante, pratos=pratos)
    except Exception as e:
        flash(f"Erro ao carregar cardápio: {e}", "danger")
        return redirect(url_for("lista_restaurantes"))

if __name__ == "__main__":
    app.run(debug=True)
