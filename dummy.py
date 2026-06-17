from app.main import create_app
from app.extensions import db
from app.models.user import Karyawan, User
from faker import Faker
import random
import time

app = create_app()
# Menginisialisasi lokalisasi bahasa Indonesia untuk data yang realistis
fake = Faker('id_ID') 

def generate_hierarki_perusahaan(jumlah_target=50):
    with app.app_context():
        divisi_korporat = ['Operasional', 'Keuangan', 'Pemasaran', 'Rantai Pasok', 'Teknologi Informasi']
        entitas_berhasil = 0
        waktu_mulai = time.time()
        
        print(f"Memulai komputasi injeksi untuk {jumlah_target} entitas...")

        for i in range(jumlah_target):
            # Membangun integritas hierarki: 1 Manajer untuk setiap 6 Staf
            if i % 7 == 0:
                jabatan = 'Manajer Divisi'
                role = 'manajer'
                kode_prefix = 'MGR'
            else:
                jabatan = 'Staf Pelaksana'
                role = 'karyawan'
                kode_prefix = 'STF'

            # Menghasilkan pengenal unik untuk mencegah bentrok konstrain (Integrity Error)
            nip_unik = f"{kode_prefix}{fake.unique.random_number(digits=4)}"
            nama_palsu = fake.name()
            divisi_acak = random.choice(divisi_korporat)
            
            # Inisialisasi Model Fisik
            karyawan = Karyawan(
                nip=nip_unik,
                nama=nama_palsu,
                jabatan=jabatan,
                divisi=divisi_acak
            )
            
            user = User(
                nip=nip_unik,
                username=f"{nip_unik.lower()}_{fake.unique.word()}",
                role=role
            )
            user.set_password('rahasia123') # Sandi seragam untuk kemudahan pengujian
            
            # Menumpuk data ke dalam memori sesi (belum dikirim ke SQL)
            db.session.add(karyawan)
            db.session.add(user)
            entitas_berhasil += 1

        try:
            # Mengeksekusi komit massal (Batch Commit) untuk Optimasi Performa I/O
            db.session.commit()
            durasi = round(time.time() - waktu_mulai, 2)
            print(f"Operasi selesai. {entitas_berhasil} profil hierarkis terinjeksi dalam {durasi} detik.")
            print("Gunakan kata sandi 'rahasia123' untuk menguji log masuk entitas buatan ini.")
        except Exception as e:
            db.session.rollback()
            print(f"Kegagalan transaksi basis data: {str(e)}")

if __name__ == '__main__':
    # Anda dapat mengubah angka ini sesuai kebutuhan pengujian beban antarmuka Anda
    generate_hierarki_perusahaan(50)