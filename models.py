from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id             = db.Column(db.Integer,     primary_key=True)
    login          = db.Column(db.String(50),  unique=True, nullable=False)
    age            = db.Column(db.Integer,     nullable=True)
    mois_naissance = db.Column(db.Integer,     nullable=True)  # 1-12
    password_hash  = db.Column(db.String(256), nullable=False)
    scores         = db.relationship('Score', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.login}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Phrase(db.Model):
    __tablename__ = 'phrases'

    id           = db.Column(db.Integer,     primary_key=True)
    texte        = db.Column(db.String(500), nullable=False)
    mot_errone   = db.Column(db.String(100), nullable=False)
    mot_corrige  = db.Column(db.String(100), nullable=False)
    position_mot = db.Column(db.Integer,     nullable=False)
    difficulte   = db.Column(db.Integer,     nullable=False)
    temps_limite = db.Column(db.Integer,     nullable=False)
    groupe       = db.Column(db.String(50),  nullable=True)   # regroupe les variantes d'une même phrase

    def __repr__(self):
        return f'<Phrase {self.id} - diff:{self.difficulte}>'


class Score(db.Model):
    __tablename__ = 'scores'

    id      = db.Column(db.Integer,  primary_key=True)
    user_id = db.Column(db.Integer,  db.ForeignKey('users.id'), nullable=False)
    valeur  = db.Column(db.Integer,  nullable=False)
    date    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Score {self.valeur} - {self.date}>'