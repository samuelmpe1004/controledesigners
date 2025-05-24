from src.models import db
from datetime import datetime

class FichaLiberacao(db.Model):
    __tablename__ = 'fichas_liberacao'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(200), nullable=False)
    tipo_tecido = db.Column(db.String(100), nullable=False)
    metragem_liberada = db.Column(db.Float, nullable=False)
    data_liberacao = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Mantém quem registrou no sistema
    
    # INÍCIO: Coluna Adicionada - Designer que Liberou (Item 3 da sua lista)
    designer_liberou = db.Column(db.String(100), nullable=False) # Armazena o nome do designer que liberou
    # FIM: Coluna Adicionada - Designer que Liberou
    
    # Adicionando campo data_criacao para rastreamento
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FichaLiberacao {self.id} - Cliente: {self.nome_cliente}>'