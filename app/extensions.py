from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Inisialisasi objek ekstensi tanpa mengikatnya ke aplikasi tertentu (Unbound Instances)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Konfigurasi Keamanan Otorisasi Sesi Pengguna
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Sila masuk terlebih dahulu untuk mengakses halaman ini.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    """
    Callback wajib untuk Flask-Login yang bertugas memuat entitas pengguna 
    dari basis data berdasarkan ID sesi yang tersimpan di peramban.
    """
    from app.models.user import User
    return User.query.get(int(user_id))