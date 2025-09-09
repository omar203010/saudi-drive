import os
import io
import qrcode
from flask import Flask, send_from_directory, Response, request

from src.models.user import db
from src.routes.user import user_bp
from src.routes.survey import survey_bp
from src.routes.admin import admin_bp

app = Flask(__name__)

# 🔑 المفتاح السري من Environment Variable (مع افتراضي محلي)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# 🔗 إعداد رابط قاعدة البيانات
db_url = os.environ.get("DATABASE_URL", "").strip()

# بعض المنصات (مثل Render/Heroku) ترجع postgres:// → نبدلها بـ postgresql+psycopg://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# fallback: إذا ما فيه DATABASE_URL → نستخدم SQLite محليًا
if not db_url:
    db_url = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# فرض SSL إذا قاعدة البيانات PostgreSQL (مهم مع Render)
if "postgresql+psycopg://" in db_url:
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"].setdefault("connect_args", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"]["connect_args"].setdefault("sslmode", "require")

# ✅ تسجيل الـ Blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(survey_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/")

# ✅ تهيئة قاعدة البيانات وإنشاء الجداول عند الحاجة
db.init_app(app)
with app.app_context():
    db.create_all()

# ✅ خدمة الملفات الثابتة (Static Files)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path: str):
    """تقديم الملفات الثابتة (HTML, CSS, JS, صور)."""
    if path == "":
        return send_from_directory(STATIC_DIR, "index.html")
    return send_from_directory(STATIC_DIR, path)

# 🔎 Route لفحص قاعدة البيانات المستخدمة
@app.route("/debug/db")
def debug_db():
    """إظهار نوع قاعدة البيانات المتصل بها التطبيق."""
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if "postgresql+psycopg://" in db_uri:
        return f"✅ التطبيق متصل بـ PostgreSQL (psycopg3)<br>URI: {db_uri}"
    elif "sqlite://" in db_uri:
        return f"⚠️ التطبيق يستخدم SQLite (مؤقت على Render)<br>URI: {db_uri}"
    else:
        return f"❓ قاعدة البيانات غير معروفة<br>URI: {db_uri}"

# 🧾 صورة الباركود (PNG) — يمكن استخدامها للطباعة أو الإدراج في مواد تسويقية
@app.route("/qr.png")
def qr_png():
    # عدّل هذا لو عندك صفحة استبيان مخصصة غير الصفحة الرئيسية
    survey_url = request.host_url  # مثال: https://YOUR-SERVICE.onrender.com/
    qr = qrcode.QRCode(version=2, box_size=12, border=2)
    qr.add_data(survey_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = Response(buf.getvalue(), mimetype="image/png")
    resp.headers["Cache-Control"] = "public, max-age=86400"  # يوم كامل
    return resp

# 🖼️ صفحة أنيقة تعرض الباركود مع لمسات سعودية وأزرار
@app.route("/qr")
def qr_page():
    survey_url = request.host_url  # غيّرها لمسار الاستبيان لو عندك صفحة محددة
    html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>استبيان — ليكون التطبيق يرضيكم</title>
<style>
  :root {{ --green:#0a7a3c; --green-dark:#075c2d; --bg:#f7faf8; --text:#0f172a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font-family:"Tajawal", system-ui, -apple-system, "Segoe UI", Arial, sans-serif; }}
  .wrap {{ min-height:100dvh; display:grid; place-items:center; padding:24px; }}
  .card {{ width:100%; max-width:920px; background:#fff; border-radius:24px; padding:28px;
          box-shadow:0 10px 30px rgba(0,0,0,.08); border:1px solid #eef2ee; }}
  .header {{ display:grid; gap:8px; align-items:center; grid-template-columns:auto 1fr; margin-bottom:22px; }}
  .flag {{ width:56px; height:56px; border-radius:14px; background:var(--green); display:grid; place-items:center;
           color:#fff; font-size:28px; user-select:none; box-shadow:inset 0 0 0 2px rgba(255,255,255,.18); }}
  h1 {{ margin:0; font-size:28px; line-height:1.25; }}
  .sub {{ color:#475569; font-size:15px; margin-top:-2px; }}
  .grid {{ display:grid; gap:24px; grid-template-columns:1fr 1fr; }}
  @media (max-width:860px) {{ .grid {{ grid-template-columns:1fr; }} }}
  .qr-box {{ border:1px dashed #d9e5da; border-radius:16px; padding:18px; display:grid; place-items:center; background:#f9fcf9; }}
  .qr-img {{ width:100%; max-width:340px; aspect-ratio:1/1; background:#fff; border-radius:12px; padding:14px;
             box-shadow:0 6px 20px rgba(10,122,60,.12); }}
  .actions {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:16px; }}
  .btn {{ appearance:none; border:none; cursor:pointer; font-weight:700; border-radius:999px; padding:12px 20px; font-size:15px;
          transition:transform .12s ease, box-shadow .12s ease, background .2s ease; }}
  .btn-primary {{ background:var(--green); color:#fff; box-shadow:0 8px 20px rgba(10,122,60,.20); }}
  .btn-primary:hover {{ background:var(--green-dark); transform:translateY(-1px); }}
  .btn-ghost {{ background:transparent; color:var(--green); border:1px solid rgba(10,122,60,.25); }}
  .btn-ghost:hover {{ background:rgba(10,122,60,.06); }}
  .quote {{ background:linear-gradient(135deg, rgba(10,122,60,.07), rgba(10,122,60,.03));
            border:1px solid rgba(10,122,60,.12); border-radius:16px; padding:18px; }}
  .quote h3 {{ margin:0 0 8px 0; font-size:18px; color:var(--green-dark); }}
  .quote p {{ margin:0; color:#334155; line-height:1.8; }}
  .footer {{ margin-top:22px; display:flex; gap:10px; align-items:center; color:#64748b; font-size:13px; flex-wrap:wrap; }}
  @media print {{ .btn, .actions, .footer {{ display:none !important; }} .card {{ box-shadow:none; border:none; }} .qr-img {{ box-shadow:none; }} }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="header">
        <div class="flag" aria-hidden="true">🇸🇦</div>
        <div>
          <h1>استبيان — ليكون التطبيق يرضيكم</h1>
          <div class="sub">ساهم برأيك في تطوير <strong>Saudi Drive</strong> — نعتز بملاحظاتك</div>
        </div>
      </div>
      <div class="grid">
        <div class="qr-box">
          <img class="qr-img" src="/qr.png" alt="QR Code — افتح الاستبيان" />
        </div>
        <div>
          <div class="quote" role="note" aria-label="اقتباس ملهم">
            <h3>عنوان: <em>نكمل بعضنا</em></h3>
            <p>«نكمل بعضنا» — نجاحنا بتضافر الجهود ومشاركة الآراء البنّاءة.</p>
          </div>
          <div class="actions">
            <a class="btn btn-primary" href="{survey_url}" target="_blank" rel="noopener">افتح الاستبيان الآن</a>
            <button class="btn btn-ghost" onclick="window.print()">طباعة الصفحة</button>
          </div>
          <div class="footer">
            <span>امسح الباركود بكاميرا الجوال لفتح الاستبيان فورًا.</span>
            <span>أو اضغط زر <strong>افتح الاستبيان الآن</strong>.</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
    return Response(html, mimetype="text/html; charset=utf-8")

# ✅ نقطة تشغيل التطبيق
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("DEBUG", "False") == "True"
    )
