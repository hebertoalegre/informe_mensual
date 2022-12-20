from flask import Flask
from flask_login import UserMixin, current_user, login_manager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__, template_folder=os.path.abspath('templates'))

bcrypt  = Bcrypt(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] =SECRET_KEY
csrf= CSRFProtect(app)


login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_BINDS'] ={
    'actividades':'sqlite:///actividades.db', 
    'registro': 'sqlite:///registro.db'
}

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(60), unique=True, nullable=False)
    no_contrato =db.Column(db.String(16), unique=True, nullable=False)
    no_acuerdo =db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dpi= db.Column(db.String(30), unique=True, nullable=False)
    password=db.Column(db.String(60), nullable=False)

class User_Act(db.Model):
    __bind_key__  = 'actividades'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(60), unique=False, nullable=False)
    no_contrato =db.Column(db.String(16), unique=False, nullable=False)
    no_acuerdo =db.Column(db.String(9), unique=False, nullable=False)
    actividad_contrato =db.Column(db.String(300), nullable=False)
    actividad_especifica =db.Column(db.String(500), nullable=False)
    ano =db.Column(db.String(4), nullable=False)
    mes =db.Column(db.String(25), nullable=False)
    date= db.Column(db.DateTime, nullable=False)

class User_Con_Act(db.Model):
    __bind_key__  = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(60), unique=False, nullable=False)
    actividad_contrato =db.Column(db.String(300), nullable=False)
    actividad_resuelta =db.Column(db.String(500), nullable=False)
  

