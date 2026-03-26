from flask import render_template_string

def register_routes(app):

    @app.route('/')
    def index():
        return render_template_string("""
            <h1>OrthoQuizz</h1>
            <p>Étape 1 OK — Flask démarre correctement.</p>
        """)
