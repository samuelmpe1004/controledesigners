from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
from src.models import db
from src.models.user import User
from src.models.ficha import FichaLiberacao
from src.forms import FichaForm, RelatorioDateFilterForm

# Crie o blueprint primeiro
main_bp = Blueprint("main_bp", __name__)

# Agora defina as rotas
@main_bp.route("/")
@login_required
def index():
    fichas = FichaLiberacao.query.filter_by(user_id=current_user.id).order_by(FichaLiberacao.data_liberacao.desc()).all()
    return render_template("index.html", title="PÁGINA INICIAL", fichas=fichas, now=datetime.utcnow())

@main_bp.route("/adicionar_ficha", methods=["GET", "POST"])
@login_required
def adicionar_ficha():
    form = FichaForm()
    if form.validate_on_submit():
        ficha = FichaLiberacao(
            nome_cliente=form.nome_cliente.data,
            tipo_tecido=form.tipo_tecido.data,
            metragem_liberada=form.metragem_liberada.data,
            data_liberacao=form.data_liberacao.data,
            designer_liberou=form.designer_liberou.data,
            user_id=current_user.id
        )
        db.session.add(ficha)
        db.session.commit()
        flash(f"FICHA DE LIBERAÇÃO PARA '{form.nome_cliente.data}' ADICIONADA COM SUCESSO!", "success")
        return redirect(url_for("main_bp.index"))
    
    return render_template("adicionar_ficha.html", title="ADICIONAR FICHA", form=form, now=datetime.utcnow())

@main_bp.route("/relatorio", methods=["GET", "POST"])
@login_required
def relatorio():
    form = RelatorioDateFilterForm()
    
    fichas_filtradas = None
    total_metragem = 0
    data_inicio_filtro = None
    data_fim_filtro = None
    nome_cliente_filtro = None
    
    if form.validate_on_submit():
        data_inicio = form.data_inicio.data
        data_fim = form.data_fim.data
        nome_cliente = form.nome_cliente.data
        
        # Ajustar data_fim para incluir todo o dia
        data_fim_ajustada = datetime.combine(data_fim, datetime.max.time())
        
        # Filtrar fichas por data e usuário atual
        query = FichaLiberacao.query.filter(
            FichaLiberacao.user_id == current_user.id,
            FichaLiberacao.data_liberacao >= data_inicio,
            FichaLiberacao.data_liberacao <= data_fim_ajustada
        )
        
        # Adicionar filtro por nome de cliente se fornecido
        if nome_cliente:
            query = query.filter(FichaLiberacao.nome_cliente.ilike(f"%{nome_cliente}%"))
            nome_cliente_filtro = nome_cliente
        
        # Executar a consulta
        fichas_filtradas = query.order_by(FichaLiberacao.data_liberacao).all()
        
        # Calcular o total de metragem
        total_metragem = sum(ficha.metragem_liberada for ficha in fichas_filtradas)
        
        data_inicio_filtro = data_inicio
        data_fim_filtro = data_fim
        
        if not fichas_filtradas:
            if nome_cliente:
                flash(f"NENHUMA FICHA ENCONTRADA PARA O CLIENTE '{nome_cliente}' NO PERÍODO SELECIONADO.", "warning")
            else:
                flash(f"NENHUMA FICHA ENCONTRADA NO PERÍODO SELECIONADO.", "warning")
    
    return render_template("relatorio.html", 
                           title="RELATÓRIO", 
                           form=form, 
                           fichas=fichas_filtradas, 
                           total_metragem=total_metragem,
                           data_inicio=data_inicio_filtro,
                           data_fim=data_fim_filtro,
                           nome_cliente_filtro=nome_cliente_filtro,
                           now=datetime.utcnow())

@main_bp.route("/api/clientes")
@login_required
def api_clientes():
    # Busca todos os nomes de clientes distintos do usuário atual
    clientes = db.session.query(FichaLiberacao.nome_cliente).filter(
        FichaLiberacao.user_id == current_user.id
    ).distinct().order_by(FichaLiberacao.nome_cliente).all()
    
    # Converte a lista de tuplas para uma lista simples de strings
    lista_clientes = [cliente[0] for cliente in clientes]
    
    return jsonify(lista_clientes)

@main_bp.route("/excluir_ficha/<int:ficha_id>")
@login_required
def excluir_ficha(ficha_id):
    ficha = FichaLiberacao.query.get_or_404(ficha_id)
    
    # Verificar se a ficha pertence ao usuário atual
    if ficha.user_id != current_user.id:
        flash("VOCÊ NÃO TEM PERMISSÃO PARA EXCLUIR ESTA FICHA.", "danger")
        return redirect(url_for("main_bp.index"))
    
    # Guardar informações para a mensagem flash
    nome_cliente = ficha.nome_cliente
    
    # Excluir a ficha
    db.session.delete(ficha)
    db.session.commit()
    
    flash(f"FICHA DE LIBERAÇÃO PARA '{nome_cliente}' FOI EXCLUÍDA COM SUCESSO.", "success")
    return redirect(url_for("main_bp.index"))

# Função auxiliar para verificar permissões de administrador
def get_admin_required():
    from src.main import admin_required
    return admin_required

# Rotas administrativas
@main_bp.route("/admin_dashboard")
def admin_dashboard():
    admin_required = get_admin_required()
    
    @admin_required
    def dashboard_view():
        users = User.query.all()
        return render_template("admin_dashboard.html", title="PAINEL DO ADMINISTRADOR", users=users, now=datetime.utcnow())
    
    return dashboard_view()

@main_bp.route("/admin/block_user/<int:user_id>")
def block_user(user_id):
    admin_required = get_admin_required()
    
    @admin_required
    def block_user_view():
        user = User.query.get_or_404(user_id)
        user.is_blocked = True
        db.session.commit()
        flash(f"USUÁRIO '{user.username}' FOI BLOQUEADO COM SUCESSO.", "success")
        return redirect(url_for("main_bp.admin_dashboard"))
    
    return block_user_view()

@main_bp.route("/admin/unblock_user/<int:user_id>")
def unblock_user(user_id):
    admin_required = get_admin_required()
    
    @admin_required
    def unblock_user_view():
        user = User.query.get_or_404(user_id)
        user.is_blocked = False
        db.session.commit()
        flash(f"USUÁRIO '{user.username}' FOI DESBLOQUEADO COM SUCESSO.", "success")
        return redirect(url_for("main_bp.admin_dashboard"))
    
    return unblock_user_view()

@main_bp.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    admin_required = get_admin_required()
    
    @admin_required
    def delete_user_view():
        user = User.query.get_or_404(user_id)
        
        # Excluir todas as fichas associadas ao usuário
        FichaLiberacao.query.filter_by(user_id=user.id).delete()
        
        # Excluir o usuário
        db.session.delete(user)
        db.session.commit()
        
        flash(f"USUÁRIO '{user.username}' E TODAS AS SUAS FICHAS FORAM EXCLUÍDOS COM SUCESSO.", "success")
        return redirect(url_for("main_bp.admin_dashboard"))
    
    return delete_user_view()

@main_bp.route("/admin/reset-password/<int:user_id>")
def reset_password(user_id):
    admin_required = get_admin_required()
    
    @admin_required
    def reset_password_view():
        user = User.query.get_or_404(user_id)
        
        # Gerar token de redefinição de senha
        token = user.get_reset_token()
        
        # Em um sistema real, você enviaria um e-mail com o link
        # Aqui, apenas geramos o link e mostramos para o administrador
        reset_url = url_for("auth_bp.reset_password", token=token, _external=True)
        
        flash(f"LINK DE REDEFINIÇÃO DE SENHA PARA {user.username} GERADO COM SUCESSO!", "success")
        flash(f"URL: {reset_url}", "info")
        
        return redirect(url_for("main_bp.admin_dashboard"))
    
    return reset_password_view()