from datetime import datetime
from app.models import BalaiKonservasi, cobabalai
from flask import render_template, request, redirect, url_for, flash, jsonify
from app.utils import simpanGambar
from app import db

import math

def BacaDataBalai():
    balai = BalaiKonservasi.query.all()
    
    return render_template('/admin/pages/BalaiKonservasi/index.html', balai=balai)

def detailBalai(id_balaikonservasi):
    balai = BalaiKonservasi.query.filter_by(id_balaikonservasi=id_balaikonservasi).first_or_404()

    return render_template('detailBalai.html', balai=balai)


def BacaDataBalaiApi():
    balais = BalaiKonservasi.query.all()
    
    return jsonify({
    "message": "Data berhasil Dibaca", 
    "body": [BalaiKonservasi.ubahJson() for BalaiKonservasi in balais]
})

# def editDatabalais(id_balaikonservasi):
#     balai = BalaiKonservasi.query.get_or_404(id_balaikonservasi)

#     if request.method == 'POST':
#         balai.nama_balai = request.form['nama_balai']
#         balai.deskripsi = request.form['deskripsi']
#         balai.provinsi = request.form['provinsi']
#         balai.alamat = request.form['alamat']

#         if 'gambarbalai' in request.files:
#             file = request.files['gambarbalai']
#             if file and file.filename != '':
#                 gambar_filename = simpanGambar(file)
#                 balai.gambarbalai = gambar_filename

#         balai.updated_at = datetime.utcnow()

#         try:
#             db.session.commit()
#             flash('Data balai berhasil diperbarui!', 'success')
#             # Redirect ke halaman daftar balai setelah update
#             return redirect(url_for('balaiKonservasi'))
#         except Exception as e:
#             db.session.rollback()
#             flash('Terjadi kesalahan: ' + str(e), 'danger')
#             return redirect(request.url)

#     return render_template('admin/pages/BalaiKonservasi/update.html', balai=balai)


# def tambahDataBalai():
#     if request.method == 'POST':
#         data = request.form
#         nama_balai = data.get('nama_balai')
#         deskripsi = data.get('deskripsi')
#         provinsi = data.get('provinsi')
#         alamat = data.get('alamat')
#         url = request.files['gambarbalai']
#         gambarbalai = simpanGambar(url)
#         dtBalai = BalaiKonservasi(nama_balai=nama_balai, deskripsi=deskripsi, provinsi=provinsi, alamat=alamat,  gambarbalai=gambarbalai)
#         db.session.add(dtBalai)
#         db.session.commit()
        
#         return redirect(url_for('balaiKonservasi')) 
    
#     return render_template('/admin/pages/BalaiKonservasi/tambah.html')

def tambahDataBalai():
    if request.method == 'POST':
        data = request.form
        nama_balai = data.get('nama_balai')
        deskripsi = data.get('deskripsi')
        provinsi = data.get('provinsi')
        alamat = data.get('alamat')
        latitude = float(data.get('latitude'))      # <--- Tambahan
        longitude = float(data.get('longitude'))    # <--- Tambahan
        call_center = data.get('call_center')

        # Simpan gambar
        if 'gambarbalai' in request.files:
            file = request.files['gambarbalai']
            if file and file.filename != '':
                gambarbalai = simpanGambar(file)
            else:
                gambarbalai = None
        else:
            gambarbalai = None

        # Buat objek BalaiKonservasi
        dtBalai = BalaiKonservasi(
            nama_balai=nama_balai,
            deskripsi=deskripsi,
            provinsi=provinsi,
            alamat=alamat,
            latitude=latitude,
            longitude=longitude,
            call_center=call_center,
            gambarbalai=gambarbalai
        )

        # Simpan ke database
        try:
            db.session.add(dtBalai)
            db.session.commit()
            flash('Data balai berhasil ditambahkan!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan: ' + str(e), 'danger')
            return redirect(request.url)

        return redirect(url_for('balaiKonservasi'))

    return render_template('/admin/pages/BalaiKonservasi/tambah.html')

def editDatabalais(id_balaikonservasi):
    balai = BalaiKonservasi.query.get_or_404(id_balaikonservasi)

    if request.method == 'POST':
        balai.nama_balai = request.form['nama_balai']
        balai.deskripsi = request.form['deskripsi']
        balai.provinsi = request.form['provinsi']
        balai.alamat = request.form['alamat']
        balai.latitude = float(request.form['latitude'])     # <--- Tambahan
        balai.longitude = float(request.form['longitude'])   # <--- Tambahan
        balai.call_center = request.form['call_center']

        # Update gambar jika ada file baru
        if 'gambarbalai' in request.files:
            file = request.files['gambarbalai']
            if file and file.filename != '':
                gambar_filename = simpanGambar(file)
                balai.gambarbalai = gambar_filename

        balai.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            flash('Data balai berhasil diperbarui!', 'success')
            return redirect(url_for('balaiKonservasi'))
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan: ' + str(e), 'danger')
            return redirect(request.url)

    return render_template('admin/pages/BalaiKonservasi/update.html', balai=balai)


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius bumi dalam kilometer
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def balai_terdekat():
    user_lat = float(request.args.get('latitude'))
    user_lon = float(request.args.get('longitude'))

    balai_konservasi = cobabalai.query.all()

    result = []
    for balai in balai_konservasi:
        distance = calculate_distance(user_lat, user_lon, balai.latitude, balai.longitude)
        result.append({
            'id': balai.id,
            'nama_balai': balai.nama_balai,
            'alamat': balai.alamat,
            'kontak': balai.kontak,
            'latitude': balai.latitude,
            'longitude': balai.longitude,
            'distance': distance
        })

    sorted_balai = sorted(result, key=lambda x: x['distance'])
    return jsonify(sorted_balai)



def halamanDataBalai():
    balais= BalaiKonservasi.query.all()
    return render_template('HalamanDataBalai.html', balais=balais)


def pencarianB():
    query = request.args.get('search', '')
    if query:
        balais = BalaiKonservasi.query.filter(BalaiKonservasi.nama_balai.ilike(f"%{query}%")).all()
    else:
        balais = BalaiKonservasi.query.all()

    data = [
        {
            'nama_balai': balai.nama_balai,
            'gambarbalai': balai.gambarbalai,
        } for balai in balais
    ]
    return jsonify(data)

def deleteBalaiKonservasi(id_balaikonservasi):
    # Ambil data balai konservasi berdasarkan ID atau kembalikan 404 jika tidak ditemukan
    balai = BalaiKonservasi.query.get_or_404(id_balaikonservasi)

    try:
        db.session.delete(balai)  # Hapus data dari database
        db.session.commit()  # Simpan perubahan
        flash('Data Balai Konservasi berhasil dihapus.', 'success')  # Pesan sukses
    except Exception as e:
        db.session.rollback()  # Batalkan transaksi jika terjadi error
        flash('Terjadi kesalahan saat menghapus data: ' + str(e), 'danger')  # Pesan error

    # Redirect ke halaman daftar balai konservasi
    return redirect(url_for('balaiKonservasi'))