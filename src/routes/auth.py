from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.forms import LoginForm, RegistrationForm, ResetPasswordForm
from src.models.user import User
from src.models import db
from datetime import datetime

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.index"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.aceitar_termos.data:
            flash("VOCÊ PRECISA ACEITAR OS TERMOS PARA SE REGISTRAR.", "danger")
            return render_template("register.html", title="REGISTRAR", form=form)
        
        user = User(
            username=form.username.data.upper(),
            nome_completo=form.nome_completo.data,
            cpf=form.cpf.data,
            data_nascimento=form.data_nascimento.data,
            apelido=form.apelido.data,
            aceitou_termos=True,
            data_aceite_termos=datetime.utcnow()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash("SEU REGISTRO FOI BEM-SUCEDIDO! AGORA VOCÊ PODE FAZER LOGIN.", "success")
        return redirect(url_for("auth_bp.login"))
    
    return render_template("register.html", title="REGISTRAR", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.upper()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash("NOME DE USUÁRIO OU SENHA INVÁLIDOS", "danger")
            return redirect(url_for("auth_bp.login"))
        
        if user.is_blocked:
            flash("SUA CONTA ESTÁ BLOQUEADA. ENTRE EM CONTATO COM O ADMINISTRADOR.", "danger")
            return redirect(url_for("auth_bp.login"))
        
        login_user(user)
        return redirect(url_for("main_bp.index"))
    
    return render_template("login.html", title="LOGIN", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()  # Usando o mesmo formulário LoginForm
    if form.validate_on_submit():
        # Credenciais atualizadas para o administrador
        if form.username.data.upper() == "PARDOMPE@GMAIL.COM" and form.password.data == "PARDOGORDO1995@@":
            session["admin_logged_in"] = True
            flash("LOGIN DE ADMINISTRADOR BEM-SUCEDIDO!", "success")
            return redirect(url_for("main_bp.admin_dashboard"))
        else:
            flash("CREDENCIAIS DE ADMINISTRADOR INVÁLIDAS", "danger")
            return redirect(url_for("auth_bp.admin_login"))
    
    return render_template("admin_login.html", title="LOGIN DO ADMINISTRADOR", form=form)

@auth_bp.route("/admin_logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("LOGOUT DE ADMINISTRADOR BEM-SUCEDIDO!", "success")
    return redirect(url_for("auth_bp.admin_login"))

@auth_bp.route("/termos")
def termos():
    return render_template("termos.html", title="TERMOS DE USO")

@auth_bp.route("/forgot-password")
def forgot_password():
    # Esta rota apenas exibe a mensagem para contatar o administrador
    # O modal já está implementado no template login.html
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Verificar se o token é válido
    user = User.verify_reset_token(token)
    if not user:
        flash("O LINK DE REDEFINIÇÃO DE SENHA É INVÁLIDO OU EXPIROU.", "danger")
        return redirect(url_for("auth_bp.login"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("SUA SENHA FOI REDEFINIDA COM SUCESSO! AGORA VOCÊ PODE FAZER LOGIN.", "success")
        return redirect(url_for("auth_bp.login"))
    
    return render_template("reset_password.html", title="REDEFINIR SENHA", form=form)