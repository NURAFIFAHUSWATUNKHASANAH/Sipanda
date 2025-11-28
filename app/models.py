from app import db,bcrypt
from datetime import date, datetime
from enum import Enum
import uuid

class StatusEnum(Enum):
    sedang_di_proses = "sedang_di_proses"
    selesai_di_proses = "selesai_di_proses"

class RoleEnum(Enum):
    user = "user"
    pihak_berwajib = "pihak_berwajib"
    super_admin = "super_admin"

#=============================================================================================================================================================
###### REGISTER, LOGIN, PROFIL ######
#=============================================================================================================================================================

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    nama = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=True)
    no_telp = db.Column(db.String(20), unique=True)
    img_profil = db.Column(db.String(255), nullable=True)
    banner_profil = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.user)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  
    deleted_at = db.Column(db.DateTime, nullable=True)
    def tojson(self):
        return {
            "id": self.id,
            "nama": self.nama,
            
        }
    
    # Relasi ke AkunBalai (One-to-One)
    akun_balai = db.relationship('AkunBalai', back_populates='user', uselist=False, cascade="all, delete")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    def __repr__(self):
        return f"User('{self.email}', '{self.nama}','{self.role}')"

#=============================================================================================================================================================
######  ######
#=============================================================================================================================================================

class cobabalai(db.Model):
    __tablename__ = 'cobabalai'
    id = db.Column(db.Integer, primary_key=True)
    nama_balai = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    alamat = db.Column(db.Text)
    kontak = db.Column(db.String(100))

# class UserBalai(db.Model):
#     __tablename__ = 'user_balai'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     id_balaikonservasi = db.Column(db.String(3), db.ForeignKey('balaikonservasi.id_balaikonservasi'), nullable=False)
#     nama_pengguna = db.Column(db.String(100), unique=True, nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     nomor_hp = db.Column(db.String(15), nullable=False)
#     alamat = db.Column(db.Text, nullable=False)
#     provinsi = db.Column(db.String(100), nullable=False)
#     kabupaten = db.Column(db.String(100), nullable=False)
#     created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

#     # Relationship with the Balaikonservasi model (assuming you have this model)
#     balaikonservasi = db.relationship('Balaikonservasi', backref='users', lazy=True)

#     def __repr__(self):
#         return f'<UserBalai {self.nama_pengguna}>'

# Definisikan model Balaikonservasi

# Definisikan model UserBalai
# class UserBalai(db.Model):
#     __tablename__ = 'user_balai'

#     id = db.Column(db.Integer, primary_key=True)
#     balai_id = db.Column(db.String(3), db.ForeignKey('balaikonservasi.id_balaikonservasi'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     nama_pengguna = db.Column(db.String(100), unique=True, nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     nomor_hp = db.Column(db.String(15), nullable=False)
#     alamat = db.Column(db.Text, nullable=False)
#     provinsi = db.Column(db.String(100), nullable=False)
#     kabupaten = db.Column(db.String(100), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     # Relasi ke Balaikonservasi
#     balai = db.relationship('BalaiKonservasi', backref='user_balai', lazy=True)

#     # Relasi ke User
#     user = db.relationship('User', backref='user_balai', lazy=True)

#     def __repr__(self):
#         return f'<UserBalai {self.nama_pengguna} - {self.balai_id}>'

from app import db
from werkzeug.security import generate_password_hash

# class AkunBalai(db.Model):
#     __tablename__ = 'akun_balai'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
#     nama = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     no_telp = db.Column(db.String(20), nullable=False)
#     password = db.Column(db.String(255), nullable=False)  # Disimpan dalam format hash
#     img_profil = db.Column(db.String(255), default=None)
#     role = db.Column(db.String(20), default='pihak_berwajib', nullable=False)
#     alamat = db.Column(db.String(255), nullable=False)
#     kabupaten = db.Column(db.String(100), nullable=False)
#     provinsi = db.Column(db.String(100), nullable=False)
#     created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

#     def __init__(self, user_id, nama, email, no_telp, password, alamat, kabupaten, provinsi, img_profil=None, role='pihak_berwajib'):
#         self.user_id = user_id
#         self.nama = nama
#         self.email = email
#         self.no_telp = no_telp
#         self.password = generate_password_hash(password)
#         self.img_profil = img_profil
#         self.alamat = alamat
#         self.kabupaten = kabupaten
#         self.provinsi = provinsi
#         self.role = role  # <-- Tambahkan ini


class AkunBalai(db.Model):
    __tablename__ = 'akun_balai'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    no_telp = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Gunakan password yang sama dengan User
    alamat = db.Column(db.String(255), nullable=False)
    kabupaten = db.Column(db.String(100), nullable=False)
    provinsi = db.Column(db.String(100), nullable=False)
    img_profil = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='pihak_berwajib', nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='akun_balai')


class HewanModel(db.Model):
    __tablename__ = 'hewan'
    id_hewan = db.Column(db.String(3), primary_key=True, default=lambda: str(uuid.uuid4())[:3])
    nama = db.Column(db.String(255), nullable=True)
    nama_latin = db.Column(db.String(255), nullable=True)
    deskripsi = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    populasi = db.Column(db.Integer, nullable=True)
    habitat = db.Column(db.String(255), nullable=True)
    url_gambar = db.Column(db.String(255), nullable=True)
    id_kategori = db.Column(db.String(1), db.ForeignKey('kategori.id_kategori'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    kategori = db.relationship("Kategori", back_populates="hewan")
    ciri_ciri = db.relationship("CiriCiriModel", back_populates="hewan", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id_hewan,
            "nama": self.nama,
            "nama_latin": self.nama_latin,
            "deskripsi": self.deskripsi,
            "status": self.status,
            "populasi": self.populasi,
            "habitat": self.habitat,
            "url_gambar": self.url_gambar,
            "kategori": self.kategori.to_dict() if self.kategori else None,
            "ciri_ciri": [ciri.to_dict() for ciri in self.ciri_ciri]  
        }

class CiriCiriModel(db.Model):
    __tablename__ = 'ciri_ciri'
    id_ciri =  db.Column(db.String(3), primary_key=True, default=lambda: str(uuid.uuid4())[:3])
    id_hewan = db.Column(db.String(3), db.ForeignKey('hewan.id_hewan'), nullable=False)
    ciri = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    hewan = db.relationship("HewanModel", back_populates="ciri_ciri")
    
    def to_dict(self):
        return {
            "id_ciri": self.id_ciri,
            "id_hewan": self.id_hewan,
            "ciri": self.ciri,
        }

# class gambarBukti(db.Model):
#     __tablename__ = 'gambar_bukti'
#     id_bukti =  db.Column(db.String(3), primary_key=True, default=lambda: str(uuid.uuid4())[:3])
#     id_laporan = db.Column(db.String(3), db.ForeignKey('lapor.id'), nullable=False)
#     nama = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     deleted_at = db.Column(db.DateTime, nullable=True)
#     lapor = db.relationship("Lapor", back_populates="gambar_bukti")

    # def to_dict(self):
    #     return {
    #         "id_ciri": self.id_ciri,
    #         "id_hewan": self.id_hewan,
    #         "ciri": self.ciri,
    #     }


class BalaiKonservasi(db.Model):
    __tablename__ = 'balaikonservasi'
    id_balaikonservasi = db.Column(db.String(3), primary_key=True,default=lambda: str(uuid.uuid4())[:3])
    nama_balai =db.Column(db.String(255), nullable=True)
    deskripsi =db.Column(db.String(255), nullable=True)
    provinsi =db.Column(db.String(255), nullable=True)
    gambarbalai =db.Column(db.String(255), nullable=True)
    alamat =db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    call_center = db.Column(db.String(50), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def ubahJson(self):
        return {
            "id_balaikonservasi": self.id_balaikonservasi,
            "nama_balai": self.nama_balai,
            "deskripsi": self.deskripsi,
            "provinsi": self.provinsi,
            "gambarbalai": self.gambarbalai,
            "alamat": self.alamat,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "call_center": self.call_center
           
        }
class Kategori(db.Model):
    __tablename__ = 'kategori'
    id_kategori = db.Column(db.String(3), primary_key=True, default=lambda: str(uuid.uuid4())[:3])
    nama_kategori = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  
    deleted_at = db.Column(db.DateTime, nullable=True)
    def to_dict(self):
        return {
            "id_kategori": self.id_kategori,
            "nama_kategori": self.nama_kategori
        }
    hewan = db.relationship("HewanModel", back_populates="kategori")


class gambarBukti(db.Model):
    __tablename__ = 'gambar_bukti'
    id_bukti =  db.Column(db.String(3), primary_key=True, default=lambda: str(uuid.uuid4())[:3])
    id_laporan = db.Column(db.String(3), db.ForeignKey('lapor.id'), nullable=False)
    nama = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    lapor = db.relationship("Lapor", back_populates="gambar_bukti")
#====================================================================================================================

class Lapor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nama_lapor = db.Column(db.String(255), nullable=False)
    nomer_hp = db.Column(db.String(15), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    maps = db.Column(db.String(255), nullable=False)
    keterangan = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum("verifikasi", "sedang_di_proses", "selesai_di_proses", "tidak_valid"),
        nullable=False,
        default="verifikasi",
    )
    file_url = db.Column(db.String(255), nullable=True)  
    # bukti_penindakan = db.Column(db.String(255), nullable=True)  # Kolom baru untuk menyimpan gambar bukti
    gambar_bukti = db.relationship("gambarBukti", back_populates="lapor", cascade="all, delete-orphan")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relasi ke User
    user = db.relationship('User', backref=db.backref('laporan', lazy=True))

    def update_status(self, status_baru):
        if status_baru not in ["verifikasi", "sedang_di_proses", "selesai_di_proses", "tidak_valid"]:
            raise ValueError("Invalid status value")
        self.status = status_baru

#====================================================================================================================
# class Lapor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nama_lapor = db.Column(db.String(255), nullable=False)
#     nomer_hp = db.Column(db.String(15), nullable=False)
#     alamat = db.Column(db.Text, nullable=False)
#     maps = db.Column(db.String(255), nullable=False)
#     keterangan = db.Column(db.Text, nullable=False)
#     status = db.Column(db.Enum("verifikasi", "sedang_di_proses", "selesai_di_proses", "tidak_valid"), 
#                        nullable=False, default="verifikasi")
#     file_url = db.Column(db.String(255), nullable=True)  # Kolom baru untuk URL gambar
#     gambar_bukti = db.relationship("gambarBukti", back_populates="lapor", cascade="all, delete-orphan")
#     def update_status(self, status_baru):
#         if status_baru not in ["verifikasi", "sedang_di_proses", "selesai_di_proses", "tidak_valid"]:
#             raise ValueError("Invalid status value")
#         self.status = status_baru

    def to_dict(self):
        return {
            "id": self.id,
            "nama_lapor": self.nama_lapor,
            "nomer_hp": self.nomer_hp,
            "alamat": self.alamat,
            "maps": self.maps,
            "keterangan": self.keterangan,
            "status": self.status.value,
            "file_url": self.file_url, 
        }
    
class Berita(db.Model):
    __tablename__ = 'berita'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    judul = db.Column(db.String(255), nullable=False)
    tanggal = db.Column(db.Date, nullable=False, default=date.today)
    konten = db.Column(db.Text, nullable=False)
    gambar = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Berita {self.id} - {self.judul}>"

    def to_dict(self):
        return {
            "id": self.id,
            "judul": self.judul,
            "tanggal": self.tanggal.strftime('%Y-%m-%d') if self.tanggal else None,
            "konten": self.konten,
            "gambar": self.gambar
        }
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    sentiment = db.Column(db.String(10), nullable=False)
    

from app import db

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)

class Jumbotron(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text, nullable=False)

class JumbotronImage(db.Model):
    __tablename__ = 'jumbotron_images'  # pakai nama tabel sesuai di MySQL
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JenisKawasan(db.Model):
    __tablename__ = "jenis_kawasan"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    kawasans = db.relationship("KawasanKonservasi", backref="jenis", lazy=True)


class KawasanKonservasi(db.Model):
    __tablename__ = "kawasan_konservasi"
    id = db.Column(db.Integer, primary_key=True)
    jenis_id = db.Column(db.Integer, db.ForeignKey("jenis_kawasan.id"), nullable=False)
    nama = db.Column(db.String(150), nullable=False)
    foto = db.Column(db.String(255))
    lokasi = db.Column(db.String(255))
    deskripsi = db.Column(db.Text)

class UnitKerja(db.Model):
    __tablename__ = "unit_kerja"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    kabupaten = db.Column(db.String(100), nullable=False)
    telepon = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    kepala_resor = db.Column(db.String(255))
    kode_resor = db.Column(db.String(50))
    peta_lokasi = db.Column(db.Text)                # link google maps/embed
    wilayah_kerja = db.Column(db.String(255))       # contoh: "Kabupaten Semarang, Salatiga"
    status = db.Column(db.Enum('aktif','nonaktif'), default='aktif')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Footer(db.Model):
    __tablename__ = 'footer'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    instagram_link = db.Column(db.String(255))
    twitter_link = db.Column(db.String(255))
    facebook_link = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    company_links = db.Column(db.Text)
    feature_links = db.Column(db.Text)
    copyright_text = db.Column(db.String(255))

class BKSDAProfile(db.Model):
    __tablename__ = 'bksda_profile'
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    telepon = db.Column(db.String(50))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    kepala_balai = db.Column(db.String(255))
    visi = db.Column(db.Text)
    misi = db.Column(db.Text)
    jam_operasional = db.Column(db.Text)
    informasi = db.Column(db.Text)
    gambar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())