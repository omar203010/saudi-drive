import os
from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.survey import survey_bp
from src.routes.admin import admin_bp

app = Flask(__name__)

# 🔑 السر من المتغيرات البيئية (مع افتراضي محلي)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# 🔗 تهيئة قاعدة البيانات
db_url = os.environ.get("DATABASE_URL", "").strip()

# Render/Supabase/Heroku قد تُرجِع postgres:// ويجب تحويله إلى postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    # تشغيل محلي باستخدام SQLite إذا ما وُجد DATABASE_URL
    db_url = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# فرض SSL على اتصال PostgreSQL في بيئة السحابة
if "postgresql://" in db_url:
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"].setdefault("connect_args", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["connect_args"].setdefault("sslmode", "require")

# ✅ تسجيل الـ Blueprints (السطر الذي كان فيه الخطأ)
app.register_blueprint(user_bp,   url_prefix="/api")
app.register_blueprint(survey_bp, url_prefix="/api")
app.register_blueprint(admin_bp,  url_prefix="/")

# ✅ تهيئة قاعدة البيانات
db.init_app(app)
with app.app_context():
    db.create_all()

# ✅ تقديم الملفات الثابتة من مسار مطلق
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path: str):
    if path == "":
        return send_from_directory(STATIC_DIR, "index.html")
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("DEBUG", "False") == "True")
