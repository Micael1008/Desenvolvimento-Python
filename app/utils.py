from . import db
from .models import User, Profile, Project
from werkzeug.security import generate_password_hash

def create_default_admin_and_projects():
    if not User.query.filter_by(email='admin@exemplo.com').first():
        admin_user = User(
            email='admin@exemplo.com',
            senha=generate_password_hash('123456', method='pbkdf2:sha256'),
            tipoUsuario=True,
            liberacao=True
        )
        db.session.add(admin_user)
        db.session.commit()
        admin_profile = Profile(userID=admin_user.id, nome='Administrador Exemplo', contato='11999999999')
        db.session.add(admin_profile)
        db.session.commit()
        print("Utilizador administrador padrão criado: admin@exemplo.com / 123456")

        if not Project.query.filter_by(user_id=admin_user.id).first():
            mock_projects = [
                Project(user_id=admin_user.id, name='Desenvolvimento do Backend', description='Criar a API REST com Flask e SQLite.', status='Em Andamento'),
                Project(user_id=admin_user.id, name='Criação do Frontend SPA', description='Desenvolver a interface com HTML, CSS e JS.', status='Concluído'),
                Project(user_id=admin_user.id, name='Testes e Implementação', description='Realizar testes unitários e de integração.', status='A Fazer'),
            ]
            for proj in mock_projects:
                db.session.add(proj)
            db.session.commit()
            print("Projetos mock para administrador criados.")