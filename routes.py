from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm


class CsrfForm(FlaskForm):
    pass


def register_routes(app):

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
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('quiz_home'))

        form = CsrfForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erreur de sécurité, réessaie.', 'error')
                return render_template('register.html', form=form)

            login_val        = request.form.get('login',            '').strip()
            # age              = request.form.get('age',              '').strip()
            # email_parent     = request.form.get('email_parent',     '').strip()
            password         = request.form.get('password',         '')
            password_confirm = request.form.get('password_confirm', '')

            errors = []
            if len(login_val) < 3:
                errors.append('Le pseudo doit faire au moins 3 caractères.')
            # if not age.isdigit() or not (5 <= int(age) <= 18):
            #     errors.append("L'âge doit être compris entre 5 et 18 ans.")
            # if '@' not in email_parent:
            #     errors.append("L'email des parents n'est pas valide.")
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
                # age=int(age),
                # email_parent=email_parent,
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
    # Admin
    # -----------------------------------------------------------------------

    @app.route('/admin/login', methods=['GET', 'POST'])
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
        from models import User, Phrase
        return render_template('admin_dashboard.html',
                               form=CsrfForm(),
                               nb_phrases=Phrase.query.count(),
                               nb_users=User.query.count())

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
        return redirect(url_for('admin_login'))

    # -----------------------------------------------------------------------
    # Quiz
    # -----------------------------------------------------------------------

    @app.route('/quiz')
    @login_required
    def quiz_home():
        from models import Phrase
        return render_template('quiz_home.html',
                               form=CsrfForm(),
                               nb_questions=min(10, Phrase.query.count()))

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

        idx        = quiz['current_index']
        phrase     = Phrase.query.get(quiz['phrase_ids'][idx])
        type_info  = get_type_info(phrase.difficulte)
        pokemon_id = type_info['pokemon_ids'][phrase.id % len(type_info['pokemon_ids'])]
        pokemon_nom = POKEMON_NOMS.get(pokemon_id, 'Mystérieux')

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

        try:
            position_cliquee = int(request.form.get('position_cliquee', -1))
            temps_restant    = max(0, int(request.form.get('temps_restant', 0)))
        except ValueError:
            position_cliquee, temps_restant = -1, 0

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
        from services import get_derniers_scores
        derniers_scores = get_derniers_scores(current_user.id)
        return render_template('quiz_result.html',
                               form=CsrfForm(),
                               score_final=derniers_scores[0].valeur if derniers_scores else 0,
                               last_scores=derniers_scores)