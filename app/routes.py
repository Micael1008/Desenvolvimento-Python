# app/routes.py
from flask import render_template, request, jsonify, Blueprint, url_for
from . import db
from .models import User, Profile, Project
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import re
import secrets
from datetime import datetime, timedelta

api_bp = Blueprint('routes', __name__)

@api_bp.route('/')
def index():
    return render_template('index.html')

@api_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'E-mail e senha são obrigatórios.'}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Formato de e-mail inválido.'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.senha, password):
        return jsonify({'message': 'Credenciais inválidas. Verifique seu e-mail e senha.'}), 401
    if not user.liberacao:
        return jsonify({'message': 'Sua conta está inativa. Entre em contato com o suporte.'}), 403
    login_user(user, remember=False)
    user_name = user.profile.nome if user.profile and user.profile.nome else user.email.split('@')[0]
    return jsonify({
        'message': 'Login bem-sucedido',
        'user': {'id': user.id, 'email': user.email, 'nome': user_name},
        'requiresPasswordChange': user.mudaSenha,
        'isAuthenticated': True
    }), 200

@api_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or len(name.strip()) < 2:
        return jsonify({'message': 'Nome completo é obrigatório e deve ter no mínimo 2 caracteres.'}), 400
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Formato de e-mail inválido.'}), 400
    if not password or len(password) < 6:
        return jsonify({'message': 'A senha é obrigatória e deve ter no mínimo 6 caracteres.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Este e-mail já está registrado'}), 409
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, senha=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    new_profile = Profile(userID=new_user.id, nome=name)
    db.session.add(new_profile)
    db.session.commit()
    login_user(new_user)
    return jsonify({
        'message': 'Conta criada com sucesso!',
        'user': {'id': new_user.id, 'email': new_user.email, 'nome': new_profile.nome},
        'isAuthenticated': True
    }), 201

@api_bp.route('/api/auth_status', methods=['GET'])
def api_auth_status():
    if current_user.is_authenticated:
        user_profile = current_user.profile
        profile_nome = user_profile.nome if user_profile and user_profile.nome else current_user.email.split('@')[0]
        return jsonify({
            'isAuthenticated': True,
            'user': {
                'id': current_user.id, 'email': current_user.email,
                'nome': profile_nome, 'contato': user_profile.contato,
                'foto': user_profile.foto, 'tipoUsuario': current_user.tipoUsuario,
                'mudaSenha': current_user.mudaSenha
            }
        }), 200
    return jsonify({'isAuthenticated': False}), 200

@api_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logout bem-sucedido'}), 200

@api_bp.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    user_profile = current_user.profile
    if request.method == 'GET':
        return jsonify(nome=user_profile.nome, contato=user_profile.contato, foto=user_profile.foto), 200
    data = request.get_json()
    if data.get('nome') is not None: user_profile.nome = data.get('nome')
    if data.get('contato') is not None: user_profile.contato = data.get('contato')
    if data.get('foto') is not None: user_profile.foto = data.get('foto')
    db.session.commit()
    return jsonify({'message': 'Perfil atualizado com sucesso'}), 200

@api_bp.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json()
    current_password, new_password = data.get('currentPassword'), data.get('newPassword')
    if not current_password or not new_password:
        return jsonify({'message': 'Todos os campos são obrigatórios.'}), 400
    if not check_password_hash(current_user.senha, current_password):
        return jsonify({'message': 'A senha atual está incorreta.'}), 401
    if len(new_password) < 6:
        return jsonify({'message': 'A nova senha deve ter no mínimo 6 caracteres.'}), 400
    current_user.senha = generate_password_hash(new_password, method='pbkdf2:sha256')
    current_user.mudaSenha = False
    db.session.commit()
    return jsonify({'message': 'Sua senha foi atualizada com sucesso!'}), 200

@api_bp.route('/api/forgot_password', methods=['POST'])
def api_forgot_password():
    email = request.get_json().get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_expiration = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        reset_link = url_for('routes.index', _external=True) + f'#reset-password-{token}'
        print(f"DEBUG: Link de redefinição para {user.email}: {reset_link}")
    return jsonify({'message': 'Se o e-mail estiver registrado, um link será enviado.'}), 200

@api_bp.route('/api/reset_password', methods=['POST'])
def api_reset_password():
    data = request.get_json()
    token, new_password, confirm_new_password = data.get('token'), data.get('newPassword'), data.get('confirmNewPassword')
    if not token or not new_password or new_password != confirm_new_password or len(new_password) < 6:
        return jsonify({'message': 'Token ou senhas inválidas.'}), 400
    user = User.query.filter_by(reset_token=token).first()
    if not user or (user.reset_expiration and user.reset_expiration < datetime.utcnow()):
        return jsonify({'message': 'O link de redefinição é inválido ou expirou.'}), 400
    user.senha = generate_password_hash(new_password, method='pbkdf2:sha256')
    user.reset_token = None
    user.reset_expiration = None
    db.session.commit()
    return jsonify({'message': 'A sua senha foi redefinida com sucesso!'}), 200

@api_bp.route('/api/projects', methods=['GET', 'POST'])
@login_required
def api_projects():
    if request.method == 'GET':
        projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
        return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'status': p.status, 'createdAt': p.created_at.isoformat()} for p in projects])
    data = request.get_json()
    name = data.get('name')
    if not name or len(name.strip()) < 3:
        return jsonify({'message': 'Nome do projeto é obrigatório.'}), 400
    new_project = Project(user_id=current_user.id, name=name, description=data.get('description'), status=data.get('status', 'A Fazer'))
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Projeto criado com sucesso!', 'project': {'id': new_project.id, 'name': new_project.name, 'description': new_project.description, 'status': new_project.status, 'createdAt': new_project.created_at.isoformat()}}), 201

@api_bp.route('/api/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_single_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'message': 'Não autorizado.'}), 403
    if request.method == 'GET':
        return jsonify({'id': project.id, 'name': project.name, 'description': project.description, 'status': project.status, 'createdAt': project.created_at.isoformat()})
    elif request.method == 'PUT':
        data = request.get_json()
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.status = data.get('status', project.status)
        db.session.commit()
        return jsonify({'message': 'Projeto atualizado com sucesso!'})
    elif request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projeto excluído com sucesso!'})