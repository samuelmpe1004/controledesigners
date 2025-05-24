from flask import Blueprint, jsonify, request
from src.models.user import User, db
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
from functools import wraps

user_bp = Blueprint('user', __name__)

# Decorator para verificar permissões de administrador
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"error": "ACESSO NEGADO. PERMISSÃO DE ADMINISTRADOR NECESSÁRIA."}), 403
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    
    # Verificar se o usuário já existe
    existing_user = User.query.filter_by(username=data['username'].upper()).first()
    if existing_user:
        return jsonify({"error": "NOME DE USUÁRIO JÁ EXISTE"}), 400
    
    # Criar novo usuário
    user = User(
        username=data['username'].upper(),
        nome_completo=data.get('nome_completo', ''),
        cpf=data.get('cpf', ''),
        data_nascimento=data.get('data_nascimento'),
        apelido=data.get('apelido', ''),
        aceitou_termos=True
    )
    
    # Definir senha
    if 'password' in data:
        user.set_password(data['password'])
    else:
        return jsonify({"error": "SENHA É OBRIGATÓRIA"}), 400
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Atualizar campos do usuário
    if 'username' in data:
        # Verificar se o novo username já existe (exceto para o próprio usuário)
        existing_user = User.query.filter_by(username=data['username'].upper()).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error": "NOME DE USUÁRIO JÁ EXISTE"}), 400
        user.username = data['username'].upper()
    
    if 'nome_completo' in data:
        user.nome_completo = data['nome_completo']
    
    if 'cpf' in data:
        user.cpf = data['cpf']
    
    if 'data_nascimento' in data:
        user.data_nascimento = data['data_nascimento']
    
    if 'apelido' in data:
        user.apelido = data['apelido']
    
    if 'is_blocked' in data:
        user.is_blocked = data['is_blocked']
    
    # Atualizar senha se fornecida
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # Gerar token de redefinição de senha
    token = user.get_reset_token()
    
    # Em um sistema real, você enviaria um e-mail com o link
    # Aqui, apenas retornamos o token
    reset_url = request.host_url.rstrip('/') + '/auth/reset-password/' + token
    
    return jsonify({
        "message": f"LINK DE REDEFINIÇÃO DE SENHA PARA {user.username} GERADO COM SUCESSO!",
        "reset_url": reset_url
    })