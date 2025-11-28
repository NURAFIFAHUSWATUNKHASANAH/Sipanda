from flask import render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
from app import app, db, bcrypt  

from werkzeug.utils import secure_filename
import os
from app.models import Lapor, StatusEnum, User, gambarBukti
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os, shutil
from app import app, db
from app.models import Lapor, User, gambarBukti

def laporF():
    # Cek login
    if 'user_id' not in session:
        flash("Anda harus login untuk mengakses halaman ini.", "danger")
        return redirect(url_for('login', next=request.url))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash("Pengguna tidak ditemukan.", "danger")
        return redirect(url_for('login'))

    # Ambil file_url dari GET (hasil scan) atau hidden input
    file_url = request.args.get('file_url')  # bisa berupa uploads/nama_file.jpg

    if request.method == 'POST':
        # Ambil data form
        nama_lapor = request.form['nama_lapor']
        nomer_hp = request.form['nomer_hp']
        alamat = request.form['alamat']
        maps = request.form['maps']
        keterangan = request.form['keterangan']
        file_url_form = request.form.get('file_url')  # hidden input

        # --------------------------
        # Tangani file scan (copy ke laporan)
        # --------------------------
        if file_url_form:
            filename_scan = os.path.basename(file_url_form)
            src_path = os.path.join(app.root_path, 'static', 'uploads', filename_scan)
            if os.path.exists(src_path):
                laporan_folder = os.path.join(app.root_path, 'static', 'laporan')
                os.makedirs(laporan_folder, exist_ok=True)
                dest_path = os.path.join(laporan_folder, filename_scan)
                shutil.copy(src_path, dest_path)
                file_url = f"laporan/{filename_scan}"  # path relatif ke DB
            else:
                file_url = None

        # --------------------------
        # Tangani upload gambar laporan manual (opsional)
        # --------------------------
        gambar_laporan = request.files.get('gambar_laporan')
        if gambar_laporan and gambar_laporan.filename:
            laporan_folder = os.path.join(app.root_path, 'static', 'laporan')
            os.makedirs(laporan_folder, exist_ok=True)
            filename_laporan = secure_filename(gambar_laporan.filename)
            gambar_laporan.save(os.path.join(laporan_folder, filename_laporan))
            file_url = f"laporan/{filename_laporan}"  # overwrite file_url jika upload manual

        # --------------------------
        # Simpan data Lapor ke DB
        # --------------------------
        laporan = Lapor(
            user_id=user_id,
            nama_lapor=nama_lapor,
            nomer_hp=nomer_hp,
            alamat=alamat,
            maps=maps,
            keterangan=keterangan,
            file_url=file_url
        )
        db.session.add(laporan)
        db.session.commit()

        # --------------------------
        # Tangani multiple bukti foto
        # --------------------------
        gambar_bukti_files = request.files.getlist('gambar_bukti[]')
        bukti_folder = os.path.join(app.root_path, 'static', 'bukti')
        os.makedirs(bukti_folder, exist_ok=True)

        for gambar_bukti in gambar_bukti_files:
            if gambar_bukti and gambar_bukti.filename:
                filename_bukti = secure_filename(gambar_bukti.filename)
                gambar_bukti.save(os.path.join(bukti_folder, filename_bukti))
                bukti = gambarBukti(
                    id_laporan=laporan.id,
                    nama=f"bukti/{filename_bukti}"  # path relatif ke DB
                )
                db.session.add(bukti)

        db.session.commit()  # commit semua bukti foto

        flash("popup")
        return redirect(url_for('lapor'))

    # --------------------------
    # Pastikan file_url preview di form
    # --------------------------
    if file_url:
        # jika file_url hanya nama file, tambahkan folder uploads
        if not file_url.startswith(("uploads/", "laporan/")):
            file_url = f"uploads/{os.path.basename(file_url)}"

    return render_template('lapor.html', user=user, file_url=file_url)

def laporApiF():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data tidak valid"}), 400

    nama_lapor = data.get('nama_lapor')
    nomer_hp = data.get('nomer_hp')
    alamat = data.get('alamat')
    maps = data.get('maps')
    keterangan = data.get('keterangan')
    status = data.get('status', StatusEnum.sedang_di_proses.value)  
    file_url = request.get('file_url')

    # Validasi status jika disediakan
    if status not in [e.value for e in StatusEnum]:
        return jsonify({"error": "Status tidak valid"}), 400

    laporan = Lapor(
        nama_lapor=nama_lapor,
        nomer_hp=nomer_hp,
        alamat=alamat,
        maps=maps,
        file_url=file_url,
        keterangan=keterangan,
        status=status
    )
    db.session.add(laporan)
    db.session.commit()

    return jsonify({
        "message": "Laporan berhasil disimpan",
        "data": {
            "id": laporan.id,
            "nama_lapor": nama_lapor,
            "nomer_hp": nomer_hp,
            "alamat": alamat,
            "maps": maps,
            "keterangan": keterangan,
            "file_url": file_url,
            "status": status
        }
    }), 201

def laporan_page():
    """Halaman untuk menampilkan semua data laporan."""
    laporan_data = Lapor.query.all()
    laporan_proses = Lapor.query.filter_by(status=StatusEnum.sedang_di_proses.value).count()
    laporan_selesai = Lapor.query.filter_by(status=StatusEnum.selesai_di_proses.value).count()
    return render_template(
        'admin/pages/Laporan.html', 
        laporan_data=laporan_data, 
        laporan_proses=laporan_proses, 
        laporan_selesai=laporan_selesai
    )


def update_status():
    """Fungsi untuk memperbarui status laporan."""
    laporan_id = request.form.get('id')
    status = request.form.get('status')

    if not laporan_id or not status:
        flash("ID laporan atau status tidak ditemukan.", 'danger')
        return redirect(url_for('laporan'))

    laporan = Lapor.query.get(laporan_id)
    if not laporan:
        flash("Laporan tidak ditemukan.", 'danger')
        return redirect(url_for('laporan'))

    # Validasi status
    valid_statuses = [e.value for e in StatusEnum]
    if status not in valid_statuses:
        flash("Status tidak valid.", 'danger')
        return redirect(url_for('laporan'))

    # Update status laporan
    laporan.status = status
    db.session.commit()
    flash(f"Status laporan berhasil diubah menjadi '{status}'.", 'success')
    return redirect(url_for('laporan'))

def delete_laporan_by_id(laporan_id):
    laporan = Lapor.query.get_or_404(laporan_id)

    try:
        db.session.delete(laporan)  # Hapus laporan dari database
        db.session.commit()  # Simpan perubahan ke database
        flash('Laporan berhasil dihapus.', 'success')  # Tampilkan pesan sukses
    except Exception as e:
        db.session.rollback()  # Batalkan perubahan jika terjadi kesalahan
        flash(f'Terjadi kesalahan saat menghapus laporan: {e}', 'danger')  # Tampilkan pesan error

    return redirect(url_for('laporan'))

def cobaUpdate():
    data = request.json  # Mengambil data JSON dari fetch
    laporan_id = data.get('id')
    new_status = data.get('status')

    # Update laporan berdasarkan ID di database Anda
    laporan = Lapor.query.get(laporan_id)
    if laporan:
        laporan.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status berhasil diperbarui!'})
    return jsonify({'success': False, 'message': 'Laporan tidak ditemukan!'})