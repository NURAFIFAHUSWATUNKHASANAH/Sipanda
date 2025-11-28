from functools import wraps
import os
from random import randint
from flask import current_app, render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from app import app, db, bcrypt, mail,cache
from app.utils import allowed_file, cek_nomor_wa, kirim_wa_fonnte, simpanGambar
from app.models import Lapor, RoleEnum, User
from flask_mail import Message
import jwt
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
           
            if 'role' not in session or session['role'] not in allowed_roles:
                flash('Akses ditolak! Kamu tidak memiliki izin untuk mengakses halaman ini.', 'danger')
                return redirect(url_for('home'))  
            return func(*args, **kwargs)
        return wrapper
    return decorator

#=============================================================================================================================================================
###### AUTH ######
#=============================================================================================================================================================


def registerF():
    try:
        # Ambil data dari form
        nama = request.form.get('nama')
        email = request.form.get('email')
        no_telp = request.form.get('no_telp')
        password = request.form.get('password')

        # Format nomor WA ke 62
        if no_telp.startswith("0"):
            no_telp = "62" + no_telp[1:]

        # Cek apakah email sudah terdaftar
        existing_user = User.query.filter_by(email=email).first()

        # === VALIDASI NOMOR WA ===
        validasi = cek_nomor_wa(no_telp)

        if validasi and "not_registered" in validasi and no_telp in validasi["not_registered"]:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"status": "error", "message": "Nomor WhatsApp tidak terdaftar."}, 400
            else:
                flash("Nomor WhatsApp tidak terdaftar!", "danger")
                return redirect(url_for('login'))

        existing_phone = User.query.filter_by(no_telp=no_telp).first()

        if existing_phone:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"status": "error", "message": "Nomor WhatsApp sudah terdaftar"}, 400
            else:
                flash('Nomor WhatsApp sudah terdaftar!', 'warning')
                return redirect(url_for('login'))


        if existing_user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"status": "error", "message": "Email sudah terdaftar"}, 400
            else:
                flash('Email sudah terdaftar, silakan login.', 'warning')
                return redirect(url_for('login'))


        # Enkripsi password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Simpan user baru ke database (belum aktif)
        new_user = User(nama=nama, email=email, no_telp=no_telp, password=hashed_password, is_verified=False)
        db.session.add(new_user)
        db.session.commit()
        print(f"👤 User baru ditambahkan: {email}")

        # Buat token verifikasi
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='email-confirmation-salt')

        # Buat tautan verifikasi
        link = url_for('verify_email', token=token, _external=True)

        # Kirim email verifikasi
        try:
            with current_app.app_context():
                msg = Message(
                    subject='Verifikasi Akun SIPANDA',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )
                msg.body = (
                    f"Halo {nama},\n\n"
                    f"Terima kasih telah mendaftar di SIPANDA.\n\n"
                    f"Silakan klik tautan berikut untuk verifikasi akunmu:\n"
                    f"{link}\n\n"
                    f"Tautan ini berlaku selama 1 jam.\n\n"
                    f"Salam,\nTim SIPANDA"
                )
                mail.send(msg)
                print(f"✅ Email verifikasi berhasil dikirim ke: {email}")
                flash('Pendaftaran berhasil! Cek email kamu untuk verifikasi akun.', 'success')
        except Exception as e:
            print("❌ Gagal mengirim email:", str(e))
            flash('Akun berhasil dibuat, tetapi email verifikasi gagal dikirim.', 'danger')

        # === KIRIM WA ===
        try:
            pesan_wa = (
                f"Halo {nama}! 👋\n\n"
                f"Terima kasih telah mendaftar di *SIPANDA*.\n"
                f"*{email}*\n\n"
                f"Silakan cek email kamu untuk melakukan verifikasi akun.\n\n"
                f"Salam,\nTim SIPANDA 🐼💚"
            )

            kirim_wa_fonnte(no_telp, pesan_wa)
            print(f"📲 WA berhasil dikirim ke {no_telp}")
        except Exception as e:
            print("❌ Gagal kirim WA:", str(e))
        # === END KIRIM WA ===
        # === RESPONSE AJAX SUCCESS ===
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"status": "success", "message": "Pendaftaran berhasil!"}, 200
        
        return redirect(url_for('login'))

    except Exception as e:
        print("❌ Error pada register:", str(e))
        db.session.rollback()
        flash('Terjadi kesalahan saat registrasi. Coba lagi.', 'danger')
        return redirect(url_for('login'))
    

def verify_emailF(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=3600)

        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()

            # ========== KIRIM WHATSAPP ========== 
            try:
                pesan_wa = (
                    f"Halo {user.nama}! 👋\n\n"
                    f"Akun kamu (*{user.email}*) berhasil *diverifikasi* ✅\n"
                    f"Sekarang kamu bisa login ke aplikasi SIPANDA.\n\n"
                    f"Selamat menggunakan layanan kami! 🐼💚"
                )

                # Format nomor HP ke 62
                no_telp = user.no_telp
                if no_telp.startswith("0"):
                    no_telp = "62" + no_telp[1:]

                kirim_wa_fonnte(no_telp, pesan_wa)
                print(f"📲 WA verifikasi berhasil dikirim ke {no_telp}")

            except Exception as e:
                print("❌ Gagal kirim WA:", str(e))
            # ========== END WHATSAPP ==========

            flash('Email kamu berhasil diverifikasi! Silakan login.', 'success')
            print(f"✅ Akun {email} berhasil diverifikasi.")
            return redirect(url_for('login'))

        else:
            flash('Akun tidak ditemukan.', 'danger')
            return redirect(url_for('login'))

    except Exception as e:
        print("❌ Token tidak valid atau kadaluarsa:", str(e))
        flash('Link verifikasi tidak valid atau sudah kadaluarsa.', 'danger')
        return redirect(url_for('login'))

def loginF():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = User.query.filter_by(email=email).first()

        if not users or not users.check_password(password):
            flash('Email atau password salah!', 'danger')
            return redirect(url_for('login'))

        if not users.is_verified:
            flash('Akun belum diverifikasi. Cek email kamu untuk verifikasi.', 'warning')
            return redirect(url_for('login'))

        # Jika sudah diverifikasi, lanjutkan login seperti biasa
        session['user_id'] = users.id
        session['email'] = users.email
        session['role'] = users.role.name
        session.permanent = True
        # app.permanent_session_lifetime = datetime.timedelta(hours=3)
        app.permanent_session_lifetime = timedelta(hours=3)


        flash('Berhasil login!', 'success')
        return redirect(url_for('home'))

    # ✅ Tambahkan ini untuk method GET
    return render_template('auth/login.html')

def registerApi():
    data = request.get_json()
    email = data.get('email')
    nama = data.get('nama')
    no_telp = data.get('no_telp')
    password = data.get('password')

    if not email or not nama or not password:
        return jsonify({'message': 'Wajib Di Isi Semua', 'status': 'Perhatian'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email Sudah Ada!', 'status': 'danger'}), 400

    try:
        user = User(
            nama=nama,
            email=email,
            no_telp=no_telp,
            img_profil="profilKosong.png" if not data.get('img_profil') else data.get('img_profil')
        )
        
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity={'id': user.id, 'email': user.email}, expires_delta=expires)

        return jsonify({
            'message': 'Kamu berhasil Buat Akun!',
            'status': 'success',
            'token': f"Bearer {access_token}",  # Tambahkan "Bearer " di depan token
            'user': {
                "id": user.id,
                "email": user.email,
                "nama": user.nama,
                "no_telp": user.no_telp,
                "img_profil": user.img_profil,
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'status': 'danger'}), 500

def loginApi():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Email atau Password Salah!', 'status': 'danger'}), 401

    # Buat token yang valid selama 7 hari
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity={'id': user.id, 'email': user.email}, expires_delta=expires)

    return jsonify({
        'message': 'Login berhasil!',
        'status': 'success',
        'token': f"Bearer {access_token}",  # Tambahkan "Bearer " di depan token
        'user': {
            "id": user.id,
            "email": user.email,
            "nama": user.nama,
            "no_telp": user.no_telp,
            "img_profil": user.img_profil,
        }
    }), 200

@app.route('/profil', methods=['GET', 'POST'])
def profilF():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        no_telp = request.form.get('no_telp')

        # ===================== Upload Foto Profil =====================
        if 'img_profil' in request.files:
            picture_file = request.files['img_profil']
            if picture_file and picture_file.filename != '':
                picture_filename = simpanGambar(picture_file)
                user.img_profil = picture_filename

        # ===================== Upload Banner Profil =====================
        if 'banner_profil' in request.files:
            banner_file = request.files['banner_profil']
            if banner_file and banner_file.filename != '':
                banner_filename = simpanGambar(banner_file)
                user.banner_profil = banner_filename

        # ===================== Update Data User =====================
        user.nama = nama
        user.email = email
        user.no_telp = no_telp

        # ===================== Update Data di Tabel Lapor =====================
        laporan_terkait = Lapor.query.filter_by(user_id=user.id).all()
        for laporan in laporan_terkait:
            laporan.nama_lapor = nama
            laporan.nomer_hp = no_telp

        # ===================== Simpan ke Database =====================
        db.session.commit()
        flash('Profil dan data laporan berhasil diperbarui!', 'success')
        return redirect(url_for('profil'))

    # ===================== Gambar Default Jika Tidak Ada =====================
    img_profil = url_for(
        'static',
        filename='gambarUser/' + (user.img_profil if user.img_profil else 'Banner1.jpeg')
    )

    banner_profil = url_for(
        'static',
        filename='gambarUser/' + (user.banner_profil if user.banner_profil else 'Banner1.jpeg')
    )

    return render_template('profil.html', user=user, img_profil=img_profil, banner_profil=banner_profil)

def bacaUser():
    users = User.query.all()
    return jsonify({"message": "berhasil"})

# 🔹 REQUEST RESET PASSWORD
def request_reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Buat token JWT berlaku 1 jam
            token = jwt.encode(
                {
                    "user_id": user.id,
                    "exp": datetime.utcnow() + timedelta(hours=1)
                },
                app.config['SECRET_KEY'], algorithm='HS256'
            )

            # Buat link reset password
            reset_link = url_for('resetPassword', token=token, _external=True)

            try:
                msg = Message(
                    subject="🔒 Reset Password SIPANDA",
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )

                # HTML Email Template
                msg.html = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color:#2c3e50;">Reset Password SIPANDA</h2>
                    <p>Halo <b>{user.nama}</b>,</p>
                    <p>Kami menerima permintaan untuk mengatur ulang kata sandi akunmu.</p>
                    <p>Silakan klik tombol di bawah ini untuk mereset kata sandi kamu:</p>
                    <p style="text-align:center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background-color:#007bff; color:white; padding:10px 20px; 
                                  text-decoration:none; border-radius:5px; display:inline-block;">
                            Reset Password
                        </a>
                    </p>
                    <p>Tautan ini akan kedaluwarsa dalam 1 jam.</p>
                    <p>Jika kamu tidak meminta reset password, abaikan email ini.</p>
                    <hr>
                    <p style="font-size:12px; color:#888;">© 2025 SIPANDA - Sistem Informasi Perlindungan Satwa</p>
                </div>
                """

                # Kirim email
                mail.send(msg)
                print(f"✅ Email reset password berhasil dikirim ke {email}")
                flash('Email reset password telah dikirim. Silakan cek inbox kamu.', 'success')

            except Exception as e:
                print("❌ Gagal mengirim email:", str(e))
                flash('Gagal mengirim email reset password.', 'danger')
        else:
            flash('Email tidak ditemukan.', 'danger')

    return render_template('auth/request_reset_password.html')


# 🔹 RESET PASSWORD DARI LINK EMAIL
def reset_password(token):
    try:
        # Decode token JWT
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(data['user_id'])

        if not user:
            flash('Token tidak valid atau akun tidak ditemukan.', 'danger')
            return redirect(url_for('requestResetPassword'))

        if request.method == 'POST':
            new_password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Validasi password
            if not new_password or new_password != confirm_password:
                flash('Password tidak cocok atau kosong.', 'danger')
                return redirect(url_for('resetPassword', token=token))

            user.set_password(new_password)
            db.session.commit()

            flash('Password berhasil diubah. Silakan login.', 'success')
            return redirect(url_for('login'))

        return render_template('auth/reset_password.html', token=token)

    except jwt.ExpiredSignatureError:
        flash('Token telah kadaluarsa. Silakan minta ulang reset password.', 'danger')
        return redirect(url_for('requestResetPassword'))
    except jwt.InvalidTokenError:
        flash('Token tidak valid.', 'danger')
        return redirect(url_for('requestResetPassword'))

def req_api_pass():
    email = request.json.get('email')  # Mengambil data dari JSON
    user = User.query.filter_by(email=email).first()

    if user:
        # Generate token numerik (6 digit)
        token = str(randint(100000, 999999))

        # Simpan token di cache
        cache_key = f"reset_token_{email}"
        cache.set(cache_key, token)

        try:
            msg = Message(
                subject="Reset Password SIPANDA",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email]
            )
            msg.body = f"Token reset password Anda: {token}. Token berlaku selama 15 menit."
            mail.send(msg)

            return jsonify({"message": "Email reset password telah dikirim."}), 200
        except Exception as e:
            return jsonify({"error": f"Gagal mengirim email: {str(e)}"}), 500
    else:
        return jsonify({"error": "Email tidak ditemukan."}), 404

def reset_password_api():
    data = request.json
    email = data.get('email')
    token = data.get('token')  # Token dari user
    new_password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not new_password or new_password != confirm_password:
        return jsonify({"error": "Password tidak cocok atau kosong."}), 400

    # Ambil token dari cache
    cache_key = f"reset_token_{email}"
    cached_token = cache.get(cache_key)

    if not cached_token or cached_token != token:
        return jsonify({"error": "Token tidak valid atau telah kadaluarsa."}), 400

    # Reset password
    user = User.query.filter_by(email=email).first()
    if user:
        user.set_password(new_password)
        db.session.commit()

        # Hapus token dari cache setelah digunakan
        cache.delete(cache_key)

        return jsonify({"message": "Password berhasil diubah. Silakan login."}), 200
    else:
        return jsonify({"error": "Email tidak ditemukan."}), 404

def updateProfilApi():
    try:
        # Ambil data dari form-data
        user_id = request.form.get('id')
        email = request.form.get('email')
        nama = request.form.get('nama')
        no_telp = request.form.get('no_telp')
        file = request.files.get('img_profil')  # File gambar

        # Validasi input
        if not user_id or not user_id.isdigit():
            return jsonify({"msg": "Invalid or missing user ID"}), 400

        if not email or '@' not in email:
            return jsonify({"msg": "Invalid email address"}), 400

        if not nama or len(nama) < 3:
            return jsonify({"msg": "Name must be at least 3 characters"}), 400

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"msg": "User not found"}), 404

        # Update user data
        user.email = email
        user.nama = nama
        user.no_telp = no_telp

        # Update gambar jika ada
        if file:
            # Simpan file gambar menggunakan simpanGambar
            filename = simpanGambar(file)

            # Hapus gambar lama jika ada
            if user.img_profil:
                old_filepath = os.path.join(current_app.root_path, 'static/gambarUser', user.img_profil)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            user.img_profil = filename

        db.session.commit()

        return jsonify({
            "msg": "Profile updated successfully",
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "nama": user.nama,
                "no_telp": user.no_telp,
                "img_profil": f"{user.img_profil}" if user.img_profil else None,
            }
        }), 200

    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    
def data_user():
    # Mengambil data total pengguna berdasarkan role
    total_super_admin = User.query.filter_by(role=RoleEnum.super_admin).count()
    total_admin = User.query.filter_by(role=RoleEnum.pihak_berwajib).count()
    total_user = User.query.filter_by(role=RoleEnum.user).count()

    # Mengambil semua data pengguna
    users = User.query.all()

    # Me-render template pengguna.html dengan data
    return render_template(
        '/admin/pages/Pengguna/pengguna.html',
        total_super_admin=total_super_admin,
        total_admin=total_admin,
        total_user=total_user,
        users=users
    )

def edit_pengguna(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        email = request.form['email']
        no_telp = request.form['no_telp']
        role = request.form['role']
        
        # Proses gambar profil jika ada
        img_profil = request.files.get('img_profil')

        # Update data pengguna
        user.nama = nama
        user.email = email
        user.no_telp = no_telp
        user.role = role

        if img_profil and allowed_file(img_profil.filename):  # Pastikan file valid
            # Simpan gambar baru dan perbarui path gambar pengguna
            gambar_filename = simpanGambar(img_profil)
            user.img_profil = gambar_filename

        # Simpan perubahan ke database
        db.session.commit()

        flash('Data pengguna berhasil diperbarui!', 'success')
        return redirect(url_for('pengguna'))  # Ganti dengan rute yang sesuai untuk daftar pengguna

    return render_template('admin/pages/Pengguna/update.html', user=user)

def delete_user_by_id(user_id):
    user = User.query.get_or_404(user_id)  # Ambil user berdasarkan ID, jika tidak ditemukan akan 404

    try:
        db.session.delete(user)  # Hapus data user dari session
        db.session.commit()  # Simpan perubahan
        flash('User berhasil dihapus.', 'success')  # Tampilkan pesan sukses
    except Exception as e:
        db.session.rollback()  # Batalkan transaksi jika terjadi error
        flash(f'Terjadi kesalahan saat menghapus user: {str(e)}', 'danger')  # Pesan error

    return redirect(url_for('pengguna'))

def hapusakun(id):
    try:
        # Ambil data dari request
        data = request.get_json()
        password = data.get('password')

        if not password:
            return jsonify({"message": "Password diperlukan untuk verifikasi.", "success": False}), 400

        # Cari user berdasarkan ID
        user = User.query.filter_by(id=id).first()
        
        if not user:
            return jsonify({"message": "User tidak ditemukan.", "success": False}), 404

        # Verifikasi password
        if not user.check_password(password):
            return jsonify({"message": "Password salah.", "success": False}), 401

        # Tandai pengguna sebagai dihapus dengan mengisi field deleted_at
        
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Akun berhasil dihapus.", "success": True}), 200
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan saat menghapus akun.", "error": str(e), "success": False}), 500
