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
from app.models import About, BKSDAProfile, Comment, JenisKawasan, Jumbotron, JumbotronImage, KawasanKonservasi, UnitKerja, gambarBukti, Lapor, RoleEnum, User, HewanModel, BalaiKonservasi, Berita
from app.Controllers.Chatbot import chat
from app import google, db
from app.utils import send_wa_otp, simpanGambar
import secrets
from werkzeug.security import generate_password_hash
from flask import flash, redirect, url_for, session, current_app
from flask_mail import Message
from app import db, mail
from app.models import User, RoleEnum  # Sesuaikan dengan modelmu

def google_callbackF():
    try:
        # Ambil token dan info user dari Google
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
    except Exception as e:
        flash(f'Login gagal: {str(e)}', 'danger')
        return redirect(url_for('login'))

    if not user_info:
        flash('Login gagal! Tidak dapat mengambil data dari Google.', 'danger')
        return redirect(url_for('login'))

    email = user_info.get('email')
    nama = user_info.get('name')

    # Cek apakah user sudah ada
    user = User.query.filter_by(email=email).first()
    if not user:
        # Buat password acak untuk user Google (tidak digunakan)
        random_password = generate_password_hash(secrets.token_urlsafe(16))

        # Buat user baru
        user = User(
            nama=nama,
            email=email,
            password=random_password,   # Tidak NULL
            role=RoleEnum.user,         # Role default
            no_telp=0,
            is_verified=True            # Langsung verified
        )
        db.session.add(user)
        db.session.commit()
        print(f"👤 User baru dibuat dari login Google: {email}")

    # Set session
    session['user_id'] = user.id
    session['email'] = user.email
    session['role'] = user.role.value if user.role else 'user'

    # 🔹 Kirim email notifikasi login
    try:
        msg = Message(
            subject="Notifikasi Login SIPANDA",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        msg.body = (
            f"Halo {nama},\n\n"
            f"Kami mendeteksi ada login ke akun SIPANDA kamu menggunakan Google.\n"
            f"Jika ini kamu, tidak perlu khawatir.\n"
            f"Jika bukan kamu, segera amankan akunmu.\n\n"
            f"Salam,\nTim SIPANDA"
        )
        mail.send(msg)
        print(f"✅ Email notifikasi login berhasil dikirim ke {email}")
    except Exception as e:
        print(f"❌ Gagal mengirim email notifikasi login: {str(e)}")

    flash('Berhasil login dengan Google!', 'success')

    # Cek apakah user belum punya nomor HP
    if not user.no_telp or user.no_telp == "0":
        return redirect(url_for('lengkapi_nomor'))

    return redirect(url_for('home'))

def require_phone_numberF():
    allowed_routes = ['login', 'google_login', 'google_callback', 'lengkapi_nomor', 'verifikasi_nomor']

    if request.endpoint in allowed_routes or request.endpoint is None:
        return

    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        if user and (user.no_telp is None or user.no_telp == "" or user.no_telp == "0"):
            return redirect(url_for('lengkapi_nomor'))
        

def lengkapi_nomorF():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user.no_telp not in [None, "", "0"]:
        return redirect(url_for('home'))

    if request.method == 'POST':
        nomor = request.form.get('no_telp')

        if not nomor:
            return jsonify({"status": "error", "message": "Nomor telepon wajib diisi!"}), 400

        # ❗ Cek apakah nomor sudah dipakai user lain
        cek_nomor = User.query.filter(
            User.no_telp == nomor,
            User.id != user.id
        ).first()

        if cek_nomor:
            return jsonify({
                "status": "error",
                "message": "Nomor WhatsApp sudah terdaftar"
            }), 409

        # Simpan sementara di session
        session['temp_no_telp'] = nomor

        # OTP
        otp = random.randint(100000, 999999)
        session['otp'] = str(otp)

        send_wa_otp(nomor, otp)

        return jsonify({
            "status": "success",
            "message": "OTP dikirim",
            "redirect": url_for('verifikasi_nomor')
        })

    return render_template('auth/lengkapi_nomor.html')

def verifikasi_nomorF():
    if 'otp' not in session:
        return redirect(url_for('lengkapi_nomor'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        kode = request.form.get('otp')

        if kode != session.get('otp'):
            flash("Kode OTP salah!", "danger")
            return redirect(url_for('verifikasi_nomor'))

        # Simpan ke DB
        user.no_telp = session.get('temp_no_telp')
        db.session.commit()

        # Bersihkan session
        session.pop('otp')
        session.pop('temp_no_telp')

        flash("Nomor HP berhasil diverifikasi!", "success")
        return redirect(url_for('home'))

    return render_template('auth/verifikasi_nomor.html')