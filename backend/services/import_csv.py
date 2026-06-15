import csv
import io
from app.extensions import db
from app.models.user import Karyawan, User
from werkzeug.security import generate_password_hash

def proses_impor_karyawan(file_obj):
    """
    Mengeksekusi pembacaan CSV dan injeksi data massal.
    Mengembalikan tuple: (status_boolean, pesan_atau_jumlah_baris)
    """
    try:
        # Dekode aliran biner menjadi teks
        stream = io.StringIO(file_obj.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        # Validasi integritas struktur kolom
        kolom_wajib = {'nip', 'nama', 'jabatan', 'divisi'}
        if not kolom_wajib.issubset(set(reader.fieldnames)):
            return False, "Struktur kolom CSV tidak sesuai. Pastikan terdapat nip, nama, jabatan, dan divisi."

        karyawan_baru = []
        user_baru = []
        
        # Mengambil seluruh NIP eksisting ke dalam memori set untuk pencarian O(1)
        nip_eksisting = {k.nip for k in Karyawan.query.with_entities(Karyawan.nip).all()}
        
        # Generate hash kata sandi bawaan hanya satu kali di luar perulangan untuk efisiensi CPU
        sandi_bawaan = "Energi2026!"
        sandi_hash = generate_password_hash(sandi_bawaan)
        
        baris_diproses = 0

        for row in reader:
            nip = str(row['nip']).strip()
            
            # Logika pencegahan duplikasi data
            if not nip or nip in nip_eksisting:
                continue

            # Konstruksi objek entitas Karyawan
            karyawan = Karyawan(
                nip=nip,
                nama=str(row['nama']).strip(),
                jabatan=str(row['jabatan']).strip(),
                divisi=str(row['divisi']).strip()
            )
            
            # Konstruksi objek entitas User yang berelasi
            user = User(
                nip=nip,
                username=nip,
                password_hash=sandi_hash,
                role='karyawan' # Peran bawaan
            )
            
            karyawan_baru.append(karyawan)
            user_baru.append(user)
            nip_eksisting.add(nip)
            baris_diproses += 1

        if baris_diproses > 0:
            # Transaksi Data Massal dengan sifat ACID
            db.session.add_all(karyawan_baru)
            db.session.flush() # Menyinkronkan ID dan relasi sebelum commit final
            db.session.add_all(user_baru)
            db.session.commit()
            
            return True, baris_diproses
            
        return True, 0

    except Exception as e:
        db.session.rollback()
        return False, f"Galat pemrosesan data: {str(e)}"