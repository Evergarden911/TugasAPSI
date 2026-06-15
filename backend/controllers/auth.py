from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    """
    Dekorator kustom untuk mengunci rute berdasarkan peran pengguna.
    Mencegah Karyawan biasa mengakses API atau halaman milik HRD/Admin.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.role not in roles:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({"success": False, "message": "Akses ditolak. Hak otorisasi tidak mencukupi."}), 403
                return redirect(url_for('auth.login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Cegah pengguna yang sudah masuk mengakses halaman login lagi
    if current_user.is_authenticated:
        return redirect(url_for('kuesioner.dashboard'))

    if request.method == 'POST':
        data = request.get_json()
        nip = data.get('nip')
        password = data.get('password')

        user = User.query.filter_by(nip=nip).first()
        
        # Validasi kredensial (Eksekusi fungsi kriptografi dari model)
        if user and user.check_password(password):
            login_user(user, remember=data.get('remember_me', False))
            # Rute tujuan MPA setelah sukses
            return jsonify({"success": True, "redirect_url": "/dashboard"}), 200
        
        # Penundaan respons celah keamanan (menghindari enumerasi akun)
        return jsonify({"success": False, "message": "NIP atau Kata Sandi tidak valid."}), 401
        
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True}), 200