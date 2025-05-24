from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db
from datetime import datetime
from time import time
import jwt
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    
    # Novos campos para registro detalhado
    nome_completo = db.Column(db.String(120), nullable=True)
    cpf = db.Column(db.String(14), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    apelido = db.Column(db.String(50), nullable=True)
    aceitou_termos = db.Column(db.Boolean, nullable=False, default=False)
    data_aceite_termos = db.Column(db.DateTime, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    fichas = db.relationship('FichaLiberacao', backref='designer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_in=600):
        # Token expira em 10 minutos (600 segundos)
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )["reset_password"]
        except:
            return None
        return User.query.get(id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'apelido': self.apelido,
            'is_blocked': self.is_blocked,
            'aceitou_termos': self.aceitou_termos,
            'data_aceite_termos': self.data_aceite_termos.isoformat() if self.data_aceite_termos else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

    def __repr__(self):
        return f'<User {self.username}>'