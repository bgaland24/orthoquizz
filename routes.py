from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm


# Formulaire vide — sert uniquement à générer et valider le token CSRF
# On ne se sert pas des champs Flask-WTF pour garder les templates simples
class CsrfForm(FlaskForm):
    pass


def register_routes(app):

    # -----------------------------------------------------------------------
    # Page d'accueil — redirige selon l'état de connexion
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

            # --- Validations serveur ---
            # On revalide tout ici même si le HTML a des attributs required/min/max
            # car un utilisateur malveillant peut envoyer une requête HTTP directement
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

            # --- Vérification unicité du login ---
            from models import User
            from app import db

            if User.query.filter_by(login=login).first():
                flash('Ce pseudo est déjà pris, choisis-en un autre.', 'error')
                return render_template('register.html', form=form)

            # --- Création du compte ---
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

            # Message volontairement générique — on ne précise pas si c'est
            # le login ou le mot de passe qui est faux (sécurité)
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
    # Quiz home — stub, sera remplacé à l'étape 5
    # -----------------------------------------------------------------------

    @app.route('/quiz')
    @login_required
    def quiz_home():
        return f'<h1>Bonjour {current_user.login} !</h1><a href="/logout">Déconnexion</a>'