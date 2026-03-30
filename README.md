# OrthoQuizz

Application web Flask pour aider les enfants de primaire à s'améliorer en orthographe.
Format : quiz style carte Pokémon — une phrase s'affiche, l'enfant clique sur le mot mal orthographié, contre la montre.

## Fonctionnalités

- Quiz adaptatif selon le score max du joueur (3 niveaux de difficulté)
- Timer par question avec bonus de points selon la rapidité
- Carte Pokémon visuelle (image + nom FR) dont le type change selon la difficulté
- Sélection sans doublon de variante via le champ `groupe`
- Authentification (login/register/logout)
- Interface admin pour recharger les phrases depuis le CSV (`/admin`)
- Protection anti-retour arrière navigateur

## Stack

- **Backend** : Python / Flask + Flask-Login + Flask-WTF + SQLAlchemy + SQLite
- **Frontend** : Jinja2 + Bootstrap 5 (CDN) + dark theme CSS
- **Déploiement cible** : PythonAnywhere

## Installation locale

```bash
pip install -r requirements.txt
cp .env.example .env   # puis édite .env avec tes valeurs
python init_db.py      # crée la base et charge les phrases depuis data/phrases.csv
python run.py
```
flask db stamp base   # BDD vierge de tout historique Alembic
flask db upgrade      # applique toutes les migrations (juste la nôtre ici)

Ouvrir http://127.0.0.1:5000

### Variables d'environnement (`.env`)

| Variable         | Description                                 |
|------------------|---------------------------------------------|
| `SECRET_KEY`     | Clé secrète Flask (chaîne aléatoire longue) |
| `ADMIN_LOGIN`    | Identifiant du compte admin                 |
| `ADMIN_PASSWORD` | Mot de passe du compte admin                |

## Ajouter / modifier des phrases

Les phrases sont dans [data/phrases.csv](data/phrases.csv) avec les colonnes :

```
texte, mot_errone, mot_corrige, position_mot, difficulte, temps_limite, groupe
```

- `position_mot` : index **base 0** du mot dans `texte.split()` (ponctuation collée au mot)
- `difficulte` : entier de 1 à 10
- `temps_limite` : secondes allouées pour répondre
- `groupe` : optionnel — phrases du même groupe ne peuvent pas apparaître dans le même quiz

Après modification du CSV : relancer `init_db.py` puis recharger via `/admin`.

## Déploiement PythonAnywhere

1. `git pull` dans `/home/bgaland/orthoquizz`
2. Créer le `.env` dans ce dossier (voir `.env.example`)
3. Le fichier WSGI `/var/www/bgaland_pythonanywhere_com_wsgi.py` doit contenir :

```python
import sys
import os
from dotenv import load_dotenv

project_folder = '/home/bgaland/orthoquizz'
load_dotenv(os.path.join(project_folder, '.env'))

if project_folder not in sys.path:
    sys.path.append(project_folder)

from app import app as application
```

4. Recharger l'application depuis l'onglet **Web** de PythonAnywhere.
