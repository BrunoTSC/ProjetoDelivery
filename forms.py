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
    # imagem = FileField("Imagem do Prato", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens!')])
    submit = SubmitField("Cadastrar Prato")