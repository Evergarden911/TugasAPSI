import os
from dotenv import load_dotenv

# Menentukan jalur absolut ke direktori akar proyek
basedir = os.path.abspath(os.path.dirname(__file__))
# Memuat variabel lingkungan dari berkas .env yang berada di luar folder app
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # Keamanan: Kunci kriptografi untuk mengamankan data sesi dan kuki (cookies)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-cadangan-pengembangan-bumn-360'
    
    # Koneksi Data: Mengambil tautan URI basis data MySQL XAMPP
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'mysql+pymysql://root:@127.0.0.1:3306/db_penilaian_360'
    
    # Performa: Menonaktifkan fitur pelacakan modifikasi objek SQLAlchemy untuk menghemat RAM peladen
    SQLALCHEMY_TRACK_MODIFICATIONS = False