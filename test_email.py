from flask_mail import Message
from app import app, mail

with app.app_context():
    msg = Message(
        subject="Tes Email dari SIPANDA",
        recipients=["afifahhffi@gmail.com"],  # ganti dengan email penerima
        body="Halo! Ini percobaan kirim email dari Flask (SIPANDA)."
    )
    mail.send(msg)
    print("✅ Email berhasil dikirim!")
