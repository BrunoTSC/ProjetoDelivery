from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from config import get_db_connection
from forms import ClientForm, RestauranteForm, PratoForm, PedidoForm, ItemPedidoForm
from decimal import Decimal


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
    
@app.route("/novo-pedido", methods=["GET", "POST"])
def novo_pedido():
    # Carregar clientes e restaurantes para os selects
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT id, nome FROM restaurantes ORDER BY nome")
    restaurantes = cursor.fetchall()
    
    cursor.close()
    conn.close()

    form = PedidoForm()
    form.cliente_id.choices = [(0, 'Selecione um cliente')] + [(c['id'], c['nome']) for c in clientes]
    form.restaurante_id.choices = [(0, 'Selecione um restaurante')] + [(r['id'], r['nome']) for r in restaurantes]

    if form.validate_on_submit():
        # Iniciar um novo pedido na sessão
        session['pedido_temp'] = {
            'cliente_id': form.cliente_id.data,
            'restaurante_id': form.restaurante_id.data,
            'endereco_entrega': form.endereco_entrega.data,
            'forma_pagamento': form.forma_pagamento.data,
            'observacoes': form.observacoes.data,
            'itens': []
        }
        return redirect(url_for('adicionar_itens_pedido'))
    
    return render_template("novo_pedido.html", form=form, clientes=clientes, restaurantes=restaurantes)

@app.route("/adicionar-itens-pedido", methods=["GET", "POST"])
def adicionar_itens_pedido():
    if 'pedido_temp' not in session:
        return redirect(url_for('novo_pedido'))
    
    restaurante_id = session['pedido_temp']['restaurante_id']
    
    # Carregar pratos do restaurante selecionado
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nome, preco, disponivel 
        FROM pratos 
        WHERE restaurante_id = %s AND disponivel = TRUE 
        ORDER BY nome
    """, (restaurante_id,))
    pratos = cursor.fetchall()
    cursor.close()
    conn.close()

    form = ItemPedidoForm()
    form.prato_id.choices = [(0, 'Selecione um prato')] + [(p['id'], f"{p['nome']} - R$ {p['preco']:.2f}") for p in pratos]

    if form.validate_on_submit() and form.adicionar.data:
        prato_id = form.prato_id.data
        quantidade = form.quantidade.data
        
        # Buscar informações do prato
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, preco FROM pratos WHERE id = %s", (prato_id,))
        prato = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if prato:
            item = {
                'prato_id': prato_id,
                'prato_nome': prato['nome'],
                'preco_unitario': float(prato['preco']),
                'quantidade': quantidade,
                'subtotal': float(prato['preco']) * quantidade
            }
            session['pedido_temp']['itens'].append(item)
            session.modified = True
            flash("Item adicionado ao pedido!", "success")
        
        return redirect(url_for('adicionar_itens_pedido'))

    return render_template("adicionar_itens_pedido.html", form=form, pratos=pratos)

@app.route("/finalizar-pedido", methods=["POST"])
def finalizar_pedido():
    if 'pedido_temp' not in session or not session['pedido_temp']['itens']:
        flash("Adicione itens ao pedido antes de finalizar!", "warning")
        return redirect(url_for('adicionar_itens_pedido'))
    
    pedido_temp = session['pedido_temp']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calcular valor total
        valor_total = sum(item['subtotal'] for item in pedido_temp['itens'])
        
        # Inserir pedido
        cursor.execute("""
            INSERT INTO pedidos (cliente_id, restaurante_id, endereco_entrega, forma_pagamento, observacoes, valor_total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            pedido_temp['cliente_id'],
            pedido_temp['restaurante_id'],
            pedido_temp['endereco_entrega'],
            pedido_temp['forma_pagamento'],
            pedido_temp['observacoes'],
            valor_total
        ))
        
        pedido_id = cursor.lastrowid
        
        # Inserir itens do pedido
        for item in pedido_temp['itens']:
            cursor.execute("""
                INSERT INTO itens_pedido (pedido_id, prato_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, item['prato_id'], item['quantidade'], item['preco_unitario'], item['subtotal']))
        
        # Registrar status inicial
        cursor.execute("""
            INSERT INTO historico_status (pedido_id, status, observacao)
            VALUES (%s, 'pendente', 'Pedido criado')
        """, (pedido_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Limpar sessão
        session.pop('pedido_temp', None)
        
        flash(f"Pedido #{pedido_id} criado com sucesso! Valor total: R$ {valor_total:.2f}", "success")
        return redirect(url_for('detalhes_pedido', pedido_id=pedido_id))
        
    except Exception as e:
        flash(f"Erro ao finalizar pedido: {e}", "danger")
        return redirect(url_for('adicionar_itens_pedido'))

@app.route("/pedidos")
def lista_pedidos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.nome as cliente_nome, r.nome as restaurante_nome,
                   (SELECT COUNT(*) FROM itens_pedido ip WHERE ip.pedido_id = p.id) as total_itens
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN restaurantes r ON p.restaurante_id = r.id
            ORDER BY p.data_pedido DESC
        """)
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("pedidos.html", pedidos=pedidos)
    except Exception as e:
        flash(f"Erro ao carregar pedidos: {e}", "danger")
        return render_template("pedidos.html", pedidos=[])

@app.route("/pedido/<int:pedido_id>")
def detalhes_pedido(pedido_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar informações do pedido
        cursor.execute("""
            SELECT p.*, c.nome as cliente_nome, c.telefone as cliente_telefone,
                   r.nome as restaurante_nome, r.telefone as restaurante_telefone
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN restaurantes r ON p.restaurante_id = r.id
            WHERE p.id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        # Buscar itens do pedido
        cursor.execute("""
            SELECT ip.*, pr.nome as prato_nome
            FROM itens_pedido ip
            LEFT JOIN pratos pr ON ip.prato_id = pr.id
            WHERE ip.pedido_id = %s
        """, (pedido_id,))
        itens = cursor.fetchall()
        
        # Buscar histórico de status
        cursor.execute("""
            SELECT * FROM historico_status 
            WHERE pedido_id = %s 
            ORDER BY data_status DESC
        """, (pedido_id,))
        historico = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("detalhes_pedido.html", pedido=pedido, itens=itens, historico=historico)
    except Exception as e:
        flash(f"Erro ao carregar pedido: {e}", "danger")
        return redirect(url_for('lista_pedidos'))

@app.route("/atualizar-status/<int:pedido_id>", methods=["POST"])
def atualizar_status_pedido(pedido_id):
    novo_status = request.form.get('status')
    observacao = request.form.get('observacao', '')
    
    if novo_status:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Atualizar status do pedido
            cursor.execute("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, pedido_id))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_status (pedido_id, status, observacao)
                VALUES (%s, %s, %s)
            """, (pedido_id, novo_status, observacao))
            
            # Se for entregue, registrar data de entrega
            if novo_status == 'entregue':
                cursor.execute("UPDATE pedidos SET data_entrega = NOW() WHERE id = %s", (pedido_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f"Status do pedido #{pedido_id} atualizado para {novo_status}!", "success")
        except Exception as e:
            flash(f"Erro ao atualizar status: {e}", "danger")
    
    return redirect(url_for('detalhes_pedido', pedido_id=pedido_id))


if __name__ == "__main__":
    app.run(debug=True)
