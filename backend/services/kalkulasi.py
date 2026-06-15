from app.extensions import db
from app.models.kuesioner import Pemetaan, DetailEvaluasi
from sqlalchemy.sql import func

def hitung_skor_360(target_nip, periode_id):
    """
    Mengalkulasi skor akhir 360 derajat untuk satu karyawan pada periode tertentu.
    Mengembalikan nilai float (0.0 hingga 5.0).
    """
    # Definisi konfigurasi bobot penilaian (Berdasarkan rancangan PDF)
    BOBOT = {
        'atasan': 0.40,
        'bawahan': 0.30,
        'sejawat': 0.20,
        'mandiri': 0.10
    }

    # 1. Menarik semua data pemetaan yang SUDAH SELESAI dikerjakan
    evaluasi_selesai = Pemetaan.query.filter_by(
        target_nip=target_nip,
        periode_id=periode_id,
        status_pengerjaan=True
    ).all()

    if not evaluasi_selesai:
        return 0.0

    # Struktur data untuk mengelompokkan skor mentah
    skor_per_peran = {
        'atasan': [],
        'bawahan': [],
        'sejawat': [],
        'mandiri': []
    }

    # 2. Agregasi Rata-rata per Lembar Evaluasi
    for evaluasi in evaluasi_selesai:
        # Menggunakan fungsi agregasi SQL tingkat peladen (func.avg) untuk performa
        # daripada menarik ribuan baris detail ke memori Python
        rata_rata_kuesioner = db.session.query(func.avg(DetailEvaluasi.skor)).filter(
            DetailEvaluasi.pemetaan_id == evaluasi.id
        ).scalar()

        if rata_rata_kuesioner:
            # Pastikan peran yang tersimpan di DB sesuai dengan kunci dictionary BOBOT
            peran = str(evaluasi.peran_evaluator).lower()
            if peran in skor_per_peran:
                skor_per_peran[peran].append(float(rata_rata_kuesioner))

    # 3. Komputasi Skor Akhir Berdasarkan Bobot
    skor_akhir = 0.0
    bobot_terpenuhi = 0.0

    for peran, daftar_skor in skor_per_peran.items():
        if daftar_skor:
            # Rata-rata gabungan jika ada lebih dari 1 penilai di peran yang sama (misal: 3 sejawat)
            rata_rata_peran = sum(daftar_skor) / len(daftar_skor)
            skor_akhir += rata_rata_peran * BOBOT[peran]
            bobot_terpenuhi += BOBOT[peran]

    # 4. Normalisasi Bobot Dinamis (Pencegahan Edge Case)
    if bobot_terpenuhi == 0:
        return 0.0
        
    # Normalisasi mencegah nilai jatuh jika seorang karyawan tidak memiliki bawahan (bobot 30% hilang)
    skor_akhir_normalisasi = skor_akhir / bobot_terpenuhi

    return round(skor_akhir_normalisasi, 2)
