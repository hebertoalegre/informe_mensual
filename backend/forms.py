from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired

class RegistrationForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=60)])
    no_contrato = StringField('Número de contrato', validators=[DataRequired(), Length(min=2, max=16)])
    no_acuerdo = StringField('Acuerdo Ministerial', validators=[DataRequired(), Length(min=2, max=9)])
    email = StringField('Correo electrónico', validators = [DataRequired(), Email()])
    dpi = StringField('dpi', validators=[DataRequired(),Length(min=2, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators = [DataRequired(), Email()])
    password = PasswordField('Contraseña', validators = [DataRequired()])
    remember = BooleanField('Recuerdame')
    submit = SubmitField('Entrar')

class ActividadForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=60)])
    no_contrato = StringField('Número de contrato', validators=[DataRequired(), Length(min=2, max=16)])
    no_acuerdo = StringField('Acuerdo Ministerial', validators=[DataRequired(), Length(min=2, max=9)])
    actividad_contrato = StringField('Actividad Contrato', validators=[DataRequired(), Length(min=100, max=300)])
    actividad_especifica = StringField('Actividad Especifica', validators=[DataRequired(), Length(min=100, max=500)])

class ContratoForm(FlaskForm):
    usuario = SelectField(u'Usuario', coerce=int)
    actividad_contrato = TextAreaField('Actividad Contrato', validators=[DataRequired(), Length(min=100, max=300)])
    actividad_resuelta = TextAreaField('Actividad Resumida', validators=[DataRequired(), Length(min=10, max=30)])
    submit = SubmitField('Agregar')
