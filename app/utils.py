import os
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image

def simpanGambar(gambar):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(gambar.filename)
    picture_fn =random_hex + f_ext
    gambar_path = os.path.join(current_app.root_path, 'static/gambarUser', picture_fn)
    output_size = (224,224)
    img = Image.open(gambar)
    img.thumbnail(output_size)
    img.save(gambar_path)
    return picture_fn

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def saveHewan(files, upload_folder,hewan_id):
    saved_paths = []
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    for file in files:
        if file and allowed_file(file.filename):
            filename = f"{hewan_id}_{secure_filename(file.filename)}"
            file_path = os.path.join(upload_folder, filename)
            
            file.save(file_path)
            saved_paths.append(file_path)

    return saved_paths

import requests

def kirim_wa_fonnte(target, message):
    print("🚀 Mengirim WA ke:", target)
    print("📩 Isi pesan:", message)

    url = "https://api.fonnte.com/send"

    payload = {
        'target': target,
        'message': message
    }

    headers = {
        'Authorization': "tPyEH6cR5G5mHfLhNDGv"
    }

    response = requests.post(url, data=payload, headers=headers)

    print("📨 Response Fonnte:", response.text)
    print("🔚 Selesai kirim WA\n")
    return response

def cek_nomor_wa(nomor):
    url = "https://api.fonnte.com/validate"

    headers = {
        "Authorization": "tPyEH6cR5G5mHfLhNDGv"
    }

    data = {
        "target": nomor
    }

    r = requests.post(url, headers=headers, data=data)
    print("🔍 Validasi WA:", r.text)
    return r.json()

import requests

def send_wa_otp(nomor, otp):
    url = "https://api.fonnte.com/send"

    payload = {
        "target": nomor,
        "message": f"Kode verifikasi SIPANDA Anda adalah: *{otp}*.\nJangan berikan kode ini kepada siapa pun."
    }

    headers = {
        "Authorization": "tPyEH6cR5G5mHfLhNDGv"
    }

    try:
        requests.post(url, data=payload, headers=headers)
        print("OTP terkirim ke WA:", nomor)
    except Exception as e:
        print("Gagal kirim OTP:", str(e))
