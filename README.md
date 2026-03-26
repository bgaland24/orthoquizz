# OrthoQuizz

## Installation locale

```bash
pip install -r requirements.txt
cp .env.example .env   # puis édite .env avec tes valeurs

#si pertinent 
python init_db.py

python run.py
```

Ouvrir http://127.0.0.1:5000

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
