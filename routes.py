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
    # Page d'accueil
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

            login        = request.form.get('login',            '').strip()
            age          = request.form.get('age',              '').strip()
            email_parent = request.form.get('email_parent',     '').strip()
            password     = request.form.get('password',         '')
            password_confirm = request.form.get('password_confirm', '')

            errors = []
            if len(login) < 3:
                errors.append('Le pseudo doit faire au moins 3 caractères.')
            if not age.isdigit() or not (5 <= int(age) <= 18):
                errors.append("L'âge doit être compris entre 5 et 18 ans.")
            if '@' not in email_parent:
                errors.append("L'email des parents n'est pas valide.")
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

            if User.query.filter_by(login=login).first():
                flash('Ce pseudo est déjà pris, choisis-en un autre.', 'error')
                return render_template('register.html', form=form)

            user = User(
                login=login,
                age=int(age),
                email_parent=email_parent,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
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

            login_val = request.form.get('login', '').strip()
            password  = request.form.get('password', '')

            from models import User
            user = User.query.filter_by(login=login_val).first()

            if not user or not check_password_hash(user.password_hash, password):
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
    # Admin — login
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

            login_val = request.form.get('login', '').strip()
            password  = request.form.get('password', '')

            if login_val == app.config['ADMIN_LOGIN'] and password == app.config['ADMIN_PASSWORD']:
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))

            flash('Identifiants incorrects.', 'error')

        return render_template('admin_login.html', form=form)

    # -----------------------------------------------------------------------
    # Admin — dashboard
    # -----------------------------------------------------------------------

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        from models import User, Phrase
        form      = CsrfForm()
        nb_phrases = Phrase.query.count()
        nb_users   = User.query.count()
        return render_template('admin_dashboard.html',
                               form=form,
                               nb_phrases=nb_phrases,
                               nb_users=nb_users)

    # -----------------------------------------------------------------------
    # Admin — rechargement CSV
    # -----------------------------------------------------------------------

    @app.route('/admin/reload', methods=['POST'])
    @admin_required
    def admin_reload():
        from services import recharger_phrases
        succes, message = recharger_phrases(app.config['PHRASES_CSV'])
        flash(message, 'success' if succes else 'error')
        return redirect(url_for('admin_dashboard'))

    # -----------------------------------------------------------------------
    # Admin — déconnexion
    # -----------------------------------------------------------------------

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('is_admin', None)
        return redirect(url_for('admin_login'))

    # -----------------------------------------------------------------------
    # Quiz home — stub
    # -----------------------------------------------------------------------

    @app.route('/quiz')
    @login_required
    def quiz_home():
        return f'<h1>Bonjour {current_user.login} !</h1><a href="/logout">Déconnexion</a>'