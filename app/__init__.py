import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'routes.api_login'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_e_longa_aqui'
    # Corrigido para usar a pasta de instância padrão do Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'gestorprojetos.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/')

    with app.app_context():
        db.create_all()
        from .utils import create_default_admin_and_projects
        create_default_admin_and_projects()

    return app