from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipoUsuario = db.Column(db.Boolean, default=False) 
    mudaSenha = db.Column(db.Boolean, default=False)
    liberacao = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_expiration = db.Column(db.DateTime, nullable=True)
    profile = db.relationship('Profile', backref='user', uselist=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=True)
    contato = db.Column(db.String(11), nullable=True) 
    foto = db.Column(db.String(255), nullable=True, default='default.jpg')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    status = db.Column(db.String(20), default='A Fazer', nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)