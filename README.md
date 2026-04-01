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

Colonnes : `texte, mot_errone, mot_corrige, position_mot, type, difficulte, temps_limite, groupe`

- `position_mot` : index base 0 dans `texte.split()` — ponctuation collée au mot
- `type` : catégorie de la faute — `homophone`, `accent`, `accord`, `conjugaison`, `doublon`, `lettre_manquante`, `mot_incorrect`, `pluriel`, `cod`
- `difficulte` : 1 à 10
- `groupe` : optionnel — un seul par groupe par quiz

Après modification du CSV : recharger via le bouton **"Recharger depuis le CSV"** dans `/admin` (ne supprime pas les users ni les scores).

## Migrations de base de données

Pour appliquer les migrations sans perte de données (ajout de colonnes, rechargement du CSV) :

```bash
python migrate_and_reload.py
```

Ce script :
1. Applique toutes les migrations Alembic en attente (`flask db upgrade`)
2. Recharge uniquement la table `Phrase` depuis `data/phrases.csv`

Les tables `User` et `Score` ne sont jamais touchées.

**Première installation** (BDD vide, sans historique Alembic) :
```bash
flask db stamp base
python migrate_and_reload.py
```

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

4. Appliquer les migrations : `python migrate_and_reload.py`
5. Recharger depuis l'onglet **Web** de PythonAnywhere.
