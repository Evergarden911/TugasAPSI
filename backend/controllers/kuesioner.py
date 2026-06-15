from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.controllers.auth import role_required

kuesioner_bp = Blueprint('kuesioner', __name__)

@kuesioner_bp.route('/dashboard')
@login_required
def dashboard():
    """Merender halaman dasbor kondisional berdasarkan peran sesi saat ini."""
    return render_template('frontend/dashboard.html')

@kuesioner_bp.route('/api/dashboard/summary')
@login_required
def dashboard_summary():
    """Mengembalikan metrik ringkasan untuk grafik dasbor."""
    # (Di tahap berikutnya, panggil layanan get_dashboard_metrics() di sini)
    # Ini adalah struktur respons awal (Stubbing) untuk memastikan koneksi ke JavaScript berfungsi
    if current_user.role in ['hrd', 'manajer']:
        return jsonify({
            "total_karyawan": 0,
            "total_kuesioner": 0,
            "avg_progress": 0,
            "subordinates": [],
            "divisions": []
        }), 200
    else:
        return jsonify({
            "pending_count": 0,
            "completed_count": 0,
            "tasks": []
        }), 200

@kuesioner_bp.route('/master-kuesioner', methods=['GET'])
@login_required
@role_required('hrd')
def index_master_kuesioner():
    """Merender halaman manajemen bank soal AKHLAK."""
    return render_template('frontend/templates/master_kuesioner.html')