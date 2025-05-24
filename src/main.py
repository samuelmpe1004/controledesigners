from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timezone
from functools import wraps
import os
import sys

# Configuração do App
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "uma-chave-secreta-muito-forte-padrao")

# Configuração do Banco de Dados
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../banco.db" # Assume banco.db na raiz do projeto

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicialização do SQLAlchemy
from src.models import db, init_db
init_db(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_bp.login"

# Decorator para rotas de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("ACESSO NEGADO. FAÇA LOGIN COMO ADMINISTRADOR.", "danger")
            return redirect(url_for("auth_bp.admin_login"))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    from src.models.user import User
    return db.session.get(User, int(user_id)) # CORRIGIDO: Usando db.session.get()

# Importações dos modelos
from src.models.user import User
from src.models.ficha import FichaLiberacao

# Importações dos blueprints - após definir os modelos e funções auxiliares
from src.routes.auth import auth_bp
from src.routes.main import main_bp
from src.routes.user import user_bp  # Nova importação para o blueprint de usuários

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(user_bp, url_prefix='/api')  # Registrando o blueprint de usuários com prefixo /api

# Contexto para templates
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)} # CORRIGIDO: Usando datetime.now(timezone.utc)

# Criar todas as tabelas do banco de dados
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)