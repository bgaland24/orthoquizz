from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from moderation import login_est_autorise


class CsrfForm(FlaskForm):
    pass


def register_routes(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[],
        storage_uri='memory://',
    )

    # -----------------------------------------------------------------------
    # Helpers admin
    # -----------------------------------------------------------------------

    def is_admin():
        return session.get('is_admin', False)

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not is_admin():
                flash("Accès réservé à l'administrateur.", 'error')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated

    # -----------------------------------------------------------------------
    # Accueil
    # -----------------------------------------------------------------------

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))
        return redirect(url_for('login'))

    # -----------------------------------------------------------------------
    # Inscription
    # -----------------------------------------------------------------------

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit('10 per minute', methods=['POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))

        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('register.html', form=form)

            login_val        = request.form.get('login',            '').strip()
            age_val          = request.form.get('age',              '').strip()
            mois_val         = request.form.get('mois_naissance',   '').strip()
            password         = request.form.get('password',         '')
            password_confirm = request.form.get('password_confirm', '')

            errors = []
            if len(login_val) < 3:
                errors.append('Le pseudo doit faire au moins 3 caractères.')
            if not login_est_autorise(login_val):
                errors.append("Ce pseudo n'est pas autorisé. Choisis un autre pseudo.")
            if not age_val.isdigit() or not (5 <= int(age_val) <= 99):
                errors.append("L'âge doit être compris entre 5 et 99 ans.")
            if not mois_val.isdigit() or not (1 <= int(mois_val) <= 12):
                errors.append("Le mois de naissance est invalide.")
            if len(password) < 6:
                errors.append('Le mot de passe doit faire au moins 6 caractères.')
            if password != password_confirm:
                errors.append('Les mots de passe ne correspondent pas.')

            if errors:
                for e in errors:
                    flash(e, 'error')
                return render_template('register.html', form=form)

            from models import User
            from app import db

            if User.query.filter_by(login=login_val).first():
                flash('Ce pseudo est déjà pris, choisis-en un autre.', 'error')
                return render_template('register.html', form=form)

            db.session.add(User(
                login=login_val,
                age=int(age_val),
                mois_naissance=int(mois_val),
                password_hash=generate_password_hash(password)
            ))
            db.session.commit()
            flash('Compte créé ! Tu peux te connecter.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    # -----------------------------------------------------------------------
    # Connexion
    # -----------------------------------------------------------------------

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit('10 per minute', methods=['POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))

        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('login.html', form=form)

            from models import User
            user = User.query.filter_by(
                login=request.form.get('login', '').strip()
            ).first()

            if not user or not check_password_hash(
                user.password_hash, request.form.get('password', '')
            ):
                flash('Pseudo ou mot de passe incorrect.', 'error')
                return render_template('login.html', form=form)

            login_user(user)
            return redirect(url_for('quiz_home'))

        return render_template('login.html', form=form)

    # -----------------------------------------------------------------------
    # Déconnexion
    # -----------------------------------------------------------------------

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Tu es déconnecté.', 'success')
        return redirect(url_for('login'))

    # -----------------------------------------------------------------------
    # Mot de passe oublié
    # -----------------------------------------------------------------------

    @app.route('/forgot-password', methods=['GET', 'POST'])
    @limiter.limit('10 per minute', methods=['POST'])
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))

        attempts = session.get('forgot_attempts', 0)
        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('forgot_password.html', form=form, attempts=attempts)

            if attempts >= 3:
                return render_template('forgot_password.html', form=form, attempts=attempts)

            from models import User
            login_val = request.form.get('login', '').strip()
            age_val   = request.form.get('age',   '').strip()
            mois_val  = request.form.get('mois_naissance', '').strip()

            user = User.query.filter_by(login=login_val).first()
            if (user and age_val.isdigit() and mois_val.isdigit()
                    and user.age == int(age_val)
                    and user.mois_naissance == int(mois_val)):
                session['reset_user_id'] = user.id
                session.pop('forgot_attempts', None)
                return redirect(url_for('reset_password'))

            session['forgot_attempts'] = attempts + 1
            flash('Informations incorrectes. Vérifie ton pseudo, ton âge et ton mois de naissance.', 'error')

        return render_template('forgot_password.html', form=form, attempts=session.get('forgot_attempts', 0))

    @app.route('/reset-password', methods=['GET', 'POST'])
    @limiter.limit('10 per minute', methods=['POST'])
    def reset_password():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))

        user_id = session.get('reset_user_id')
        if not user_id:
            return redirect(url_for('login'))

        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('reset_password.html', form=form)

            from models import User
            from app import db
            password         = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')

            if len(password) < 6:
                flash('Le mot de passe doit faire au moins 6 caractères.', 'error')
                return render_template('reset_password.html', form=form)
            if password != password_confirm:
                flash('Les mots de passe ne correspondent pas.', 'error')
                return render_template('reset_password.html', form=form)

            user = User.query.get(user_id)
            if not user:
                session.pop('reset_user_id', None)
                return redirect(url_for('login'))

            user.password_hash = generate_password_hash(password)
            db.session.commit()
            session.pop('reset_user_id', None)
            flash('Mot de passe modifié ! Tu peux te connecter.', 'success')
            return redirect(url_for('login'))

        return render_template('reset_password.html', form=form)

    # -----------------------------------------------------------------------
    # Admin
    # -----------------------------------------------------------------------

    @app.route('/admin/login', methods=['GET', 'POST'])
    @limiter.limit('10 per minute', methods=['POST'])
    def admin_login():
        if is_admin():
            return redirect(url_for('admin_dashboard'))

        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('admin_login.html', form=form)

            if (request.form.get('login', '').strip() == app.config['ADMIN_LOGIN'] and
                    request.form.get('password', '') == app.config['ADMIN_PASSWORD']):
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))

            flash('Identifiants incorrects.', 'error')

        return render_template('admin_login.html', form=form)

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        from models import User, Phrase, Score
        from sqlalchemy import func
        from app import db
        users = (db.session.query(User, func.max(Score.valeur).label('best'))
                 .outerjoin(Score, Score.user_id == User.id)
                 .group_by(User.id)
                 .order_by(User.id.desc())
                 .all())
        return render_template('admin_dashboard.html',
                               form=CsrfForm(),
                               nb_phrases=Phrase.query.count(),
                               nb_users=User.query.count(),
                               users=users)

    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_user(user_id):
        from models import User, Score
        from app import db
        Score.query.filter_by(user_id=user_id).delete()
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
        flash('Utilisateur supprimé.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/reload', methods=['POST'])
    @admin_required
    def admin_reload():
        from services import recharger_phrases
        succes, message = recharger_phrases(app.config['PHRASES_CSV'])
        flash(message, 'success' if succes else 'error')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('is_admin', None)
        flash('Tu es déconnecté.', 'success')
        return redirect(url_for('login'))


    # -----------------------------------------------------------------------
    # Quiz
    # -----------------------------------------------------------------------

    @app.route('/quiz')
    @login_required
    def quiz_home():
        from models import Phrase
        from services import get_top10_classement
        return render_template('quiz_home.html',
                               form=CsrfForm(),
                               nb_questions=min(10, Phrase.query.count()),
                               top10=get_top10_classement(current_user.id))

    @app.route('/quiz/start', methods=['POST'])
    @login_required
    def quiz_start():
        if not CsrfForm().validate_on_submit():
            flash('Erreur de sécurité.', 'error')
            return redirect(url_for('quiz_home'))

        from services import selectionner_phrases
        phrases = selectionner_phrases(10, user_id=current_user.id)

        if not phrases:
            flash('Aucune phrase disponible. Contacte un administrateur.', 'error')
            return redirect(url_for('quiz_home'))

        session['quiz'] = {
            'phrase_ids':    [p.id for p in phrases],
            'current_index': 0,
            'total_score':   0,
            'nb_questions':  len(phrases),
        }
        return redirect(url_for('quiz_question'))

    @app.route('/quiz/question')
    @login_required
    def quiz_question():
        quiz = session.get('quiz')
        if not quiz:
            return redirect(url_for('quiz_home'))

        from models import Phrase
        from services import get_type_info, POKEMON_NOMS

        import time
        idx        = quiz['current_index']
        phrase     = Phrase.query.get(quiz['phrase_ids'][idx])
        type_info  = get_type_info(phrase.difficulte)
        pokemon_id = type_info['pokemon_ids'][phrase.id % len(type_info['pokemon_ids'])]
        pokemon_nom = POKEMON_NOMS.get(pokemon_id, 'Mystérieux')

        # Enregistre l'heure de début uniquement au premier affichage de cette question
        if quiz.get('current_phrase_id') != phrase.id:
            quiz['current_phrase_id'] = phrase.id
            quiz['question_start']    = time.time()
            session['quiz']           = quiz

        response = render_template('quiz_question.html',
                               form=CsrfForm(),
                               phrase=phrase,
                               words=phrase.texte.split(),
                               question_num=idx + 1,
                               total_questions=quiz['nb_questions'],
                               is_last=(idx + 1 == quiz['nb_questions']),
                               score=quiz['total_score'] if idx > 0 else None,
                               type_info=type_info,
                               pokemon_id=pokemon_id,
                               pokemon_nom=pokemon_nom)
        from flask import make_response
        resp = make_response(response)
        resp.headers['Cache-Control'] = 'no-store'
        return resp

    @app.route('/quiz/answer', methods=['POST'])
    @login_required
    def quiz_answer():
        if not CsrfForm().validate_on_submit():
            flash('Erreur de sécurité.', 'error')
            return redirect(url_for('quiz_question'))

        quiz = session.get('quiz')
        if not quiz:
            return redirect(url_for('quiz_home'))

        from models import Phrase
        from services import calculer_points, sauvegarder_score

        phrase = Phrase.query.get(quiz['phrase_ids'][quiz['current_index']])

        # Vérifie que la réponse correspond bien à la question en cours
        # (contre le retour arrière navigateur pour re-répondre)
        try:
            submitted_phrase_id = int(request.form.get('phrase_id', -1))
        except ValueError:
            submitted_phrase_id = -1
        if submitted_phrase_id != phrase.id:
            return redirect(url_for('quiz_question'))

        import time
        try:
            position_cliquee = int(request.form.get('position_cliquee', -1))
        except ValueError:
            position_cliquee = -1

        # Temps restant calculé côté serveur — immunise contre la triche via retour arrière
        elapsed       = time.time() - quiz.get('question_start', time.time())
        temps_restant = max(0, int(phrase.temps_limite - elapsed))

        quiz['total_score']   += calculer_points(
            phrase,
            position_cliquee == phrase.position_mot,
            temps_restant
        )
        quiz['current_index'] += 1
        session['quiz']        = quiz

        if quiz['current_index'] >= quiz['nb_questions']:
            sauvegarder_score(current_user.id, quiz['total_score'])
            session.pop('quiz', None)
            return redirect(url_for('quiz_result'))

        return redirect(url_for('quiz_question'))

    @app.route('/quiz/result')
    @login_required
    def quiz_result():
        from services import get_derniers_scores, get_top_scores, get_rang_score, get_voisins_classement
        derniers_scores = get_derniers_scores(current_user.id)
        score_final     = derniers_scores[0].valeur if derniers_scores else 0
        top_scores      = get_top_scores(current_user.id)
        rang            = get_rang_score(current_user.id, score_final)
        voisins         = get_voisins_classement(current_user.id)
        return render_template('quiz_result.html',
                               form=CsrfForm(),
                               score_final=score_final,
                               last_scores=derniers_scores,
                               top_scores=top_scores,
                               rang=rang,
                               voisins=voisins)