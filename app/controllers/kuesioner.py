from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.controllers.auth import role_required
from app.extensions import db
from app.models.user import Karyawan
from app.models.kuesioner import Periode, Pemetaan, TemplateKuesioner, DetailEvaluasi
from app.services.kalkulasi import hitung_skor_360

kuesioner_bp = Blueprint('kuesioner', __name__)

def get_active_periode():
    """Mengambil periode penilaian aktif, jika belum ada buat default."""
    periode = Periode.query.filter_by(is_active=True).first()
    if not periode:
        periode = Periode(
            nama_periode="Periode Evaluasi BUMN 2026",
            tanggal_mulai=datetime.today().date(),
            tanggal_selesai=datetime.today().date(),
            is_active=True
        )
        db.session.add(periode)
        db.session.commit()
    return periode

@kuesioner_bp.route('/dashboard')
@login_required
def dashboard():
    """Merender halaman dasbor kondisional berdasarkan peran sesi saat ini."""
    return render_template('dashboard.html')

@kuesioner_bp.route('/api/dashboard/summary')
@login_required
def dashboard_summary():
    """Mengembalikan metrik ringkasan untuk grafik dasbor."""
    periode = get_active_periode()
    
    if current_user.role in ['hrd', 'manajer']:
        total_karyawan = Karyawan.query.count()
        total_kuesioner = Pemetaan.query.filter_by(periode_id=periode.id).count()
        completed_kuesioner = Pemetaan.query.filter_by(periode_id=periode.id, status_pengerjaan=True).count()
        
        avg_progress = int((completed_kuesioner / total_kuesioner) * 100) if total_kuesioner > 0 else 0
        
        # Ambil daftar bawahan langsung atau semua karyawan jika HRD
        if current_user.role == 'hrd':
            karyawan_list = Karyawan.query.all()
        else:
            # Manajer: ambil karyawan di mana manajer terdaftar sebagai evaluator 'atasan'
            karyawan_list = Karyawan.query.join(Pemetaan, Karyawan.nip == Pemetaan.target_nip).filter(
                Pemetaan.evaluator_nip == current_user.nip,
                Pemetaan.periode_id == periode.id
            ).all()
            karyawan_list = list(set(karyawan_list))
            
        subordinates = []
        for emp in karyawan_list:
            total_maps = Pemetaan.query.filter_by(target_nip=emp.nip, periode_id=periode.id).count()
            completed_maps = Pemetaan.query.filter_by(target_nip=emp.nip, periode_id=periode.id, status_pengerjaan=True).count()
            is_complete = (completed_maps == total_maps) if total_maps > 0 else False
            subordinates.append({
                "nip": emp.nip,
                "nama": emp.nama,
                "divisi": emp.divisi,
                "complete": is_complete
            })
            
        # Pemantauan progress divisi
        divisions_dict = {}
        all_emp = Karyawan.query.all()
        for emp in all_emp:
            if emp.divisi not in divisions_dict:
                divisions_dict[emp.divisi] = []
            divisions_dict[emp.divisi].append(emp.nip)
            
        divisions = []
        for div_name, nips in divisions_dict.items():
            if not div_name:
                continue
            total_d = Pemetaan.query.filter(Pemetaan.target_nip.in_(nips), Pemetaan.periode_id == periode.id).count()
            completed_d = Pemetaan.query.filter(Pemetaan.target_nip.in_(nips), Pemetaan.periode_id == periode.id, Pemetaan.status_pengerjaan == True).count()
            percentage = int((completed_d / total_d) * 100) if total_d > 0 else 0
            divisions.append({
                "name": div_name,
                "percentage": percentage
            })
            
        return jsonify({
            "total_karyawan": total_karyawan,
            "total_kuesioner": total_kuesioner,
            "avg_progress": avg_progress,
            "subordinates": subordinates,
            "divisions": divisions
        }), 200
    else:
        # Karyawan biasa: Tampilkan daftar tugas kuesioner yang harus diisi
        tasks = Pemetaan.query.filter_by(evaluator_nip=current_user.nip, periode_id=periode.id).all()
        tasks_data = []
        pending_count = 0
        completed_count = 0
        
        for t in tasks:
            target_k = Karyawan.query.filter_by(nip=t.target_nip).first()
            if not target_k:
                continue
            if t.status_pengerjaan:
                completed_count += 1
            else:
                pending_count += 1
                
            tasks_data.append({
                "id": t.id,
                "target_nama": target_k.nama,
                "hubungan": t.peran_evaluator.upper(),
                "deadline": periode.tanggal_selesai.strftime('%d-%m-%Y') if periode.tanggal_selesai else "TBA",
                "status": "Selesai" if t.status_pengerjaan else "Proses"
            })
            
        return jsonify({
            "pending_count": pending_count,
            "completed_count": completed_count,
            "tasks": tasks_data
        }), 200

@kuesioner_bp.route('/master-kuesioner', methods=['GET'])
@login_required
@role_required('hrd')
def index_master_kuesioner():
    """Merender halaman manajemen bank soal AKHLAK."""
    return render_template('master_kuesioner.html')

@kuesioner_bp.route('/api/master-kuesioner', methods=['GET'])
@login_required
@role_required('hrd')
def api_master_kuesioner_list():
    """Mengambil seluruh indikator perilaku AKHLAK."""
    templates = TemplateKuesioner.query.filter_by(is_active=True).all()
    result = []
    for t in templates:
        result.append({
            "id": t.id,
            "pilar": t.pilar_akhlak,
            "teks_indikator": t.teks_pertanyaan
        })
    return jsonify(result), 200

@kuesioner_bp.route('/api/master-kuesioner', methods=['POST'])
@login_required
@role_required('hrd')
def api_master_kuesioner_create():
    """Menambahkan indikator perilaku baru ke bank soal."""
    data = request.get_json()
    pilar = data.get('pilar', '').strip()
    teks = data.get('teks_indikator', '').strip()
    
    if not pilar or not teks:
        return jsonify({"success": False, "message": "Pilar dan teks indikator wajib diisi."}), 400
    
    try:
        new_q = TemplateKuesioner(
            pilar_akhlak=pilar,
            teks_pertanyaan=teks,
            is_active=True
        )
        db.session.add(new_q)
        db.session.commit()
        return jsonify({"success": True, "message": "Indikator berhasil ditambahkan."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@kuesioner_bp.route('/api/master-kuesioner/<int:q_id>', methods=['PUT'])
@login_required
@role_required('hrd')
def api_master_kuesioner_update(q_id):
    """Memperbarui redaksi indikator perilaku."""
    question = TemplateKuesioner.query.get(q_id)
    if not question:
        return jsonify({"success": False, "message": "Indikator tidak ditemukan."}), 404
    
    data = request.get_json()
    try:
        question.pilar_akhlak = data.get('pilar', question.pilar_akhlak)
        question.teks_pertanyaan = data.get('teks_indikator', question.teks_pertanyaan)
        db.session.commit()
        return jsonify({"success": True, "message": "Indikator berhasil diperbarui."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@kuesioner_bp.route('/api/master-kuesioner/<int:q_id>', methods=['DELETE'])
@login_required
@role_required('hrd')
def api_master_kuesioner_delete(q_id):
    """Menghapus indikator perilaku (soft-delete via is_active=False)."""
    question = TemplateKuesioner.query.get(q_id)
    if not question:
        return jsonify({"success": False, "message": "Indikator tidak ditemukan."}), 404
    
    try:
        question.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Indikator berhasil dihapus."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@kuesioner_bp.route('/pemetaan', methods=['GET'])
@login_required
@role_required('hrd', 'manajer')
def index_pemetaan():
    """Merender halaman pemetaan relasi evaluator."""
    return render_template('pemetaan.html')

@kuesioner_bp.route('/api/pemetaan/status', methods=['GET'])
@login_required
@role_required('hrd', 'manajer')
def api_pemetaan_status():
    """Mengambil status pemetaan relasi untuk seluruh karyawan."""
    periode = get_active_periode()
    karyawan_list = Karyawan.query.all()
    
    status_pemetaan = []
    for k in karyawan_list:
        pemetaan_count = Pemetaan.query.filter_by(target_nip=k.nip, periode_id=periode.id).count()
        is_complete = pemetaan_count > 0
        status_pemetaan.append({
            "nip": k.nip,
            "nama": k.nama,
            "divisi": k.divisi,
            "is_complete": is_complete
        })
        
    return jsonify({
        "karyawan": [{"nip": k.nip, "nama": k.nama, "jabatan": k.jabatan} for k in karyawan_list],
        "status_pemetaan": status_pemetaan
    }), 200

@kuesioner_bp.route('/api/pemetaan/<nipTarget>', methods=['GET'])
@login_required
@role_required('hrd', 'manajer')
def api_pemetaan_detail(nipTarget):
    """Mengambil rincian evaluator terpetakan untuk karyawan tertentu."""
    periode = get_active_periode()
    mappings = Pemetaan.query.filter_by(target_nip=nipTarget, periode_id=periode.id).all()
    
    result = {
        "atasan": [],
        "sejawat": [],
        "bawahan": []
    }
    for m in mappings:
        role = m.peran_evaluator.lower()
        evaluator = Karyawan.query.filter_by(nip=m.evaluator_nip).first()
        if evaluator and role in result:
            result[role].append({
                "nip": evaluator.nip,
                "nama": evaluator.nama
            })
    return jsonify({"mapping": result}), 200

@kuesioner_bp.route('/api/pemetaan/<nipTarget>', methods=['POST'])
@login_required
@role_required('hrd', 'manajer')
def api_pemetaan_save(nipTarget):
    """Menyimpan konfigurasi relasi pemetaan evaluator baru."""
    periode = get_active_periode()
    data = request.get_json()
    
    # Hapus konfigurasi lama untuk target ini pada periode aktif
    Pemetaan.query.filter_by(target_nip=nipTarget, periode_id=periode.id).delete()
    
    try:
        for role in ['atasan', 'sejawat', 'bawahan']:
            evaluators = data.get(role, [])
            for ev in evaluators:
                nip_ev = ev.get('nip')
                if not nip_ev:
                    continue
                new_map = Pemetaan(
                    periode_id=periode.id,
                    target_nip=nipTarget,
                    evaluator_nip=nip_ev,
                    peran_evaluator=role,
                    status_pengerjaan=False
                )
                db.session.add(new_map)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@kuesioner_bp.route('/kuesioner', methods=['GET'])
@login_required
def index_kuesioner_redirect():
    """Mengalihkan pemanggilan menu kuesioner utama ke dasbor."""
    return redirect(url_for('kuesioner.dashboard'))

@kuesioner_bp.route('/kuesioner/isi/<int:task_id>', methods=['GET'])
@login_required
def fill_kuesioner(task_id):
    """Merender halaman pengisian kuesioner evaluasi."""
    return render_template('kuesioner.html', task_id=task_id)

@kuesioner_bp.route('/api/kuesioner/tugas/<int:task_id>', methods=['GET'])
@login_required
def api_kuesioner_task(task_id):
    """Membaca data instrumen soal AKHLAK dan detail target evaluasi."""
    pemetaan = Pemetaan.query.get(task_id)
    if not pemetaan:
        return jsonify({"message": "Tugas evaluasi tidak ditemukan."}), 404
        
    target = Karyawan.query.filter_by(nip=pemetaan.target_nip).first()
    if not target:
        return jsonify({"message": "Karyawan target tidak ditemukan."}), 404
        
    # Ambil soal-soal kuesioner aktif dari template
    templates = TemplateKuesioner.query.filter_by(is_active=True).all()
    
    # Jika tabel template kosong, buatkan bank soal default agar aplikasi tidak error
    if not templates:
        default_soal = [
            ("Amanah", "Memenuhi janji dan komitmen kerja secara konsisten."),
            ("Amanah", "Bertanggung jawab atas setiap tindakan dan keputusan yang diambil."),
            ("Kompeten", "Terus meningkatkan kapabilitas diri untuk menjawab tantangan."),
            ("Kompeten", "Menyelesaikan setiap penugasan dengan kualitas terbaik."),
            ("Harmonis", "Menghargai setiap orang terlepas dari latar belakangnya."),
            ("Harmonis", "Membangun lingkungan kerja yang kondusif dan saling mendukung."),
            ("Loyal", "Menjaga nama baik sesama karyawan, pimpinan, dan instansi."),
            ("Loyal", "Rela berkorban untuk kepentingan yang lebih besar."),
            ("Adaptif", "Cepat menyesuaikan diri untuk menghadapi perubahan."),
            ("Adaptif", "Terus menerus melakukan inovasi dan perbaikan."),
            ("Kolaboratif", "Memberi kesempatan kepada berbagai pihak untuk berkontribusi."),
            ("Kolaboratif", "Bekerja sama untuk menghasilkan nilai tambah bersama.")
        ]
        for pilar, teks in default_soal:
            t = TemplateKuesioner(pilar_akhlak=pilar, teks_pertanyaan=teks, is_active=True)
            db.session.add(t)
        db.session.commit()
        templates = TemplateKuesioner.query.filter_by(is_active=True).all()
        
    categories_dict = {}
    for t in templates:
        pilar = t.pilar_akhlak
        if pilar not in categories_dict:
            categories_dict[pilar] = {
                "nama": pilar,
                "deskripsi": f"Panduan nilai utama kompetensi {pilar}.",
                "pertanyaan": []
            }
        categories_dict[pilar]["pertanyaan"].append({
            "id": t.id,
            "teks": t.teks_pertanyaan
        })
        
    return jsonify({
        "target_nama": target.nama,
        "peran_evaluasi": pemetaan.peran_evaluator.upper(),
        "kategori_akhlak": list(categories_dict.values())
    }), 200

@kuesioner_bp.route('/api/kuesioner/submit', methods=['POST'])
@login_required
def api_kuesioner_submit():
    """Menerima submit jawaban kuesioner dan menyimpan skor evaluasi."""
    data = request.get_json()
    task_id = data.get('tugas_id')
    jawaban = data.get('jawaban', [])
    
    pemetaan = Pemetaan.query.get(task_id)
    if not pemetaan:
        return jsonify({"success": False, "message": "Tugas evaluasi tidak ditemukan."}), 404
        
    # --- LAPISAN KEAMANAN IDOR ---
    # Memastikan pengguna yang meminta eksekusi adalah pemilik sah dari mandat evaluasi ini
    if pemetaan.evaluator_nip != current_user.nip:
        return jsonify({
            "success": False, 
            "message": "Pelanggaran Otorisasi: Anda tidak memiliki hak untuk mengeksekusi tugas evaluasi ini."
        }), 403
    # ----------------------------------------
        
    try:
        for j in jawaban:
            q_id = j.get('pertanyaan_id')
            skor = j.get('skor')
            
            detail = DetailEvaluasi.query.filter_by(pemetaan_id=pemetaan.id, kuesioner_id=q_id).first()
            if detail:
                detail.skor = skor
            else:
                detail = DetailEvaluasi(
                    pemetaan_id=pemetaan.id,
                    kuesioner_id=q_id,
                    skor=skor
                )
                db.session.add(detail)
                
        pemetaan.status_pengerjaan = True
        pemetaan.tanggal_submit = datetime.now()
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
@kuesioner_bp.route('/api/hasil/<nip>', methods=['GET'])
@login_required
@role_required('hrd', 'manajer')
def api_hasil_evaluasi(nip):
    """
    Menghitung dan mengembalikan skor akhir 360 derajat karyawan.
    Hanya dapat diakses oleh manajer dan departemen SDM.
    """
    # Validasi integritas data target terlebih dahulu
    target = Karyawan.query.filter_by(nip=nip).first()
    if not target:
        return jsonify({
            "success": False, 
            "message": "Operasi dibatalkan. Karyawan target tidak ditemukan di dalam sistem."
        }), 404

    # Ambil konteks periode yang sedang berjalan
    periode = get_active_periode()
    
    try:
        # Pendelegasian komputasi ke lapisan service
        skor_akhir = hitung_skor_360(nip, periode.id)
        
        return jsonify({
            "success": True,
            "target_nip": nip,
            "target_nama": target.nama,
            "periode_id": periode.id,
            "skor_akhir": skor_akhir
        }), 200
        
    except Exception as e:
        # Penanganan galat internal untuk mencegah server berhenti (Reliability)
        return jsonify({
            "success": False,
            "message": f"Kegagalan mesin kalkulasi internal: {str(e)}"
        }), 500
