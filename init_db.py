print('1. démarrage')
from app import app, db
print('2. app importée')
import models
print('3. models importé')

with app.app_context():
    print('4. dans le contexte')
    # On supprime uniquement les tables non-utilisateurs pour préserver les comptes
    models.Score.__table__.drop(db.engine, checkfirst=True)
    models.Phrase.__table__.drop(db.engine, checkfirst=True)
    print('4b. tables Phrase et Score supprimées (utilisateurs conservés).')
    db.create_all()
    print('5. Base de données recréée.')