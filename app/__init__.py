from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app.utils import simpanGambar
from flask_mail import Mail
import datetime
import MySQLdb
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'abs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sipandas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nurafifahuswatunkh@gmail.com'
app.config['MAIL_PASSWORD'] = 'uxws nrqj ixfd ltpj'
app.config['MAIL_DEFAULT_SENDER'] = 'SIPANDA Support<nurafifahuswatunkh@gmail.com>'
app.config['JWT_SECRET_KEY'] = 'bigfours'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)  
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 900  


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
cache = Cache(app)

jwt = JWTManager(app)
mail = Mail(app)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='17955162853-5nfdfjc93msf4spbbdb0j7h4mdjnop6m.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'consent'
    },
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

from app import routes

# di app/__init__.py atau di routes.py sebelum app.run()
from app.models import BKSDAProfile, Footer

@app.context_processor
def inject_footer():
    footer = Footer.query.first()
    if not footer:
        class DummyFooter:
            title = "SIPANDA"
            description = "Sistem Informasi Hewan Dilindungi"
            instagram_link = "#"
            twitter_link = "#"
            facebook_link = "#"
            phone = "08123456789"
            email = "sipanda@gmail.com"
            address = "Tegal, Jawa Tengah"
            company_links = "Tentang,Fitur"
            feature_links = "FAQ,Testimonials"
            copyright_text = "© 2025 SIPANDA"
        footer = DummyFooter()
    return dict(footer=footer)

@app.context_processor
def inject_bksda_profile():
    profile = BKSDAProfile.query.first()
    return dict(bksda_profile=profile)
