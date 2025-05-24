from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, DateField 
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, NumberRange, Optional, Regexp
from wtforms.utils import unset_value
from src.models.user import User

# INÍCIO: Nova classe de campo para aceitar vírgula como separador decimal
class CommaAcceptingFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                # Substitui vírgula por ponto ANTES de tentar converter para float
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Não é um valor decimal válido."))
        else:
            self.data = None

class LoginForm(FlaskForm):
    username = StringField("NOME DE USUÁRIO", validators=[DataRequired(), Length(max=100)])
    password = PasswordField("SENHA", validators=[DataRequired()])
    submit = SubmitField("ENTRAR")

class RegistrationForm(FlaskForm):
    username = StringField("NOME DE USUÁRIO", validators=[DataRequired(), Length(max=100)])
    nome_completo = StringField("NOME COMPLETO", validators=[DataRequired(), Length(max=200)])
    cpf = StringField("CPF", validators=[
        DataRequired(), 
        Length(min=11, max=11, message="O CPF deve ter exatamente 11 dígitos."),
        Regexp('^[0-9]*$', message="O CPF deve conter apenas números.")
    ])
    data_nascimento = DateField("DATA DE NASCIMENTO", format="%Y-%m-%d", validators=[DataRequired()])
    apelido = StringField("COMO QUER SER CHAMADO?", validators=[Optional(), Length(max=100)])
    password = PasswordField("SENHA", validators=[DataRequired(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    confirm_password = PasswordField("CONFIRMAR SENHA", validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    aceitar_termos = BooleanField("LI E CONCORDO COM OS TERMOS", validators=[DataRequired(message="Você deve aceitar os termos para se registrar.")])
    submit = SubmitField("REGISTRAR")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.upper()).first()
        if user:
            raise ValidationError("Este nome de usuário já está em uso. Por favor, escolha outro.")

class FichaForm(FlaskForm):
    nome_cliente = StringField("NOME DO CLIENTE", validators=[DataRequired(), Length(max=200)])
    tipo_tecido = StringField("TIPO DE TECIDO", validators=[DataRequired(), Length(max=100)])
    # ALTERADO: Usando CommaAcceptingFloatField para metragem_liberada
    metragem_liberada = CommaAcceptingFloatField(
        "METRAGEM LIBERADA (METROS)", 
        validators=[
            DataRequired(message="Este campo é obrigatório."), 
            NumberRange(min=0.01, message="A metragem deve ser maior que zero.")
        ]
    )
    data_liberacao = DateField("DATA DE LIBERAÇÃO", format="%Y-%m-%d", validators=[DataRequired()])
    designer_liberou = StringField("DESIGNER QUE LIBEROU", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("SALVAR FICHA")

class RelatorioDateFilterForm(FlaskForm):
    data_inicio = DateField("DATA INÍCIO", format="%Y-%m-%d", validators=[DataRequired()])
    data_fim = DateField("DATA FIM", format="%Y-%m-%d", validators=[DataRequired()])
    nome_cliente = StringField("NOME DO CLIENTE", validators=[Optional()])
    submit = SubmitField("FILTRAR")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("NOVA SENHA", validators=[DataRequired(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    confirm_password = PasswordField("CONFIRMAR NOVA SENHA", validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    submit = SubmitField("REDEFINIR SENHA")