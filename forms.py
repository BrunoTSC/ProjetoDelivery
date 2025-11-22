from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DecimalField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, NumberRange
from flask_wtf.file import FileField, FileAllowed

class RestauranteForm(FlaskForm):
    nome = StringField("Nome do Restaurante", validators=[DataRequired(), Length(min=3, max=100)])
    cnpj = StringField("CNPJ", validators=[DataRequired(), Length(min=14, max=18)])
    telefone = StringField("Telefone", validators=[DataRequired(), Length(min=8, max=20)])
    endereco = StringField("Endereço", validators=[DataRequired(), Length(min=5, max=200)])
    categoria = SelectField("Categoria", choices=[
        ('', 'Selecione uma categoria'),
        ('pizza', 'Pizzaria'),
        ('hamburguer', 'Hamburgueria'),
        ('asiatica', 'Culinária Asiática'),
        ('brasileira', 'Comida Brasileira'),
        ('fastfood', 'Fast Food'),
        ('outros', 'Outros')
    ], validators=[DataRequired()])
    submit = SubmitField("Cadastrar Restaurante")

class ClientForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])
    telefone = StringField("Telefone", validators=[DataRequired(), Length(min=11, max=11)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField("Cadastrar")

class PratoForm(FlaskForm):
    nome = StringField("Nome do Prato", validators=[DataRequired(), Length(min=3, max=100)])
    descricao = TextAreaField("Descrição", validators=[Length(max=500)])
    preco = DecimalField("Preço (R$)", validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    categoria_id = SelectField("Categoria", coerce=int, validators=[DataRequired()])
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[DataRequired()])
    tempo_preparo = IntegerField("Tempo de Preparo (minutos)", validators=[NumberRange(min=1, max=180)])
    disponivel = BooleanField("Disponível para venda", default=True)
    submit = SubmitField("Cadastrar Prato")

class PedidoForm(FlaskForm):
    cliente_id = SelectField("Cliente", coerce=int, validators=[DataRequired()])
    restaurante_id = SelectField("Restaurante", coerce=int, validators=[DataRequired()])
    endereco_entrega = TextAreaField("Endereço de Entrega", validators=[DataRequired(), Length(max=300)])
    forma_pagamento = SelectField("Forma de Pagamento", choices=[
        ('', 'Selecione a forma de pagamento'),
        ('cartao', 'Cartão de Crédito/Débito'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX')
    ], validators=[DataRequired()])
    observacoes = TextAreaField("Observações", validators=[Length(max=500)])
    submit = SubmitField("Criar Pedido")

class ItemPedidoForm(FlaskForm):
    prato_id = SelectField("Prato", coerce=int, validators=[DataRequired()])
    quantidade = IntegerField("Quantidade", validators=[DataRequired(), NumberRange(min=1)], default=1)
    adicionar = SubmitField("Adicionar ao Pedido")