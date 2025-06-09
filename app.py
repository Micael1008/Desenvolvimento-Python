# app.py
# Backend REST API para o Gestor de Projetos (SPA Frontend)

from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import secrets
from datetime import datetime, timedelta
import re # Importar módulo de expressões regulares para validação de email e contato

# Configurações do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui' # Mude isso em produção!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestorprojetos.db' # Nome do banco de dados alterado
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' # Redireciona para a página inicial da SPA se não logado para API

# --- Modelos do Banco de Dados ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # email varchar(50)
    email = db.Column(db.String(50), unique=True, nullable=False)
    # senha varchar(30) (usaremos varchar(255) para o hash)
    senha = db.Column(db.String(255), nullable=False)
    # tipoUsuario booleano user 0 / 1 admin
    tipoUsuario = db.Column(db.Boolean, default=False) # False=user, True=admin
    # mudaSenha booleano nao mudar 0 / 1 mudar
    mudaSenha = db.Column(db.Boolean, default=False)
    # liberacao booleano inativo 0 / 1 ativo
    liberacao = db.Column(db.Boolean, default=True)

    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_expiration = db.Column(db.DateTime, nullable=True)

    profile = db.relationship('Profile', backref='user', uselist=False)
    projects = db.relationship('Project', backref='owner', lazy=True) # Renomeado 'author' para 'owner' para consistência

    def __repr__(self):
        return f"<User {self.email}>"

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # nome varchar(50) nome completo
    nome = db.Column(db.String(50), nullable=True)
    # contato varchar(11) Area 2 digitos, telefone 9 digitos
    contato = db.Column(db.String(11), nullable=True) # <-- Coluna definida como 'contato'
    # foto varchar() caminho para imagem salva no dispositivo (usaremos o nome do arquivo)
    foto = db.Column(db.String(255), nullable=True, default='default.jpg')

    def __repr__(self):
        return f"<Profile {self.nome}>"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # Renomeado 'title' para 'name' para consistência com o frontend JS
    description = db.Column(db.Text, nullable=True) # Alterado para True para permitir vazio
    status = db.Column(db.String(20), default='A Fazer', nullable=False) # Status padrão 'A Fazer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Ajustado para datetime.utcnow

    def __repr__(self):
        return f"<Project {self.name}>"

# --- Funções do Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Rotas da API ---

# Rota para servir o ficheiro HTML principal da SPA
@app.route('/')
def index():
    return app.send_static_file('index.html') # Serve o ficheiro index.html da pasta 'static'

# Endpoint de Login
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validação de entrada: E-mail e senha não podem ser vazios, e formato de e-mail válido
    if not email or not password:
        return jsonify({'message': 'E-mail e senha são obrigatórios.'}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Formato de e-mail inválido.'}), 400

    user = User.query.filter_by(email=email).first()

    # Validação de credenciais: Utilizador existe e senha está correta
    if not user or not check_password_hash(user.senha, password):
        return jsonify({'message': 'Credenciais inválidas. Verifique seu e-mail e senha.'}), 401
    
    # Validação de estado da conta: Utilizador ativo
    if not user.liberacao:
        return jsonify({'message': 'Sua conta está inativa. Entre em contato com o suporte.'}), 403

    login_user(user) # Faz o login do utilizador via Flask-Login
    
    # Obter o nome do utilizador do perfil, com um fallback seguro
    user_name = user.profile.nome if user.profile and user.profile.nome else user.email.split('@')[0] if user.email else 'Utilizador'

    # Se a senha precisa ser alterada, o frontend será notificado
    if user.mudaSenha:
        return jsonify({
            'message': 'Login bem-sucedido. Sua senha precisa ser alterada.',
            'user': {'id': user.id, 'email': user.email, 'nome': user_name},
            'requiresPasswordChange': True
        }), 200

    return jsonify({
        'message': 'Login bem-sucedido',
        'user': {'id': user.id, 'email': user.email, 'nome': user_name}, # Retorna dados básicos do utilizador
        'isAuthenticated': True
    }), 200

# Endpoint de Registro
@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validação de entrada para o registo
    if not name or len(name.strip()) < 2:
        return jsonify({'message': 'Nome completo é obrigatório e deve ter no mínimo 2 caracteres.'}), 400
    if not email:
        return jsonify({'message': 'E-mail é obrigatório.'}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Formato de e-mail inválido.'}), 400
    if not password or len(password) < 6:
        return jsonify({'message': 'A senha é obrigatória e deve ter no mínimo 6 caracteres.'}), 400
    # Validação de complexidade de senha (exemplo, pode ser expandido com mais regras)
    # if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$", password):
    #     return jsonify({'message': 'Senha deve ter no mínimo 6 caracteres, com letra maiúscula, minúscula, número e caractere especial.'}), 400


    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Este e-mail já está registrado'}), 409 # Conflict

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(email=email, senha=hashed_password, tipoUsuario=False, mudaSenha=False, liberacao=True)
    db.session.add(new_user)
    db.session.commit()

    new_profile = Profile(userID=new_user.id, nome=name, contato=None)
    db.session.add(new_profile)
    db.session.commit()

    login_user(new_user) # Opcional: logar o utilizador automaticamente após o registo

    return jsonify({
        'message': 'Conta criada com sucesso!',
        'user': {'id': new_user.id, 'email': new_user.email, 'nome': new_profile.nome},
        'isAuthenticated': True
    }), 201 # Created

# Endpoint para verificar o estado de autenticação (usado na inicialização do SPA)
@app.route('/api/auth_status', methods=['GET'])
def api_auth_status():
    if current_user.is_authenticated:
        user_profile = Profile.query.filter_by(userID=current_user.id).first()
        # Fallback seguro para user_profile.nome e contato
        profile_nome = user_profile.nome if user_profile and user_profile.nome else current_user.email.split('@')[0] if current_user.email else 'Utilizador'
        profile_contato = user_profile.contato if user_profile and user_profile.contato else None
        profile_foto = user_profile.foto if user_profile and user_profile.foto else 'default.jpg'

        return jsonify({
            'isAuthenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'nome': profile_nome,
                'contato': profile_contato,
                'foto': profile_foto,
                'tipoUsuario': current_user.tipoUsuario,
                'mudaSenha': current_user.mudaSenha
            }
        }), 200
    return jsonify({'isAuthenticated': False}), 200

# Endpoint de Logout
@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logout bem-sucedido'}), 200

# Endpoint para Perfil do Utilizador (GET e PUT para atualização)
@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    user_profile = Profile.query.filter_by(userID=current_user.id).first()
    if not user_profile:
        # Se o perfil não existir, cria um vazio para evitar erros
        user_profile = Profile(userID=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'GET':
        return jsonify({
            'id': user_profile.id,
            'userID': user_profile.userID,
            'nome': user_profile.nome,
            'contato': user_profile.contato,
            'foto': user_profile.foto,
            'email': current_user.email,
            'tipoUsuario': current_user.tipoUsuario,
            'mudaSenha': current_user.mudaSenha
        }), 200

    elif request.method == 'PUT':
        data = request.get_json()
        new_name = data.get('nome')
        new_contact = data.get('contato')
        new_photo = data.get('foto')

        # Validação de entrada para o perfil
        if new_name is not None and len(new_name.strip()) < 2:
            return jsonify({'message': 'Nome completo deve ter no mínimo 2 caracteres.'}), 400
        if new_contact is not None and not re.match(r"^\d{11}$", new_contact):
            return jsonify({'message': 'Formato de contato inválido. Use 11 dígitos numéricos.'}), 400
        # Adicionar validação para URL da foto se necessário (ex: começar com http/https)

        if new_name is not None:
            user_profile.nome = new_name
        if new_contact is not None:
            user_profile.contato = new_contact
        if new_photo is not None: # Apenas atualiza se um valor for fornecido (mock URL)
            user_profile.foto = new_photo
        
        db.session.commit()
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200

# Endpoint para Alterar Senha (chamado do Perfil ou Mudança Forçada)
@app.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json()
    current_password = data.get('currentPassword') # Senha atual adicionada para validação
    new_password = data.get('newPassword')
    confirm_new_password = data.get('confirmNewPassword')

    # Validação de entrada: Todos os campos são obrigatórios
    if not current_password or not new_password or not confirm_new_password:
        return jsonify({'message': 'Ambos os campos de senha são obrigatórios.'}), 400

    # Validação: Verifica se a senha atual está correta
    if not check_password_hash(current_user.senha, current_password):
        return jsonify({'message': 'A senha atual está incorreta.'}), 401 # Unauthorized

    # Validação: Nova senha e confirmação devem ser iguais
    if new_password != confirm_new_password:
        return jsonify({'message': 'As novas senhas não coincidem.'}), 400

    # Validação: Comprimento mínimo da nova senha
    if len(new_password) < 6:
        return jsonify({'message': 'A nova senha deve ter no mínimo 6 caracteres.'}), 400
    
    # Se todas as validações passarem, atualiza a senha
    current_user.senha = generate_password_hash(new_password, method='pbkdf2:sha256')
    current_user.mudaSenha = False # Desativa a flag após a mudança
    db.session.commit()

    return jsonify({'message': 'Sua senha foi atualizada com sucesso!'}), 200

# Endpoint para Solicitar Redefinição de Senha (Forgot Password)
@app.route('/api/forgot_password', methods=['POST'])
def api_forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Validação: E-mail não pode ser vazio e deve ter formato válido
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Por favor, insira um e-mail válido.'}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_expiration = datetime.utcnow() + timedelta(hours=1) # Token válido por 1 hora
        db.session.commit()
        
        reset_link = url_for('index', _external=True) + f'#reset-password-{token}'
        print(f"DEBUG: Link de redefinição para {user.email}: {reset_link}")
        return jsonify({'message': f'Um link para redefinir a sua senha foi enviado para {user.email}. (Verifique a consola para o link de depuração)'}), 200
    else:
        # Mensagem genérica para segurança (não revela se o e-mail existe)
        return jsonify({'message': 'Se o e-mail estiver registrado, um link de redefinição será enviado.'}), 200

# Endpoint para Redefinir Senha com Token
@app.route('/api/reset_password', methods=['POST'])
def api_reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('newPassword')
    confirm_new_password = data.get('confirmNewPassword')

    # Validação: Token, nova senha e confirmação são obrigatórios
    if not token:
        return jsonify({'message': 'Token de redefinição inválido.'}), 400
    if not new_password or not confirm_new_password:
        return jsonify({'message': 'Ambos os campos de senha são obrigatórios.'}), 400
    
    # Validação: Nova senha e confirmação devem ser iguais
    if new_password != confirm_new_password:
        return jsonify({'message': 'As novas senhas não coincidem.'}), 400
    
    # Validação: Comprimento mínimo da nova senha
    if len(new_password) < 6:
        return jsonify({'message': 'A nova senha deve ter no mínimo 6 caracteres.'}), 400

    user = User.query.filter_by(reset_token=token).first()

    # Validação: Token existe e não expirou
    if not user or (user.reset_expiration and user.reset_expiration < datetime.utcnow()):
        return jsonify({'message': 'O link de redefinição é inválido ou expirou.'}), 400

    # Se todas as validações passarem, atualiza a senha
    user.senha = generate_password_hash(new_password, method='pbkdf2:sha256')
    user.reset_token = None
    user.reset_expiration = None
    user.mudaSenha = False
    db.session.commit()

    return jsonify({'message': 'A sua senha foi redefinida com sucesso!'}), 200

# --- Endpoints CRUD para Projetos ---
@app.route('/api/projects', methods=['GET', 'POST'])
@login_required
def api_projects():
    if request.method == 'GET':
        # Retorna apenas projetos do utilizador com sessão iniciada
        projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
        projects_data = [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'status': p.status,
            'createdAt': p.created_at.isoformat()
        } for p in projects]
        return jsonify(projects_data), 200

    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        status = data.get('status', 'A Fazer')

        # Validação para POST (criação de projeto)
        if not name or len(name.strip()) < 3:
            return jsonify({'message': 'O nome do projeto é obrigatório e deve ter no mínimo 3 caracteres.'}), 400
        # Descrição opcional, não precisa de validação de presença, mas pode ter de comprimento
        if description and len(description.strip()) < 5:
            return jsonify({'message': 'A descrição do projeto deve ter no mínimo 5 caracteres, se fornecida.'}), 400
        if status not in ['A Fazer', 'Em Andamento', 'Concluído']: # Garante que o status é um dos valores permitidos
            return jsonify({'message': 'Status de projeto inválido.'}), 400


        new_project = Project(user_id=current_user.id, name=name, description=description, status=status)
        db.session.add(new_project)
        db.session.commit()

        return jsonify({'message': 'Projeto criado com sucesso!', 'project': {
            'id': new_project.id,
            'name': new_project.name,
            'description': new_project.description,
            'status': new_project.status,
            'createdAt': new_project.created_at.isoformat()
        }}), 201

@app.route('/api/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_single_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'message': 'Projeto não encontrado'}), 404

    # Garante que o utilizador com sessão iniciada é o proprietário do projeto
    if project.user_id != current_user.id:
        return jsonify({'message': 'Não autorizado a aceder a este projeto.'}), 403

    if request.method == 'GET':
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'status': project.status,
            'createdAt': project.created_at.isoformat()
        }), 200

    elif request.method == 'PUT':
        data = request.get_json()
        new_name = data.get('name')
        new_description = data.get('description')
        new_status = data.get('status')

        # Validação para PUT (atualização de projeto)
        if new_name is not None and len(new_name.strip()) < 3:
            return jsonify({'message': 'O nome do projeto é obrigatório e deve ter no mínimo 3 caracteres.'}), 400
        if new_description is not None and len(new_description.strip()) < 5:
            return jsonify({'message': 'A descrição do projeto deve ter no mínimo 5 caracteres, se fornecida.'}), 400
        if new_status is not None and new_status not in ['A Fazer', 'Em Andamento', 'Concluído']:
            return jsonify({'message': 'Status de projeto inválido.'}), 400

        if new_name is not None:
            project.name = new_name
        if new_description is not None:
            project.description = new_description
        if new_status is not None:
            project.status = new_status
        
        db.session.commit()
        return jsonify({'message': 'Projeto atualizado com sucesso!'}), 200

    elif request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projeto excluído com sucesso!'}), 200

# Bloco para rodar a aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria as tabelas no banco de dados
        # Cria utilizador administrador padrão se não existir
        if not User.query.filter_by(email='admin@exemplo.com').first():
            admin_user = User(
                email='admin@exemplo.com',
                senha=generate_password_hash('123456', method='pbkdf2:sha256'),
                tipoUsuario=True, # Admin
                liberacao=True
            )
            db.session.add(admin_user)
            db.session.commit()
            admin_profile = Profile(userID=admin_user.id, nome='Administrador Exemplo', contato='11999999999')
            db.session.add(admin_profile)
            db.session.commit()
            print("Utilizador administrador padrão criado: admin@exemplo.com / 123456")

        # Mock de projetos para o utilizador administrador (apenas se o banco estiver vazio)
        if User.query.filter_by(email='admin@exemplo.com').first() and not Project.query.filter_by(user_id=1).first():
            mock_projects = [
                Project(user_id=1, name='Desenvolvimento do Backend', description='Criar a API REST com Flask e SQLite.', status='Em Andamento'),
                Project(user_id=1, name='Criação do Frontend SPA', description='Desenvolver a interface com HTML, CSS e JS.', status='Concluído'),
                Project(user_id=1, name='Testes e Implementação', description='Realizar testes unitários e de integração.', status='A Fazer'),
            ]
            for proj in mock_projects:
                db.session.add(proj)
            db.session.commit()
            print("Projetos mock para administrador criados.")

    app.run(debug=True)
