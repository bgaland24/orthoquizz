# OrthoQuizz — Contexte projet pour Claude

## Description
Application web Flask pour aider les enfants de primaire à s'améliorer en orthographe.
Format : quiz style carte Pokémon — une phrase s'affiche, l'enfant clique sur le mot mal orthographié contre la montre.

## Stack
- **Backend** : Flask + Flask-Login + Flask-WTF (CSRF) + SQLAlchemy + SQLite
- **Frontend** : Jinja2 + Bootstrap 5 (CDN) + CSS inline (dark theme)
- **Déploiement cible** : PythonAnywhere (`from app import app as application`)

## Structure des fichiers clés
- `app.py` — factory `create_app()`, extensions globales (`db`, `login_manager`, `csrf`)
- `models.py` — `User`, `Phrase`, `Score` + `@login_manager.user_loader`
- `routes.py` — toutes les routes dans `register_routes(app)` avec `CsrfForm` pour CSRF
- `services.py` — `selectionner_phrases`, `calculer_points`, `get_type_info`, `POKEMON_NOMS`, `recharger_phrases`
- `init_db.py` — recrée uniquement les tables `Phrase` et `Score` (conserve `User`)
- `data/phrases.csv` — source des phrases, colonnes : `texte, mot_errone, mot_corrige, position_mot, difficulte, temps_limite, groupe`
- `run.py` — point d'entrée local

## Modèle de données
- **User** : `id, login, password_hash` (age et email_parent commentés/désactivés)
- **Phrase** : `id, texte, mot_errone, mot_corrige, position_mot, difficulte (1-10), temps_limite, groupe (nullable)`
- **Score** : `id, user_id, valeur, date`

## Fonctionnalités implémentées
- Authentification (login/register/logout) + interface admin (rechargement CSV depuis `/admin`)
- Quiz adaptatif selon score max du joueur : difficulté ≤3 / ≥4 / ≥7
- Sélection sans doublon de variante : champ `groupe` dans `Phrase`, fonction `_un_par_groupe()`
- Timer par question, calcul de points avec bonus temps
- Carte Pokémon visuelle : image depuis PokeAPI sprites CDN, nom FR depuis `POKEMON_NOMS`
- 5 types visuels selon difficulté : Normal / Plante / Eau / Feu / Psychique
- Protection retour arrière navigateur : `Cache-Control: no-store` + vérification `phrase_id` en session
- CSS partagé dark theme dans `base.html` (`.home-title`, `.form-box`, `.action-btn`, etc.)
- Templates : `login.html`, `register.html`, `quiz_home.html`, `quiz_question.html`, `quiz_result.html`

## Points d'attention
- `position_mot` est un index **base 0** dans `phrase.texte.split()`
- La ponctuation est collée au mot lors du split — pas d'espaces autour des tirets ni avant les apostrophes dans le CSV
- `groupe` est lu en optionnel dans l'import CSV (`row.get('groupe', '')`)
- Après modification du modèle → relancer `init_db.py` puis recharger le CSV via `/admin`
- Les `console.log` de debug ont été retirés du JS — ne pas les remettre en prod

## Préférences de collaboration
- **Commenter plutôt que supprimer** : ne jamais supprimer du code sans demande explicite
- **Valider avant d'implémenter** : pour tout changement architectural, proposer les options d'abord
- **Lire avant de modifier** : toujours lire un fichier avant de l'éditer, surtout le CSV
- **Réponses courtes** : aller droit au but, expliquer uniquement ce qui impacte d'autres fichiers
