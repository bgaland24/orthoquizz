print('1. démarrage')
from app import app, db
print('2. app importée')
import models
print('3. models importé')

with app.app_context():
    print('4. dans le contexte')
    db.create_all()
    print('5. Base de données créée.')