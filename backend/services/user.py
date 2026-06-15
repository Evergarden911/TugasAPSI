from app.extensions import db
from app.models.user import Karyawan, User
from werkzeug.security import generate_password_hash

def get_semua_karyawan():
    """Mengambil daftar seluruh entitas karyawan berserta hak aksesnya."""
    # Menggunakan SQLAlchemy JOIN untuk menggabungkan data profil dan akun
    query = db.session.query(Karyawan, User).join(User, Karyawan.nip == User.nip).all()
    
    hasil = []
    for karyawan, user in query:
        hasil.append({
            'nip': karyawan.nip,
            'nama': karyawan.nama,
            'divisi': karyawan.divisi,
            'jabatan': karyawan.jabatan,
            'role': user.role
        })
    return hasil

def tambah_karyawan_satuan(data):
    """Menambahkan satu karyawan baru berserta pembuatan akun otomatis."""
    nip = data.get('nip', '').strip()
    
    if Karyawan.query.filter_by(nip=nip).first():
        return False, "NIP tersebut sudah terdaftar di dalam sistem."
        
    try:
        karyawan = Karyawan(
            nip=nip,
            nama=data.get('nama', '').strip(),
            divisi=data.get('divisi', '').strip(),
            jabatan=data.get('jabatan', '').strip()
        )
        
        user = User(
            nip=nip,
            username=nip,
            password_hash=generate_password_hash("Energi2026!"),
            role=data.get('role', 'karyawan').strip()
        )
        
        db.session.add(karyawan)
        db.session.add(user)
        db.session.commit()
        return True, "Data berhasil disimpan."
        
    except Exception as e:
        db.session.rollback()
        return False, "Gagal menyimpan data ke basis data."

def perbarui_karyawan(nip, data):
    """Memperbarui informasi profil dan hak akses."""
    karyawan = Karyawan.query.filter_by(nip=nip).first()
    user = User.query.filter_by(nip=nip).first()
    
    if not karyawan or not user:
        return False, "Karyawan tidak ditemukan."
        
    try:
        karyawan.nama = data.get('nama', karyawan.nama)
        karyawan.divisi = data.get('divisi', karyawan.divisi)
        karyawan.jabatan = data.get('jabatan', karyawan.jabatan)
        user.role = data.get('role', user.role)
        
        db.session.commit()
        return True, "Data berhasil diperbarui."
        
    except Exception as e:
        db.session.rollback()
        return False, "Gagal memperbarui data."

def hapus_karyawan(nip):
    """Menghapus data karyawan. Penghapusan akun dan relasi diurus oleh Cascade DB."""
    karyawan = Karyawan.query.filter_by(nip=nip).first()
    if not karyawan:
        return False, "Karyawan tidak ditemukan."
        
    try:
        db.session.delete(karyawan)
        db.session.commit()
        return True, "Data berhasil dihapus."
    except Exception as e:
        db.session.rollback()
        return False, "Gagal menghapus data. Pastikan tidak ada bentrok relasi struktural."