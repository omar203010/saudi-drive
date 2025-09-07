import os
from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.survey import survey_bp
from src.routes.admin import admin_bp

app = Flask(__name__)

# 🔑 المفتاح السري من Environment Variable (مع افتراضي محلي)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# 🔗 تهيئة قاعدة البيانات
db_url = os.environ.get("DATABASE_URL", "").strip()

# بعض المنصات (Render/Heroku) ترجع postgres:// → لازم يتحول إلى postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# إذا ما فيه DATABASE_URL → نستخدم SQLite محليًا
if not db_url:
    db_url = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# فرض SSL على PostgreSQL في بيئة السحابة
if "postgresql://" in db_url:
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"].setdefault("connect_args", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["connect_args"].setdefault("sslmode", "require")

# ✅ تسجيل الـ Blueprints
app.register_blueprint(user_bp,   url_prefix="/api")
app.register_blueprint(survey_bp, url_prefix="/api")
app.register_blueprint(admin_bp,  url_prefix="/")

# ✅ تهيئة قاعدة البيانات
db.init_app(app)
with app.app_context():
    db.create_all()

# ✅ الملفات الثابتة (Static Files)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path: str):
    if path == "":
        return send_from_directory(STATIC_DIR, "index.html")
    return send_from_directory(STATIC_DIR, path)

# 🔎 Route لفحص قاعدة البيانات المستخدمة
@app.route("/debug/db")
def debug_db():
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if "postgresql://" in db_uri:
        return f"✅ التطبيق متصل بـ PostgreSQL<br>URI: {db_uri}"
    elif "sqlite://" in db_uri:
        return f"⚠️ التطبيق يستخدم SQLite (مؤقت على Render)<br>URI: {db_uri}"
    else:
        return f"❓ قاعدة البيانات غير معروفة<br>URI: {db_uri}"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("DEBUG", "False") == "True"
    )
