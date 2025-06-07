# app.py
# Arquivo principal da aplicação FreelaHub

# Importa as classes e funções necessárias do Flask
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurações do Flask
# Chave secreta para segurança das sessões (MUITO IMPORTANTE!)
# Em produção, use uma variável de ambiente: os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui_para_producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Configura o banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desativa o rastreamento de modificações (melhora performance)

# Inicializa o SQLAlchemy para interagir com o banco de dados
db = SQLAlchemy(app)

# Configura o Flask-Login para gerenciar sessões de usuário
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Define a rota para onde o usuário será redirecionado se não estiver logado

# --- Modelos do Banco de Dados ---
# Definindo os modelos (tabelas) do banco de dados com SQLAlchemy
# Eles herdam de db.Model

class User(db.Model, UserMixin):
    """
    Modelo para a tabela USUÁRIOS.
    Representa os usuários da plataforma (freelancers ou admins).
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipoUsuario = db.Column(db.Boolean, default=False) # False=user (freelancer), True=admin
    email = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False) # Aumentado para armazenar hash de senha
    mudaSenha = db.Column(db.Boolean, default=False) # False=não mudar, True=mudar no próximo login
    liberacao = db.Column(db.Boolean, default=True) # False=inativo, True=ativo

    # Relacionamento com a tabela PERFIL (um usuário tem um perfil)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.email}', Tipo: {self.tipoUsuario}, Ativo: {self.liberacao})"

class Profile(db.Model):
    """
    Modelo para a tabela PERFIL.
    Armazena informações adicionais do perfil do usuário.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=True) # Nome completo
    contato = db.Column(db.String(11), nullable=True) # Telefone/WhatsApp (DDD + 9 dígitos)
    foto = db.Column(db.String(255), nullable=True, default='default.jpg') # Caminho para imagem (ex: 'static/img/profile_pics/default.jpg')

    def __repr__(self):
        return f"Profile('{self.nome}', Contato: {self.contato})"

class Project(db.Model):
    """
    Modelo de exemplo para a tabela PROJETOS.
    Será usado para o CRUD principal da aplicação.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Aberto') # Ex: 'Aberto', 'Em Andamento', 'Concluído'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relacionamento com o usuário que criou o projeto
    user = db.relationship('User', backref='projects', lazy=True)

    def __repr__(self):
        return f"Project('{self.title}', '{self.status}')"


# --- Funções do Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    """
    Função para recarregar o objeto User do ID do usuário armazenado na sessão.
    Necessário para o Flask-Login.
    """
    return User.query.get(int(user_id))

# --- Rotas da Aplicação ---

@app.route('/')
def home():
    """
    Rota para a página inicial (index.html).
    """
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para a página de login.
    Lida com a exibição do formulário GET e o processamento do POST.
    """
    # Se o usuário já estiver logado, redireciona para a página de perfil ou dashboard
    if current_user.is_authenticated:
        return redirect(url_for('profile')) # Ou 'dashboard'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False # "Lembrar-me"

        user = User.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta
        if not user or not check_password_hash(user.senha, password):
            flash('Por favor, verifique seu e-mail ou senha e tente novamente.', 'danger')
            return redirect(url_for('login'))

        # Verifica se o usuário está ativo
        if not user.liberacao:
            flash('Sua conta está inativa. Entre em contato com o suporte.', 'warning')
            return redirect(url_for('login'))

        # Loga o usuário
        login_user(user, remember=remember)
        flash('Login realizado com sucesso!', 'success')

        # Se o usuário precisa mudar a senha, redireciona para a página de mudança de senha
        if user.mudaSenha:
            return redirect(url_for('change_password_on_login'))

        # Redireciona para a página de perfil após o login
        return redirect(url_for('profile')) # Ou para a próxima URL se houver (next_page = request.args.get('next'))

    return render_template('paginaLogin.html') # Exibe o formulário de login/cadastro

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para a página de registro de novos usuários.
    """
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type') # 'freelancer' ou 'admin' (se houver checkbox/radio)

        # Validações básicas
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6: # Exemplo de validação de senha
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('register'))

        # Verifica se o e-mail já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Este e-mail já está cadastrado.', 'danger')
            return redirect(url_for('register'))

        # Hash da senha antes de salvar
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Define tipo de usuário (exemplo: se houver um campo no form para isso)
        is_admin = True if user_type == 'admin' else False

        new_user = User(
            email=email,
            senha=hashed_password,
            tipoUsuario=is_admin,
            mudaSenha=False, # Por padrão, não precisa mudar a senha no primeiro login
            liberacao=True # Por padrão, usuário ativo
        )
        db.session.add(new_user)
        db.session.commit()

        # Cria um perfil vazio para o novo usuário
        new_profile = Profile(userID=new_user.id)
        db.session.add(new_profile)
        db.session.commit()

        flash('Sua conta foi criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('paginaLogin.html') # Pode ser um template separado para registro se preferir

@app.route('/logout')
@login_required # Garante que apenas usuários logados podem acessar esta rota
def logout():
    """
    Rota para realizar o logout do usuário.
    """
    logout_user()
    flash('Você foi desconectado(a).', 'info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Rota para o perfil do usuário.
    Permite visualizar e editar informações do perfil.
    """
    user_profile = Profile.query.filter_by(userID=current_user.id).first()
    if not user_profile:
        # Se por algum motivo o perfil não existir, cria um
        user_profile = Profile(userID=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'POST':
        user_profile.nome = request.form.get('nome')
        user_profile.contato = request.form.get('contato')
        # Lógica para upload de foto virá depois, é mais complexa
        # Por enquanto, apenas atualiza nome e contato

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user, profile=user_profile)

@app.route('/change_password_on_login', methods=['GET', 'POST'])
@login_required
def change_password_on_login():
    """
    Rota para forçar a mudança de senha no próximo login.
    """
    if not current_user.mudaSenha:
        return redirect(url_for('profile')) # Se não precisa mudar, redireciona

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if new_password != confirm_new_password:
            flash('As novas senhas não coincidem.', 'danger')
            return redirect(url_for('change_password_on_login'))

        if len(new_password) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('change_password_on_login'))

        current_user.senha = generate_password_hash(new_password, method='pbkdf2:sha256')
        current_user.mudaSenha = False # Desativa a flag após a mudança
        db.session.commit()

        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('profile'))

    return render_template('change_password_on_login.html')

# --- Rotas para o CRUD de Projetos (Exemplo da Aplicação Principal) ---
@app.route('/projects')
@login_required
def list_projects():
    """
    Lista todos os projetos (ou apenas os do usuário logado, dependendo da lógica).
    """
    projects = Project.query.all() # Ou Project.query.filter_by(user_id=current_user.id).all()
    return render_template('projects.html', projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """
    Cria um novo projeto.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status', 'Aberto') # Padrão 'Aberto'

        new_proj = Project(
            user_id=current_user.id,
            title=title,
            description=description,
            status=status
        )
        db.session.add(new_proj)
        db.session.commit()
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('list_projects'))
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    """
    Visualiza um projeto específico.
    """
    project = Project.query.get_or_404(project_id)
    # Opcional: Adicionar verificação de permissão se apenas o criador puder ver
    return render_template('view_project.html', project=project)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """
    Edita um projeto existente.
    Apenas o criador do projeto pode editar.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Você não tem permissão para editar este projeto.', 'danger')
        return redirect(url_for('list_projects'))

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.status = request.form.get('status')
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('view_project', project_id=project.id))
    return render_template('edit_project.html', project=project)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """
    Deleta um projeto.
    Apenas o criador do projeto pode deletar.
    """
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Você não tem permissão para deletar este projeto.', 'danger')
        return redirect(url_for('list_projects'))

    db.session.delete(project)
    db.session.commit()
    flash('Projeto deletado com sucesso!', 'success')
    return redirect(url_for('list_projects'))


# --- Rotas para a REST API (Exemplo) ---
# Usaremos jsonify para retornar respostas JSON

from flask import jsonify

@app.route('/api/projects', methods=['GET'])
def api_list_projects():
    """
    API: Retorna uma lista de todos os projetos em JSON.
    """
    projects = Project.query.all()
    projects_data = []
    for proj in projects:
        projects_data.append({
            'id': proj.id,
            'user_id': proj.user_id,
            'title': proj.title,
            'description': proj.description,
            'status': proj.status,
            'created_at': proj.created_at.isoformat()
        })
    return jsonify(projects_data)

@app.route('/api/project/<int:project_id>', methods=['GET'])
def api_get_project(project_id):
    """
    API: Retorna detalhes de um projeto específico em JSON.
    """
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'message': 'Projeto não encontrado'}), 404
    project_data = {
        'id': project.id,
        'user_id': project.user_id,
        'title': project.title,
        'description': project.description,
        'status': project.status,
        'created_at': project.created_at.isoformat()
    }
    return jsonify(project_data)

# Nota: Para API de criação/edição/deleção, você precisaria de autenticação de API (ex: tokens JWT)
# e validação de dados, que são mais avançados. Este é um exemplo básico.


# --- Inicialização do Banco de Dados ---
# Este bloco deve ser executado APENAS UMA VEZ para criar as tabelas.
# Em um ambiente de produção, você usaria ferramentas de migração (ex: Flask-Migrate).
# REMOVIDO: @app.before_first_request
# A criação das tabelas e o usuário admin agora estão apenas no bloco if __name__ == '__main__':

# Bloco para rodar a aplicação
if __name__ == '__main__':
    # Cria as tabelas do banco de dados antes de rodar o app
    # Isso é feito aqui para simplicidade, mas em produção, use `flask db upgrade`
    with app.app_context():
        db.create_all()
        # Exemplo: Criar um usuário admin padrão se não existir
        if not User.query.filter_by(email='admin@freelahub.com').first():
            admin_user = User(
                email='admin@freelahub.com',
                senha=generate_password_hash('admin123', method='pbkdf2:sha256'),
                tipoUsuario=True, # Admin
                liberacao=True
            )
            db.session.add(admin_user)
            db.session.commit()
            admin_profile = Profile(userID=admin_user.id, nome='Administrador FreelaHub', contato='99999999999')
            db.session.add(admin_profile)
            db.session.commit()
            print("Usuário admin padrão criado: admin@freelahub.com / admin123")

    app.run(debug=True)
