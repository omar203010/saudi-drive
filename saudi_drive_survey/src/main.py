from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.survey import survey_bp
from src.routes.admin import admin_bp
import os

app = Flask(__name__)

# 🔑 إعداد المفتاح السري للجلسات من Environment Variable
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# 🔗 تهيئة قاعدة البيانات
# إذا Render أعطاك DATABASE_URL (PostgreSQL) → يستخدمه
# إذا ما فيه → يرجع لـ SQLite محليًا
db_url = os.environ.get("DATABASE_URL")
if db_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ تسجيل الـ Blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(survey_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix_