from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email

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