# OrthoQuizz

Quiz d'orthographe pour enfants de primaire. Format carte Pokémon — clique sur le mot mal orthographié, contre la montre.

**Stack** : Flask · SQLAlchemy · SQLite · Jinja2 · PythonAnywhere

## Installation locale

```bash
pip install -r requirements.txt
cp .env.example .env      # renseigner SECRET_KEY, ADMIN_LOGIN, ADMIN_PASSWORD
python init_db.py         # crée la BDD et charge data/phrases.csv
python run.py
```

Première utilisation avec Flask-Migrate :
```bash
flask db stamp base
flask db upgrade
```

## Variables d'environnement (`.env`)

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Clé secrète Flask (générer : `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `ADMIN_LOGIN` | Identifiant admin |
| `ADMIN_PASSWORD` | Mot de passe admin |

## Phrases (`data/phrases.csv`)

Colonnes : `texte, mot_errone, mot_corrige, position_mot, difficulte, temps_limite, groupe`

- `position_mot` : index base 0 dans `texte.split()` — ponctuation collée au mot
- `difficulte` : 1 à 10
- `groupe` : optionnel — un seul par groupe par quiz

Après modification : `python init_db.py` puis recharger via `/admin`.

## Déploiement PythonAnywhere

1. `git pull` dans `/home/bgaland/orthoquizz`
2. Créer `.env` (voir `.env.example`)
3. Fichier WSGI :

```python
import sys, os
from dotenv import load_dotenv
project_folder = '/home/bgaland/orthoquizz'
load_dotenv(os.path.join(project_folder, '.env'))
if project_folder not in sys.path:
    sys.path.append(project_folder)
from app import app as application
```

4. Recharger depuis l'onglet **Web** de PythonAnywhere.
