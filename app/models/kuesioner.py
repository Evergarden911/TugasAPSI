from app.extensions import db

class Periode(db.Model):
    __tablename__ = 'periode'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_periode = db.Column(db.String(50), nullable=False)
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    pemetaan_list = db.relationship('Pemetaan', backref='periode', lazy='dynamic')

class TemplateKuesioner(db.Model):
    __tablename__ = 'template_kuesioner'
    
    id = db.Column(db.Integer, primary_key=True)
    pilar_akhlak = db.Column(db.String(50), nullable=False)
    teks_pertanyaan = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Pemetaan(db.Model):
    __tablename__ = 'pemetaan'
    
    id = db.Column(db.Integer, primary_key=True)
    periode_id = db.Column(db.Integer, db.ForeignKey('periode.id', ondelete='RESTRICT'), nullable=False)
    # Merujuk nama tabel 'karyawan' sebagai string, tidak perlu import Karyawan dari user.py
    target_nip = db.Column(db.String(20), db.ForeignKey('karyawan.nip', ondelete='CASCADE'), nullable=False)
    evaluator_nip = db.Column(db.String(20), db.ForeignKey('karyawan.nip', ondelete='CASCADE'), nullable=False)
    peran_evaluator = db.Column(db.String(20), nullable=False)
    status_pengerjaan = db.Column(db.Boolean, default=False)
    tanggal_submit = db.Column(db.DateTime, nullable=True)

    hasil_detail = db.relationship('DetailEvaluasi', backref='pemetaan', lazy='dynamic', cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('periode_id', 'target_nip', 'evaluator_nip', name='uq_pemetaan_periode'),
    )

class DetailEvaluasi(db.Model):
    __tablename__ = 'detail_evaluasi'
    
    id = db.Column(db.Integer, primary_key=True)
    pemetaan_id = db.Column(db.Integer, db.ForeignKey('pemetaan.id', ondelete='CASCADE'), nullable=False)
    kuesioner_id = db.Column(db.Integer, db.ForeignKey('template_kuesioner.id', ondelete='CASCADE'), nullable=False)
    skor = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('pemetaan_id', 'kuesioner_id', name='uq_detail_skor'),
    )