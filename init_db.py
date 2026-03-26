print('1. démarrage')
import os
from app import app, db
print('2. app importée')
import models
print('3. models importé')

with app.app_context():
    print('4. dans le contexte')
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        os.remove(db_path)
        print('4b. ancienne base supprimée.')
    db.create_all()
    print('5. Base de données créée.')