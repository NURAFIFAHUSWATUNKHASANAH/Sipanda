from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Footer
# ==================== FUNGSI UTAMA FOOTER ====================
def footer_index():
    footer = Footer.query.first()

    # Jika belum ada data footer, buat data default
    if not footer:
        footer = Footer(
            title="SIPANDA - Sistem Informasi Satwa Dilindungi",
            description="SIPANDA membantu masyarakat mengenali dan melaporkan satwa yang dilindungi untuk mendukung pelestarian keanekaragaman hayati.",
            instagram_link="https://instagram.com/sipanda_official",
            twitter_link="https://twitter.com/sipanda",
            facebook_link="https://facebook.com/sipanda.id",
            phone="+628123456789",
            email="info@sipanda.id",
            address="Jl. Hutan Lestari No. 12, Jakarta, Indonesia",
            company_links="Tentang Kami,Karier,Kontak",
            feature_links="Deteksi Satwa,Peta Habitat,Laporan Pelanggaran",
            copyright_text="© 2025 SIPANDA. All rights reserved."
        )
        db.session.add(footer)
        db.session.commit()

    return render_template('admin/pages/Footer/footer.html', footer=footer)


def footer_updateF():
    footer = Footer.query.first()

    if not footer:
        footer = Footer()  # Buat baru kalau belum ada
        db.session.add(footer)

    footer.title = request.form.get('title', '')
    footer.description = request.form.get('description', '')
    footer.instagram_link = request.form.get('instagram_link', '')
    footer.twitter_link = request.form.get('twitter_link', '')
    footer.facebook_link = request.form.get('facebook_link', '')
    footer.phone = request.form.get('phone', '')
    footer.email = request.form.get('email', '')
    footer.address = request.form.get('address', '')
    footer.company_links = request.form.get('company_links', '')
    footer.feature_links = request.form.get('feature_links', '')
    footer.copyright_text = request.form.get('copyright_text', '')

    db.session.commit()
    flash("Footer berhasil diperbarui!", "success")

    return redirect(url_for('footer'))
