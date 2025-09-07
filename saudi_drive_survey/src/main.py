from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.survey import survey_bp
from src.routes.admin import admin_bp
import os

app = Flask(__name__)

# إعداد المفتاح السري للجلسات الآمنة
app.secret_key = 'SaudiDrive2025_SecureKey_Omar_Admin_Panel'

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(survey_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == '':
        return send_from_directory('static', 'index.html')
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

