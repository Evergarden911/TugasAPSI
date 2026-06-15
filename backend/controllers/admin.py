from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.controllers.auth import role_required
from app.services.import_csv import proses_impor_karyawan

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
@login_required
@role_required('admin')
def index_admin():
    return render_template('frontend/templates/admin.html')

@admin_bp.route('/api/admin/import-karyawan', methods=['POST'])
@login_required
@role_required('admin')
def import_csv_karyawan():
    """Menerima unggahan multipart/form-data dan memvalidasi ekstensi berkas."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Tidak ada berkas yang dilampirkan dalam permintaan."}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "Nama berkas kosong."}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "message": "Sistem menolak integritas berkas. Format harus CSV murni."}), 415

    # Mendelegasikan pembacaan data massal ke lapisan Service
    sukses, hasil = proses_impor_karyawan(file)
    
    if sukses:
        return jsonify({"success": True, "rows_inserted": hasil}), 201
    else:
        return jsonify({"success": False, "message": hasil}), 422