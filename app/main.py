import os

from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_class=Config):
    """Fungsi pabrik untuk merakit dan mengonfigurasi aplikasi Flask."""
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
    )
    app.config.from_object(config_class)

    # Mengikat dan menginisialisasi ekstensi dengan objek aplikasi yang baru dibuat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Registrasi Blueprints (Lapisan Rute/Controllers)
    from app.controllers.auth import auth_bp
    from app.controllers.karyawan import karyawan_bp
    from app.controllers.admin import admin_bp
    from app.controllers.kuesioner import kuesioner_bp

    # Mendaftarkan modul kontroler ke dalam arsitektur aplikasi
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(karyawan_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(kuesioner_bp)

    return app