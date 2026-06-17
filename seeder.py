from app.main import create_app
from app.extensions import db
from app.models.user import Karyawan, User

app = create_app()

def jalankan_seeder():
    with app.app_context():
        # Struktur data statis mencakup empat profil untuk menguji sistem kontrol akses
        data_awal = [
            {
                "nip": "ADM001",
                "nama": "Super Administrator",
                "divisi": "IT",
                "jabatan": "System Administrator",
                "username": "admin_it", 
                "role": "admin",
                "password": "admin123"
            },
            {
                "nip": "HRD001",
                "nama": "Administrator SDM",
                "divisi": "Human Resources",
                "jabatan": "HR Manager",
                "username": "hrd_utama",
                "role": "hrd",
                "password": "hrd123"
            },
            {
                "nip": "MGR001",
                "nama": "Manajer Operasional",
                "divisi": "Operasional",
                "jabatan": "General Manager",
                "username": "mgr_ops",
                "role": "manajer",
                "password": "manajer123"
            },
            {
                "nip": "KRY001",
                "nama": "Staf Eksekutif",
                "divisi": "Operasional",
                "jabatan": "Staf Senior",
                "username": "kry_staf",
                "role": "karyawan",
                "password": "karyawan123"
            }
        ]

        entitas_baru = 0
        
        for data in data_awal:
            # Validasi mencegah bentrok kunci primer
            if not Karyawan.query.filter_by(nip=data['nip']).first():
                # Pembuatan profil fisik
                karyawan = Karyawan(
                    nip=data['nip'],
                    nama=data['nama'],
                    divisi=data['divisi'],
                    jabatan=data['jabatan']
                )
                db.session.add(karyawan)
                
                # Pembuatan kredensial sistem dengan atribut lengkap
                user = User(
                    nip=data['nip'],
                    username=data['username'],
                    role=data['role']
                )
                user.set_password(data['password'])
                db.session.add(user)
                
                entitas_baru += 1
                print(f"Mempersiapkan entitas: {data['nip']} dengan akses {data['role'].upper()}")
            else:
                print(f"Abaikan: Entitas {data['nip']} sudah beroperasi di pangkalan data.")
        
        # Eksekusi komit massal
        if entitas_baru > 0:
            try:
                db.session.commit()
                print(f"Transaksi selesai. {entitas_baru} profil berhasil disuntikkan secara permanen.")
            except Exception as e:
                db.session.rollback()
                print(f"Kegagalan sistem saat melakukan komit: {str(e)}")
        else:
            print("Operasi dibatalkan. Tidak ada data baru yang membutuhkan injeksi.")

if __name__ == '__main__':
    jalankan_seeder()