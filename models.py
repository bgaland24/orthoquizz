from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)
    login        = db.Column(db.String(50),  unique=True, nullable=False)
    email_parent = db.Column(db.String(120), nullable=False)
    age          = db.Column(db.Integer,     nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Relation : un User a plusieurs Scores
    scores = db.relationship('Score', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.login}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# Phrase
# ---------------------------------------------------------------------------

class Phrase(db.Model):
    __tablename__ = 'phrases'

    id          = db.Column(db.Integer, primary_key=True)
    texte       = db.Column(db.String(500), nullable=False)
    mot_errone  = db.Column(db.String(100), nullable=False)
    position_mot = db.Column(db.Integer,   nullable=False)  # index du mot (base 0)
    difficulte  = db.Column(db.Integer,    nullable=False)  # 1 à 10
    temps_limite = db.Column(db.Integer,   nullable=False)  # en secondes

    def __repr__(self):
        return f'<Phrase {self.id} - diff:{self.difficulte}>'


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------

class Score(db.Model):
    __tablename__ = 'scores'

    id      = db.Column(db.Integer,   primary_key=True)
    user_id = db.Column(db.Integer,   db.ForeignKey('users.id'), nullable=False)
    valeur  = db.Column(db.Integer,   nullable=False)
    date    = db.Column(db.DateTime,  nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Score {self.valeur} - {self.date}>'


# ---------------------------------------------------------------------------
# Calcul des points — fonction isolée
# ---------------------------------------------------------------------------

def calculer_points(phrase: Phrase, reponse_correcte: bool, temps_restant: int) -> int:
    """
    Calcule les points marqués pour une question.

    Args:
        phrase          : la Phrase posée (contient difficulte et temps_limite)
        reponse_correcte: True si l'enfant a cliqué sur le bon mot
        temps_restant   : secondes restantes quand l'enfant a répondu (0 si timeout)

    Returns:
        int : points marqués pour cette question

    Formule actuelle (simple, facile à changer ici sans toucher au reste) :
        - Mauvaise réponse ou timeout → 0 point
        - Bonne réponse → difficulte * (1 + temps_restant / temps_limite)
          ex: difficulte=6, temps_limite=12, temps_restant=9
              → 6 * (1 + 9/12) = 6 * 1.75 = 10.5 → arrondi à 10
    """
    if not reponse_correcte:
        return 0

    bonus_temps = temps_restant / phrase.temps_limite
    points = phrase.difficulte * (1 + bonus_temps)
    return round(points)