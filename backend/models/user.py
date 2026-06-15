from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Karyawan(db.Model):
    __tablename__ = 'karyawan'
    
    nip = db.Column(db.String(20), primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jabatan = db.Column(db.String(100), nullable=False)
    divisi = db.Column(db.String(100), nullable=False)

    akun = db.relationship('User', backref='data_karyawan', uselist=False, cascade="all, delete-orphan")
    relasi_dinilai = db.relationship('Pemetaan', foreign_keys='Pemetaan.target_nip', backref='target', lazy='dynamic')
    relasi_menilai = db.relationship('Pemetaan', foreign_keys='Pemetaan.evaluator_nip', backref='evaluator', lazy='dynamic')

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(20), db.ForeignKey('karyawan.nip', ondelete='CASCADE'), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='karyawan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)