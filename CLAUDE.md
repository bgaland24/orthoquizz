# OrthoQuizz — Guide Claude

## Bonnes pratiques & architecture

### Conventions de code
- Lire un fichier avant de le modifier — toujours
- Proposer les options avant tout changement architectural
- Ne jamais supprimer du code sans demande explicite
- Réponses courtes, expliquer uniquement ce qui impacte d'autres fichiers
- Pas de `console.log` en prod

### CSS / JS
- Tout CSS dans `static/css/`, tout JS dans `static/js/` — aucun `<style>` ou `<script>` inline dans les templates
- Passer les données Jinja2 → JS via `data-attributes`, pas via interpolation dans `<script>`
- Exception tolérée : `style="--css-var: {{ val }}"` pour les CSS custom properties dynamiques (carte Pokémon)
- Fichiers : `base.css` (partagé), `quiz-question.css/js`, `quiz-home.css`, `quiz-result.css`, `login.css`, `admin.css`, `pokemon-slider.js`

### Sécurité
- CSP : `script-src 'self'` sans `unsafe-inline` — configurée dans `app.py:set_security_headers`
- CSRF : `CsrfForm` + `form.validate_on_submit()` sur tous les POST
- Rate limiting POST uniquement (`methods=['POST']`) — ne jamais limiter les GET
- Validation côté serveur obligatoire même si HTML a `pattern`/`minlength`
- Login : regex `^[a-zA-ZÀ-ÿ0-9_-]{3,15}$`, password : 6-20 chars
- Mot de passe haché via `werkzeug` — jamais comparé en clair
- Valeurs entières castées `int()` avant toute requête DB
- Pas d'interpolation de données utilisateur dans les attributs JS (`onsubmit`, `onclick`)

### Templates Jinja2
- Macros réutilisables dans `_macros.html` : `pokemon_slider()`, `mois_select(selected='')`
- `base.html` charge `base.css` — les templates enfants ajoutent leur CSS via `{% block extra_styles %}`
- Auto-échappement Jinja2 actif — ne jamais utiliser `{{ var | safe }}` sur des données utilisateur

### Base de données
- ORM SQLAlchemy uniquement — aucun SQL construit par concaténation
- Migrations via Flask-Migrate : `flask db migrate` / `flask db upgrade`
- Première mise en prod sans historique Alembic : `flask db stamp base` puis `flask db upgrade`

---

## Description du projet

App Flask quiz orthographe pour enfants de primaire. Une phrase avec un mot mal orthographié s'affiche en carte Pokémon, l'enfant clique sur l'erreur contre la montre.

**Stack** : Flask + Flask-Login + Flask-WTF + SQLAlchemy + SQLite | Jinja2 + dark theme CSS | PythonAnywhere

### Fichiers clés
- `app.py` — `create_app()`, extensions, headers sécurité, config
- `models.py` — `User`, `Phrase`, `Score`
- `routes.py` — toutes les routes dans `register_routes(app)` + `CsrfForm` + `Limiter`
- `services.py` — `selectionner_phrases`, `calculer_points`, `get_type_info`, `POKEMON_NOMS`, `recharger_phrases`
- `moderation.py` — filtre mots interdits dans les pseudos
- `data/phrases.csv` — `texte, mot_errone, mot_corrige, position_mot, difficulte, temps_limite, groupe`
- `init_db.py` — recrée `Phrase` et `Score` uniquement (conserve `User`)

### Modèle de données
- **User** : `id, login, password_hash, age, mois_naissance`
- **Phrase** : `id, texte, mot_errone, mot_corrige, position_mot, difficulte (1-10), temps_limite, groupe`
- **Score** : `id, user_id, valeur, date`

### Points d'attention CSV
- `position_mot` : index **base 0** dans `texte.split()` — ponctuation collée au mot
- `groupe` : optionnel — un seul par groupe par quiz (`_un_par_groupe()`)
- Après modif CSV : `init_db.py` puis recharger via `/admin`

### Fonctionnalités
- Auth login/register/logout + reset password (âge + mois, sans email)
- Quiz adaptatif : difficulté ≤3 / ≥4 / ≥7 selon score max joueur
- Timer serveur (anti-triche), bonus points rapidité
- Carte Pokémon : 5 types visuels selon difficulté, image PokeAPI CDN, nom FR
- Protection retour arrière : `Cache-Control: no-store` + vérif `phrase_id` en session
- Top 10 leaderboard sur page d'accueil quiz
- Admin `/admin` : rechargement CSV, liste utilisateurs, suppression
