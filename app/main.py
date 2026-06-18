import os
from flask import Flask, redirect, url_for
from app.config import Config
from app.extensions import db, migrate, login_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
    )
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.controllers.auth import auth_bp
    from app.controllers.karyawan import karyawan_bp
    from app.controllers.admin import admin_bp
    from app.controllers.kuesioner import kuesioner_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(karyawan_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(kuesioner_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login')) 


    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)