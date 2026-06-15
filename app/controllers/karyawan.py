from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.controllers.auth import role_required
from app.services.user import get_semua_karyawan, tambah_karyawan_satuan, perbarui_karyawan, hapus_karyawan

karyawan_bp = Blueprint('karyawan', __name__)

@karyawan_bp.route('/karyawan', methods=['GET'])
@login_required
@role_required('hrd', 'manajer') # Lapis keamanan RBAC
def index_karyawan():
    """Merender cetakan HTML dasar untuk halaman karyawan."""
    return render_template('karyawan.html')

@karyawan_bp.route('/api/karyawan', methods=['GET', 'POST'])
@login_required
@role_required('hrd')
def api_karyawan_koleksi():
    """Titik akhir API untuk menarik data tabel atau menambah karyawan baru."""
    if request.method == 'GET':
        data = get_semua_karyawan()
        return jsonify(data), 200
    
    if request.method == 'POST':
        data = request.get_json()
        sukses, pesan = tambah_karyawan_satuan(data)
        status_code = 201 if sukses else 400
        return jsonify({"success": sukses, "message": pesan}), status_code

@karyawan_bp.route('/api/karyawan/<nip>', methods=['PUT', 'DELETE'])
@login_required
@role_required('hrd')
def api_karyawan_entitas(nip):
    """Titik akhir API untuk memodifikasi atau menghapus entitas tunggal."""
    if request.method == 'PUT':
        data = request.get_json()
        sukses, pesan = perbarui_karyawan(nip, data)
    elif request.method == 'DELETE':
        sukses, pesan = hapus_karyawan(nip)
        
    status_code = 200 if sukses else 400
    return jsonify({"success": sukses, "message": pesan}), status_code