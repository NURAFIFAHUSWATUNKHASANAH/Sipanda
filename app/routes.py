import os
import random
import uuid
from flask import jsonify, render_template, request, redirect, url_for, flash, session, Blueprint
from flask_jwt_extended import jwt_required
import jwt
from app import app
from werkzeug.utils import secure_filename
from app.Controllers.LaporController import delete_laporan_by_id, laporApiF, laporF, laporan_page, update_status, cobaUpdate
from app.Controllers.ScanController import deteksi
from app.Controllers.beritaController import BacaDataBerita, delete_berita_by_id, get_news, tambahBerita, updateBerita, detailBerita
from app.Controllers.footerController import footer_index, footer_updateF
from app.Controllers.login_google import google_callbackF, lengkapi_nomorF, require_phone_numberF, verifikasi_nomorF
from app.models import About, BKSDAProfile, Comment, JenisKawasan, Jumbotron, JumbotronImage, KawasanKonservasi, UnitKerja, gambarBukti, Lapor, RoleEnum, User, HewanModel, BalaiKonservasi, Berita
from app.Controllers.Chatbot import chat
from app import google, db
from app.Controllers.authController import data_user, delete_user_by_id, edit_pengguna, hapusakun, loginF, registerF, profilF,bacaUser, registerApi,loginApi, request_reset_password, reset_password,reset_password_api,req_api_pass, role_required, updateProfilApi, verify_emailF
from app.Controllers.Balaikonservasi import BacaDataBalai, BacaDataBalaiApi, deleteBalaiKonservasi, detailBalai, editDatabalais,tambahDataBalai,balai_terdekat,halamanDataBalai, pencarianB
from app.Controllers.HewanController import bacaDataHewan,bacaDataHewanApi, cariDataHewanApi, deleteDataHewan,detailHewans, halamanDataHewan, tambahDataHewan, tambahDataHewanApi, ambilDataDariKategori, updateDataHewan
from app.Controllers.Kategori import buatKategori, bacaData,bacaDataApi, updateData, updateDataApi, deleteDataApi,deleteData
from app.Controllers.sentimenController import tambahKomen,tambahKomenApi
from app.utils import send_wa_otp, simpanGambar
import secrets
from werkzeug.security import generate_password_hash
from flask import flash, redirect, url_for, session, current_app
from flask_mail import Message
from app import db, mail
from app.models import User, RoleEnum  # Sesuaikan dengan modelmu

#=============================================================================================================================================================
###### AUTH ######
#=============================================================================================================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    return registerF()

@app.route('/api/register', methods=['POST'])
def registerApis():
    return registerApi()

@app.route('/api/chatbot', methods=['POST'])
def halamanChatApi():
    return chat()

@app.route('/api/login', methods=[ 'POST'])
def loginApis():
    return loginApi()

@app.route('/login', methods=['GET', 'POST'])
def login():
    return loginF()

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    return profilF()

@app.route('/verify/<token>')
def verify_email(token):
    return verify_emailF(token)

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def google_callback():
    return google_callbackF()

@app.before_request
def require_phone_number():
    return require_phone_numberF()

@app.route('/lengkapi-nomor', methods=['GET', 'POST'])
def lengkapi_nomor():
    return lengkapi_nomorF()

@app.route('/verifikasi-nomor', methods=['GET', 'POST'])
def verifikasi_nomor():
    return verifikasi_nomorF()

#=============================================================================================================================================================

@app.route('/detailberita/<int:id_berita>', methods=['GET'])
def pindahHalamanBerita(id_berita):
    return detailBerita(id=id_berita)

@app.route('/logout')
def logout():
    session.clear()
    flash('Kamu telah logout.', 'success')
    return redirect(url_for('login'))

@app.route('/get_bukti_foto/<int:laporan_id>')
def get_bukti_foto(laporan_id):
    # Ambil data gambar berdasarkan ID laporan
    bukti = gambarBukti.query.filter_by(id_laporan=laporan_id).all()

    if not bukti:
        return jsonify({"success": False, "message": "Gambar tidak ditemukan."})

    # Buat list URL gambar
    urls = [url_for('static', filename='uploads/' + b.nama) for b in bukti]

    return jsonify({"success": True, "bukti": urls})

@app.route('/scan', methods=['GET', 'POST'])
def halamanScan():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file yang dipilih.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nama file kosong.', 'error')
            return redirect(request.url)

        # Simpan file upload
        upload_folder = os.path.join(os.getcwd(), './app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            result = deteksi(file_path)

            # ✅ Jika tidak ada deteksi, tetap tampilkan halaman hasil
            if "detections" not in result or len(result["detections"]) == 0:
                session['result'] = {
                    'image_path': filename,
                    'predicted_label': 'Tidak Terdeteksi',
                    'confidence': None,
                    'species_info': {
                        'status': 'Tidak Ada',
                        'latin_name': '-',
                        'habitat': '-',
                        'description': 'Tidak ada objek satwa yang terdeteksi pada gambar ini.'
                    }
                }
                return redirect(url_for('halamanHasil'))
            
            # ✅ Jika ada hasil deteksi
            detection = result["detections"][0]  
            predicted_label = detection["label"]
            confidence = detection["confidence"]
            species_info = detection["species_info"]

            session['result'] = {
                'image_path': filename,
                'predicted_label': predicted_label,
                'confidence': confidence,
                'species_info': species_info
            }

        except Exception as e:
            flash(f'Error saat prediksi: {str(e)}', 'error')
            return redirect(request.url)

        return redirect(url_for('halamanHasil'))

    return render_template('scan.html')



@app.route('/api/scan', methods=['GET', 'POST'])
def halamanScanApi():
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dipilih.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong.'}), 400

    try:
        # Buat folder untuk menyimpan file jika belum ada
        upload_folder = os.path.join(os.getcwd(), './app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Simpan file dengan nama unik
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Lakukan prediksi
        result = deteksi(file_path)  # Fungsi deteksi harus sudah didefinisikan

        # Format respons JSON
        response = {
            'image_path': f'/static/uploads/{filename}',  # URL untuk akses file
            'predicted_label': result['predicted_label'],
            'confidence': result['confidence'],
            'species_info': result.get('species_info', None)
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': f'Error saat prediksi: {str(e)}'}), 500

@app.route('/api/komen', methods=['POST'])
def apiKomen():
    return tambahKomenApi()
@app.route('/api/hapusAkun/<int:id>', methods=['DELETE'])
def hapusAkunApi(id):
    return hapusakun(id)

@app.route('/hasil')
def halamanHasil():
    result = session.get('result')
    if not result:
        flash('Tidak ada hasil untuk ditampilkan.', 'error')
        return redirect(url_for('halamanScan'))
    file_url =result['image_path']
    return render_template('hasil.html', result=result, file_url=file_url)

@app.route('/detailhewan/<string:id_hewan>', methods=['GET'])
def pindahHalaman(id_hewan):
    hewan = HewanModel.query.filter_by(id_hewan=id_hewan).first()
    
    if hewan is None:
        flash('Hewan tidak ditemukan', 'error')
        return redirect(url_for('halamanDataHewan')) 
    
    url_gambar = url_for('static', filename='gambarUser/' + hewan.url_gambar)
    
    return render_template('DetailHewan.html', hewans=hewan, url_gambar=url_gambar)

@app.route('/detailbalai/<string:id_balaikonservasi>', methods=['GET'])
def pindahHalamanBalai(id_balaikonservasi):
    balai = BalaiKonservasi.query.filter_by(id_balaikonservasi=id_balaikonservasi).first()
    
    if balai is None:
        flash('Balai Konservasi tidak ditemukan', 'error')
        return redirect(url_for('halamanDataBalai'))  
    
    url_gambar = url_for('static', filename='gambarUser/' + balai.gambarbalai)
    
    return render_template('detailbalai.html', balai=balai, url_gambar=url_gambar)


# ===================================================================================================================================
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Lapor
import os

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/lapor', methods=['GET', 'POST'])
def lapor():
    return laporF()

@app.route('/api/lapor', methods=['POST'])
def laporApi():
    return laporApiF()

# =======================================================

@app.route('/')
def home():
    about = About.query.first()  # Ambil About pertama
    jumbotron = Jumbotron.query.first()  # Ambil Jumbotron pertama
    hewans = HewanModel.query.all()
    balais = BalaiKonservasi.query.all()
    kawasans = KawasanKonservasi.query.all()  # ✅ ambil semua data kawasan
    news = get_news()
    images = JumbotronImage.query.all()  # Ambil semua gambar jumbotron
    bksda_profile = BKSDAProfile.query.first() 
    unit_kerja_data = UnitKerja.query.filter_by(status="aktif").all()

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template(
            'home.html', 
            user=user, 
            hewans=hewans, 
            balais=balais, 
            kawasans=kawasans,   # ✅ kirim ke template
            news=news, 
            about=about, 
            jumbotron=jumbotron,
            images=images,
            bksda_profile=bksda_profile,
            unit_kerja_data=unit_kerja_data
        )
    else:
        return render_template(
            'home.html', 
            hewans=hewans, 
            balais=balais, 
            kawasans=kawasans,   # ✅ kirim ke template
            news=news, 
            about=about, 
            jumbotron=jumbotron,
            images=images,
            bksda_profile=bksda_profile,
            unit_kerja_data=unit_kerja_data
        )

@app.route('/admin')
@role_required(['super_admin', 'pihak_berwajib'])
def admin():
    positive_count = Comment.query.filter_by(sentiment="Positive").count()
    negative_count = Comment.query.filter_by(sentiment="Negative").count()

    # Ambil data komentar berdasarkan sentimen
    positive_comments = Comment.query.filter_by(sentiment="Positive").all()
    negative_comments = Comment.query.filter_by(sentiment="Negative").all()

    return render_template(
        './admin/pages/dashboard.html',
        positive=positive_count,
        negative=negative_count,
        positive_comments=positive_comments,
        negative_comments=negative_comments
    )


@app.route('/comment/add', methods=['POST'])
def komenTambah():
    return tambahKomen()
    
#route kategori Api
@app.route('/admin/api/kategori', methods=['GET'])
def kategoriApi():
    return bacaDataApi()
@app.route('/admin/kategori/tambah', methods=['GET','POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def kategoriTambah():
    return buatKategori()
@app.route('/admin/kategori/delete/<string:id_kategori>', methods=['GET','POST','DELETE'])
@role_required(['super_admin', 'pihak_berwajib'])
def hapusKategori(id_kategori):
    return deleteData(id_kategori)
@app.route('/admin/api/kategori/delete/<string:id_kategori>', methods=['DELETE'])
def hapusKategoriApi(id_kategori):
    return deleteDataApi(id_kategori)
@app.route('/admin/kategori/update/<string:id_kategori>', methods=['GET', 'POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def kategoriUpdate(id_kategori):
    return updateData(id_kategori)
@app.route('/admin/api/kategori/update/<string:id_kategori>', methods=['GET', 'PUT'])
def kategoriUpdateApi(id_kategori):
    return updateDataApi(id_kategori)
@app.route('/admin/kategori')
@role_required(['super_admin', 'pihak_berwajib'])
def kategori():
    return bacaData()


#hewan
@app.route('/admin/hewan')
@role_required(['super_admin', 'pihak_berwajib'])
def hewan():
    return bacaDataHewan()
@app.route('/admin/api/hewan/kategori/<string:id_kategori>', methods=["GET"])
def hewanKategori(id_kategori):
    return ambilDataDariKategori(id_kategori)
@app.route('/admin/api/hewan', methods=['GET'])
def hewanApi():
    return bacaDataHewanApi()
@app.route('/admin/hewan/tambah',methods=['GET', 'POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def tambahHewan():
    return tambahDataHewan()
@app.route('/admin/api/hewan/tambah',methods=['POST'])
def tambahHewanApi():
    return tambahDataHewanApi()

@app.route('/admin/hewan/edit/<string:id_hewan>', methods=['GET', 'POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def editHewans(id_hewan):
    return updateDataHewan(id_hewan)

@app.route('/admin/hewan/delete/<string:id_hewan>', methods=['POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def deleteHewan(id_hewan):
    return deleteDataHewan(id_hewan)

@app.route('/admin/hewan/cari', methods=['GET'])
@role_required(['super_admin', 'pihak_berwajib'])
def cari_hewan():
    return cariDataHewanApi()

@app.route('/admin/balaikonservasi')
@role_required(['super_admin', 'pihak_berwajib'])
def balaiKonservasi():
    return BacaDataBalai()

@app.route('/admin/api/balaikonservasi',  methods=['GET'])
def balaiKonservasiApi():
    return BacaDataBalaiApi()

@app.route('/admin/balaikonservasi/tambah', methods=['GET','POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def tambahDatabalais():
    return tambahDataBalai()

@app.route('/admin/balaikonservasi/update/<string:id_balaikonservasi>', methods=['GET', 'POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def editbalai(id_balaikonservasi):
    return editDatabalais(id_balaikonservasi)

@app.route('/admin/balaikonservasi/delete/<string:id_balaikonservasi>', methods=['POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def deletebalai(id_balaikonservasi):
    return deleteBalaiKonservasi(id_balaikonservasi)

@app.route('/admin/api/bacauser', methods=['GET'])
def bcauserapi():
    return bacaUser()
#======================================================================================================================================================
#Laporan
@app.route('/admin/laporan')
@role_required(['super_admin', 'pihak_berwajib'])
def laporan():
    laporan_data = Lapor.query.options(db.joinedload(Lapor.gambar_bukti)).all()
    laporan_proses = Lapor.query.filter_by(status="sedang_di_proses").count()
    laporan_selesai = Lapor.query.filter_by(status="selesai_di_proses").count()

    return render_template('admin/pages/Laporan.html', laporan_data=laporan_data, laporan_proses=laporan_proses, laporan_selesai=laporan_selesai)
#======================================================================================================================================================

@app.route('/admin/laporan/delete/<int:laporan_id>', methods=['POST'])
def delete_laporan(laporan_id):
    return delete_laporan_by_id(laporan_id)

@app.route('/admin/update', methods=['POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def update_status_route():
    return update_status()
@app.route('/update_status', methods=['POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def update_status():
    return cobaUpdate()

@app.route('/reset-password', methods=['GET', 'POST'])
def requestResetPassword():
    return request_reset_password()

@app.route('/reset-password/<string:token>', methods=['GET', 'POST'])
def resetPassword(token):
    return reset_password(token)

@app.route('/cobahalaman', methods=['GET'])
def cobaBalais():
    return render_template('cobabalai.html')

@app.route('/HalamanDataBalai', methods=['GET'])
def dataHalaman():
    return halamanDataBalai()

@app.route('/HalamanDataHewan', methods=['GET'])
def halamanHewan():
    return halamanDataHewan()

@app.route('/api/pencarian/balai', methods=['GET'])
def pencarianDataBalai():
    return pencarianB()

@app.route('/api/pencarian/hewan', methods=['GET'])
def pencarianDataHewan():
    return cariDataHewanApi()

@app.route('/cobabalai', methods=['GET'])
def cobaBalai():
    return pencarianB()

@app.route('/api/token/resetpassword', methods=['POST'])
def mintaToken():
    return req_api_pass()

@app.route('/api/resetpassword', methods=['POST'])
def resetPassApi():
    return reset_password_api()
@app.route('/api/profil/update', methods=['POST'])
def updateProfilRes():
    return updateProfilApi()

@app.route('/api/chatbot/mobile', methods=['POST'])
def ApiChatbotMobile():
    return chat()


#berita
@app.route('/admin/berita', methods=['GET'])
def Berita():
    return BacaDataBerita()
@app.route('/admin/berita/tambah', methods=['GET', 'POST'])
def create_berita():
    return tambahBerita()
@app.route('/admin/berita/update/<int:berita_id>', methods=['GET', 'POST'])
def update_berita(berita_id):
    return updateBerita(berita_id)
@app.route('/admin/berita/delete/<int:berita_id>', methods=['POST'])
def delete_berita(berita_id):
    return delete_berita_by_id(berita_id)

#pengguna
@app.route('/admin/pengguna')
@role_required(['super_admin', 'pihak_berwajib'])
def pengguna():
    return data_user()
@app.route('/admin/pengguna/update/<int:user_id>', methods=['GET', 'POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def editDataPengguna(user_id):
    return edit_pengguna(user_id)
@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@role_required(['super_admin', 'pihak_berwajib'])
def delete_user(user_id):
    return delete_user_by_id(user_id)

@app.route('/chatbot')
def halamanChat():
    return render_template('chat.html')

@app.route('/lapor')
def halamanLapor():
    return render_template('lapor.html')
@app.route('/detail')
def halamanDetail():
    return render_template('detail.html')


# BARUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU

from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User, AkunBalai

# Menampilkan daftar akun balai
@app.route('/akun_balai', methods=['GET'])
def akun_balai():
    akun_balai = AkunBalai.query.all()  # Ambil semua akun balai
    return render_template('admin/pages/UserBalai/index.html', akun_balai=akun_balai)

# Menampilkan halaman form tambah akun balai
@app.route('/tambah_akun_balai_form', methods=['GET'])
def tambah_akun_balai_form():
    return render_template('admin/pages/UserBalai/tambah_akun_balai_form.html')

# Tambah akun Balai Konservasi
@app.route('/tambah_akun_balai', methods=['GET', 'POST'])
def tambah_akun_balai():
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form.get('nama')
        email = request.form.get('email')
        no_telp = request.form.get('no_telp')
        password = request.form.get('password')
        alamat = request.form.get('alamat')
        kabupaten = request.form.get('kabupaten')
        provinsi = request.form.get('provinsi')
        img_profil = request.files.get('img_profil')  # Mengambil file yang diunggah
        
        # Validasi form
        if not nama or not email or not no_telp or not password:
            flash("Semua field wajib diisi!", "danger")
            return redirect(url_for('tambah_akun_balai'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Simpan gambar profil jika ada
        filename = None
        if img_profil and img_profil.filename:
            filename = secure_filename(img_profil.filename)
            img_profil.save(os.path.join('static/uploads/', filename))

        # Simpan ke tabel User
        user = User(
            nama=nama,
            email=email,
            no_telp=no_telp,
            password=hashed_password,
            img_profil=f'uploads/{filename}' if filename else None,
            role='pihak_berwajib'
        )
        db.session.add(user)
        db.session.commit()

        # Simpan ke tabel AkunBalai
        akun_balai = AkunBalai(
            user_id=user.id,
            nama=nama,
            email=email,
            no_telp=no_telp,
            password=hashed_password,
            alamat=alamat,
            kabupaten=kabupaten,
            provinsi=provinsi,
            img_profil=f'uploads/{filename}' if filename else None  # Menyimpan gambar profil juga di AkunBalai
        )
        db.session.add(akun_balai)
        db.session.commit()

        flash('Akun Balai Konservasi berhasil ditambahkan', 'success')
        return redirect(url_for('akun_balai'))

    return render_template('admin/tambah_akun_balai.html')


# Route untuk menampilkan halaman edit akun balai
@app.route('/edit_balai/<int:id>', methods=['GET', 'POST'])
def edit_balai(id):
    balai = AkunBalai.query.get_or_404(id)

    if request.method == 'POST':
        # Update data AkunBalai
        balai.nama = request.form.get('nama')
        balai.email = request.form.get('email')
        balai.no_telp = request.form.get('no_telp')
        balai.alamat = request.form.get('alamat')
        balai.kabupaten = request.form.get('kabupaten')
        balai.provinsi = request.form.get('provinsi')

        # Update data User terkait
        user = User.query.get_or_404(balai.user_id)
        user.nama = balai.nama
        user.email = balai.email
        user.no_telp = balai.no_telp
        
        # Cek apakah pengguna mengunggah gambar baru
        img_profil = request.files.get('img_profil')
        if img_profil and img_profil.filename:
            filename = secure_filename(img_profil.filename)
            img_path = os.path.join('static/uploads/', filename)
            img_profil.save(img_path)
            balai.img_profil = f'uploads/{filename}'  # Simpan path relatif
            user.img_profil = f'uploads/{filename}'  # Update foto di tabel User

        # Commit kedua tabel
        db.session.commit()
        flash('Akun Balai Konservasi berhasil diperbarui', 'success')
        return redirect(url_for('akun_balai'))

    return render_template('admin/pages/UserBalai/edit_akun_balai.html', balai=balai)


# 📌 Route untuk menghapus akun balai
# Route untuk menghapus akun balai
@app.route('/delete_balai/<int:id>', methods=['POST'])
def delete_balai(id):
    akun_balai = AkunBalai.query.get_or_404(id)
    
    # Hapus data dari tabel User juga
    user = User.query.get_or_404(akun_balai.user_id)
    db.session.delete(user)  # Hapus akun user yang terkait
    
    db.session.delete(akun_balai)  # Hapus akun balai
    db.session.commit()

    flash('Akun Balai Konservasi dan data pengguna berhasil dihapus!', 'success')
    return redirect(url_for('akun_balai'))

 
def get_laporan_by_id(laporan_id):
    laporan = laporan.query.get(laporan_id)  # Sesuaikan dengan ORM yang digunakan
    return laporan

# ========================================================================================================================================
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app import app, db
from app.models import Lapor

# Fungsi untuk mendapatkan laporan berdasarkan ID
def get_laporan_by_id(laporan_id):
    return Lapor.query.get(laporan_id)

# Route untuk mengedit laporan
@app.route("/edit_laporan/<int:laporan_id>", methods=["GET", "POST"])
def edit_laporan(laporan_id):
    laporan = get_laporan_by_id(laporan_id)
    if not laporan:
        flash("Laporan tidak ditemukan.", "danger")
        return redirect(url_for("data_laporan"))

    if request.method == "POST":
        status_baru = request.form["status"]
        laporan.update_status(status_baru)

        # Jika ada bukti penindakan yang diupload
        if "bukti_penindakan" in request.files:
            file = request.files["bukti_penindakan"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                laporan.file_url = filename

        db.session.commit()
        flash("Laporan berhasil diperbarui.", "success")
        return redirect(url_for("data_laporan"))

    return render_template("admin/pages/Laporan_Edit.html", laporan=laporan)

# Route untuk menampilkan daftar laporan
@app.route("/data_laporan")
def data_laporan():
    laporan_data = Lapor.query.all()
    laporan_proses = Lapor.query.filter_by(status="sedang_di_proses").count()
    laporan_selesai = Lapor.query.filter_by(status="selesai_di_proses").count()

    return render_template(
        "admin/pages/Laporan.html",  # Menggunakan nama file yang benar
        laporan_data=laporan_data, 
        laporan_proses=laporan_proses, 
        laporan_selesai=laporan_selesai
    )

# Route untuk memperbarui laporan
@app.route('/update_laporan/<int:id>', methods=['POST'])
def update_laporan(id):
    laporan = Lapor.query.get_or_404(id)  # <- ganti di sini
    try:
        status = request.form.get('status')
        print("Status diterima dari form:", status)
        laporan.status = status

        # cek upload bukti
        if 'bukti_penindakan' in request.files and request.files['bukti_penindakan']:
            file_bukti = request.files['bukti_penindakan']
            if file_bukti.filename != '':
                file_url = simpanGambar(file_bukti)
                # jika tipe data gambar_bukti adalah list of dict, append
                if not hasattr(laporan, 'gambar_bukti') or laporan.gambar_bukti is None:
                    laporan.gambar_bukti = []
                laporan.gambar_bukti.append({'nama': file_url})

        db.session.commit()
        flash('Laporan berhasil diperbarui.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return redirect(url_for("data_laporan"))

# ========================================================================================================================================

@app.route('/status_laporan')
def status_laporan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    laporan_data = Lapor.query.filter_by(user_id=session['user_id']).order_by(Lapor.updated_at.desc()).all()
    return render_template('status_laporan.html', laporan_data=laporan_data)

# @app.route("/admin/about", methods=["GET", "POST"], endpoint="manage_about")
# def manage_about():
#     about_data = About.query.first()  # hanya ada 1 record About

#     if request.method == "POST":
#         title = request.form.get("title")
#         description = request.form.get("description")
#         image = request.files.get("image")

#         # Gunakan gambar lama jika ada, atau None
#         filename = about_data.image if about_data else None

#         # Jika ada gambar baru, simpan
#         if image and image.filename:
#             filename = secure_filename(image.filename)
#             upload_path = os.path.join(app.root_path, "static", "gambarUser")
#             os.makedirs(upload_path, exist_ok=True)
#             image.save(os.path.join(upload_path, filename))

#         # Update jika sudah ada data, kalau belum buat baru
#         if about_data:
#             about_data.title = title
#             about_data.description = description
#             about_data.image = filename
#         else:
#             about_data = About(
#                 title=title,
#                 description=description,
#                 image=filename
#             )
#             db.session.add(about_data)

#         db.session.commit()
#         flash("Data About berhasil disimpan!", "success")
#         return redirect(url_for("manage_about"))

#     return render_template("admin/pages/About/about.html", about=about_data)
@app.route("/admin/about", methods=["GET", "POST"], endpoint="about_admin")
def about_admin():
    about_data = About.query.first()  # hanya ada 1 record About

    # Jika belum ada data, buat default sementara (tidak langsung simpan)
    if not about_data:
        about_data = About(
            title="Tentang SIPANDA",
            description=(
                "Sistem Informasi Hewan Dilindungi (SIPANDA) merupakan platform edukatif "
                "yang membantu masyarakat mengenali dan melaporkan satwa dilindungi. "
                "Aplikasi ini dikembangkan untuk mendukung konservasi satwa di Indonesia."
            ),
            image="gedung_bksda.png"  # bisa kamu taruh gambar default di /static/gambarUser/
        )

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")

        # Hitung jumlah kata
        word_count = len(description.split())
        if word_count > 50:
            flash(f"Deskripsi tidak boleh lebih dari 50 kata! Saat ini: {word_count} kata", "danger")
            return redirect(url_for("about_admin"))

        # Gunakan gambar lama jika ada
        filename = about_data.image if about_data else None

        # Jika ada gambar baru
        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_path = os.path.join(app.root_path, "static", "gambarUser")
            os.makedirs(upload_path, exist_ok=True)
            image.save(os.path.join(upload_path, filename))

        # Update atau tambah baru ke database
        existing_about = About.query.first()
        if existing_about:
            existing_about.title = title
            existing_about.description = description
            existing_about.image = filename
        else:
            new_about = About(title=title, description=description, image=filename)
            db.session.add(new_about)

        db.session.commit()
        flash("Data About berhasil disimpan!", "success")
        return redirect(url_for("about_admin"))

    return render_template("admin/pages/About/about.html", about=about_data)

from flask import Flask, render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Jumbotron
@app.route('/admin/jumbotron', methods=['GET', 'POST'])
def admin_jumbotron():
    jumbotrons = Jumbotron.query.all()

    # Create
    if request.method == 'POST' and 'create' in request.form:
        title = request.form['title']
        subtitle = request.form['subtitle']

        # Validasi jumlah kata
        if len(title.split()) > 3:
            flash("Title tidak boleh lebih dari 3 kata!", "danger")
            return redirect(url_for('admin_jumbotron'))

        if len(subtitle.split()) > 20:
            flash("Subtitle tidak boleh lebih dari 20 kata!", "danger")
            return redirect(url_for('admin_jumbotron'))

        new_jumbotron = Jumbotron(title=title, subtitle=subtitle)
        db.session.add(new_jumbotron)
        db.session.commit()
        flash('Jumbotron berhasil dibuat!', 'success')
        return redirect(url_for('admin_jumbotron'))

    return render_template('admin/pages/Jumbotron/index.html', jumbotrons=jumbotrons)


@app.route('/admin/jumbotron/edit/<int:id>', methods=['POST'])
def edit_jumbotron(id):
    jumbotron = Jumbotron.query.get_or_404(id)
    title = request.form['title']
    subtitle = request.form['subtitle']

    # Validasi jumlah kata
    if len(title.split()) > 3:
        flash("Title tidak boleh lebih dari 3 kata!", "danger")
        return redirect(url_for('admin_jumbotron'))

    if len(subtitle.split()) > 20:
        flash("Subtitle tidak boleh lebih dari 20 kata!", "danger")
        return redirect(url_for('admin_jumbotron'))

    jumbotron.title = title
    jumbotron.subtitle = subtitle
    db.session.commit()
    flash('Jumbotron berhasil diubah!', 'success')
    return redirect(url_for('admin_jumbotron'))

@app.route('/admin/jumbotron/delete/<int:id>', methods=['POST'])
def delete_jumbotron(id):
    jumbotron = Jumbotron.query.get_or_404(id)
    db.session.delete(jumbotron)
    db.session.commit()
    flash('Jumbotron berhasil dihapus!', 'success')
    return redirect(url_for('admin_jumbotron'))

# Upload gambar baru
@app.route('/admin/jumbotron_images/upload', methods=['POST'])
def upload_jumbotron_image():
    file = request.files.get('image')
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.root_path, "static", "img")
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))

        new_img = JumbotronImage(filename=filename)
        db.session.add(new_img)
        db.session.commit()
        flash("Gambar berhasil di-upload!", "success")
    else:
        flash("Tidak ada gambar yang dipilih!", "danger")
    return redirect(url_for('admin_jumbotron_images'))

# Delete gambar
@app.route('/admin/jumbotron_images/delete/<int:id>', methods=['POST'])
def delete_jumbotron_image(id):
    img = JumbotronImage.query.get_or_404(id)
    # hapus file dari folder static
    try:
        file_path = os.path.join(app.root_path, "static", "img", img.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print("Error hapus file:", e)
    db.session.delete(img)
    db.session.commit()
    flash("Gambar berhasil dihapus!", "success")
    return redirect(url_for('admin_jumbotron_images'))

# Halaman utama jumbotron images
@app.route('/admin/jumbotron_images')
def admin_jumbotron_images():
    images = JumbotronImage.query.all()
    return render_template('admin/pages/Jumbotron/jumbotron_images.html', images=images)

# ========== CRUD Jenis Kawasan ==========
# ========== CRUD Jenis Kawasan ==========
@app.route('/admin/jenis_kawasan/create', methods=['POST'])
def create_jenis_kawasan():
    nama = request.form['nama']
    deskripsi = request.form['deskripsi']

    new_jenis = JenisKawasan(nama=nama, deskripsi=deskripsi)
    db.session.add(new_jenis)
    db.session.commit()

    flash("Jenis Kawasan berhasil ditambahkan", "success")
    return redirect(url_for('list_jenis_kawasan'))

@app.route("/admin/jenis_kawasan")
def list_jenis_kawasan():
    data = JenisKawasan.query.all()
    return render_template("admin/pages/Konservasi/kategori_konservasi.html", data=data)

@app.route('/admin/jenis_kawasan/update/<int:id>', methods=['POST'])
def update_jenis_kawasan(id):
    jenis = JenisKawasan.query.get_or_404(id)
    jenis.nama = request.form['nama']
    jenis.deskripsi = request.form['deskripsi']
    db.session.commit()
    flash("Jenis Kawasan berhasil diperbarui", "success")
    return redirect(url_for('list_jenis_kawasan'))

@app.route('/admin/jenis_kawasan/delete/<int:id>', methods=['POST'])
def delete_jenis_kawasan(id):
    jenis = JenisKawasan.query.get_or_404(id)
    db.session.delete(jenis)
    db.session.commit()
    flash("Jenis Kawasan berhasil dihapus", "success")
    return redirect(url_for('list_jenis_kawasan'))

# ========== CRUD Kawasan Konservasi ==========
import os

@app.route('/admin/kawasan/create', methods=['POST'])
def create_kawasan():
    nama = request.form['nama']
    lokasi = request.form['lokasi']
    deskripsi = request.form['deskripsi']
    jenis_id = request.form['jenis_id']

    foto = None
    file = request.files['foto']
    if file and file.filename != "":
        filename = file.filename

        # path absolut ke folder gambarKawasan
        folder_path = os.path.join(
            app.root_path, "static", "gambarKawasan"
        )
        os.makedirs(folder_path, exist_ok=True)

        file.save(os.path.join(folder_path, filename))
        foto = filename

    new_kawasan = KawasanKonservasi(
        nama=nama,
        lokasi=lokasi,
        deskripsi=deskripsi,
        jenis_id=jenis_id,
        foto=foto
    )
    db.session.add(new_kawasan)
    db.session.commit()

    flash("Kawasan Konservasi berhasil ditambahkan", "success")
    return redirect(url_for('list_kawasan'))


@app.route('/admin/kawasan/update/<int:id>', methods=['POST'])
def update_kawasan(id):
    kawasan = KawasanKonservasi.query.get_or_404(id)
    kawasan.nama = request.form['nama']
    kawasan.lokasi = request.form['lokasi']
    kawasan.deskripsi = request.form['deskripsi']
    kawasan.jenis_id = request.form['jenis_id']

    # jika update foto
    file = request.files['foto']
    if file and file.filename != "":
        filename = file.filename
        file.save(os.path.join('static/gambarKawasan', filename))
        kawasan.foto = filename

    db.session.commit()
    flash("Kawasan berhasil diperbarui", "success")
    return redirect(url_for('list_kawasan'))

@app.route('/admin/kawasan/delete/<int:id>', methods=['GET','POST'])
def delete_kawasan(id):
    kawasan = KawasanKonservasi.query.get_or_404(id)
    db.session.delete(kawasan)
    db.session.commit()
    flash("Kawasan berhasil dihapus", "success")
    return redirect(url_for('list_kawasan'))

@app.route("/admin/kawasan")
def list_kawasan():
    data = KawasanKonservasi.query.all()
    jenis_list = JenisKawasan.query.all()
    return render_template("admin/pages/Konservasi/createkawasan.html", data=data, jenis_list=jenis_list)

@app.route("/kawasan/<int:id>")
def detail_kawasan(id):
    kawasan = KawasanKonservasi.query.get_or_404(id)

    # jika ada foto, ambil url-nya
    url_foto = None
    if kawasan.foto:
        url_foto = url_for("static", filename="gambarKawasan/" + kawasan.foto)

    return render_template(
        "detail_kawasan.html",
        kawasan=kawasan,
        url_foto=url_foto
    )
@app.route("/kawasan")
def kawasan_public():
    # ambil semua Kawasan Konservasi
    data = KawasanKonservasi.query.all()
    return render_template("kawasan_list.html", data=data)

from flask import jsonify, request

@app.route("/api/pencarian/kawasan")
def api_pencarian_kawasan():
    search = request.args.get('search', '').strip()  # ambil query search, default kosong

    if search:
        # cari kawasan yang namanya mengandung keyword search
        hasil = KawasanKonservasi.query.filter(KawasanKonservasi.nama.ilike(f"%{search}%")).all()
    else:
        # jika tidak ada query, ambil semua
        hasil = KawasanKonservasi.query.all()

    # ubah hasil query jadi list dict untuk JSON
    data = []
    for k in hasil:
        data.append({
            'id': k.id,
            'nama': k.nama,
            'foto': k.foto or 'default.jpg',
            'lokasi': k.lokasi,
            'deskripsi': k.deskripsi,
            'jenis_id': k.jenis_id
        })

    return jsonify(data)


@app.route("/admin/unit_kerja")
def unit_kerja():
    data = UnitKerja.query.all()
    return render_template("admin/pages/UnitKerja/unit_kerja.html", data=data)

@app.route("/admin/unit_kerja/create", methods=["POST"])
def create_unit_kerja():
    new_unit = UnitKerja(
        nama=request.form['nama'],
        alamat=request.form['alamat'],
        kabupaten=request.form['kabupaten'],
        telepon=request.form['telepon'],
        email=request.form['email'],
        kepala_resor=request.form.get('kepala_resor'),
        kode_resor=request.form.get('kode_resor'),
        peta_lokasi=request.form.get('peta_lokasi'),
        wilayah_kerja=request.form.get('wilayah_kerja'),
        status=request.form['status']
    )
    db.session.add(new_unit)
    db.session.commit()
    flash("Unit Kerja berhasil ditambahkan", "success")
    return redirect(url_for('unit_kerja'))


@app.route("/admin/unit_kerja/update/<int:id>", methods=["POST"])
def update_unit_kerja(id):
    unit = UnitKerja.query.get_or_404(id)
    unit.nama = request.form['nama']
    unit.alamat = request.form['alamat']
    unit.kabupaten = request.form['kabupaten']
    unit.telepon = request.form['telepon']
    unit.email = request.form['email']
    unit.kepala_resor = request.form.get('kepala_resor')
    unit.kode_resor = request.form.get('kode_resor')
    unit.peta_lokasi = request.form.get('peta_lokasi')
    unit.wilayah_kerja = request.form.get('wilayah_kerja')
    unit.status = request.form['status']
    db.session.commit()
    flash("Unit Kerja berhasil diperbarui", "success")
    return redirect(url_for('unit_kerja'))

@app.route("/admin/unit_kerja/delete/<int:id>", methods=['POST'])
def delete_unit_kerja(id):
    unit = UnitKerja.query.get_or_404(id)
    db.session.delete(unit)
    db.session.commit()
    flash("Unit Kerja berhasil dihapus", "success")
    return redirect(url_for('unit_kerja'))



@app.route("/admin/bksda", methods=["GET"])
def admin_bksda():
    data = BKSDAProfile.query.first()  # hanya ambil 1 data
    return render_template("admin/pages/ProfileBKSDA/bksda.html", data=data)


# Create
@app.route("/admin/bksda/create", methods=["POST"])
def create_bksda():
    existing = BKSDAProfile.query.first()
    if existing:
        flash("Profil sudah ada, gunakan edit untuk mengubah.", "warning")
        return redirect(url_for("admin_bksda"))

    judul = request.form["judul"]
    deskripsi = request.form["deskripsi"]
    alamat = request.form["alamat"]
    telepon = request.form.get("telepon")
    email = request.form.get("email")
    website = request.form.get("website")
    kepala_balai = request.form.get("kepala_balai")
    visi = request.form.get("visi")
    misi = request.form.get("misi")
    jam_operasional = request.form.get("jam_operasional")
    informasi = request.form.get("informasi")

    gambar = None
    if "gambar" in request.files:
        file = request.files["gambar"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.root_path, "static", "gambarUser")
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            gambar = filename

    new_data = BKSDAProfile(
        judul=judul, deskripsi=deskripsi, alamat=alamat,
        telepon=telepon, email=email, website=website,
        kepala_balai=kepala_balai, visi=visi, misi=misi,
        jam_operasional=jam_operasional, informasi=informasi,
        gambar=gambar
    )
    db.session.add(new_data)
    db.session.commit()
    flash("Profil berhasil ditambahkan", "success")
    return redirect(url_for("admin_bksda"))

# Update
@app.route("/admin/bksda/update/<int:id>", methods=["POST"])
def update_bksda(id):
    profile = BKSDAProfile.query.get_or_404(id)
    profile.judul = request.form["judul"]
    profile.deskripsi = request.form["deskripsi"]
    profile.alamat = request.form["alamat"]
    profile.telepon = request.form.get("telepon")
    profile.email = request.form.get("email")
    profile.website = request.form.get("website")
    profile.kepala_balai = request.form.get("kepala_balai")
    profile.visi = request.form.get("visi")
    profile.misi = request.form.get("misi")
    profile.jam_operasional = request.form.get("jam_operasional")
    profile.informasi = request.form.get("informasi")

    if "gambar" in request.files:
        file = request.files["gambar"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.root_path, "static", "gambarUser")
            os.makedirs(upload_path, exist_ok=True)

            # hapus file lama kalau ada
            if profile.gambar:
                old_path = os.path.join(upload_path, profile.gambar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # simpan file baru
            file.save(os.path.join(upload_path, filename))
            profile.gambar = filename

    db.session.commit()
    flash("Profil berhasil diperbarui", "success")
    return redirect(url_for("admin_bksda"))

#=============================================================================================================================================================
#FOOTER#
#=============================================================================================================================================================
@app.route('/admin/footer', methods=['GET'])
def footer():
    return footer_index()

@app.route('/admin/footer/update', methods=['POST'])
def footer_update():
    return footer_updateF()