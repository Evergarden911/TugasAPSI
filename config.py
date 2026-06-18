import os
from dotenv import load_dotenv

# Menentukan jalur absolut ke direktori akar proyek
basedir = os.path.abspath(os.path.dirname(__file__))
# Memuat variabel lingkungan dari berkas .env yang berada di luar folder app
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # Keamanan: Kunci kriptografi untuk mengamankan data sesi
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-cadangan-pengembangan-bumn-360'
    
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            "GAGAL KRITIS: Variabel DATABASE_URL tidak ditemukan. "
            "Sistem menolak untuk menyala dalam kondisi buta. "
            f"Periksa apakah berkas .env berada di {os.path.dirname(basedir)} dan tidak memiliki ekstensi .txt tersembunyi."
        )
    

    SQLALCHEMY_TRACK_MODIFICATIONS = False