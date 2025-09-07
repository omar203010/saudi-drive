from src.models.user import db
from datetime import datetime

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    
    # الأسئلة الجديدة للركاب
    current_app = db.Column(db.String(50), nullable=True)  # التطبيق المستخدم حالياً
    usage_frequency = db.Column(db.String(50), nullable=True)  # تكرار الاستخدام
    important_factors = db.Column(db.Text, nullable=True)  # العوامل المهمة (متعدد)
    additional_features = db.Column(db.Text, nullable=True)  # ميزات إضافية مطلوبة
    current_problems = db.Column(db.Text, nullable=True)  # المشاكل الحالية (متعدد)
    additional_problems = db.Column(db.Text, nullable=True)  # مشاكل إضافية
    try_saudi_app = db.Column(db.String(10), nullable=True)  # استعداد لتجربة التطبيق السعودي
    preferred_payment = db.Column(db.Text, nullable=True)  # طرق الدفع المفضلة (متعدد)
    female_captain_service = db.Column(db.String(100), nullable=True)  # خدمة الكابتنة
    female_service_suggestions = db.Column(db.Text, nullable=True)  # اقتراحات خدمة الكابتنة
    
    # الأسئلة القديمة (للتوافق مع النسخة السابقة)
    price_suggestions = db.Column(db.Text, nullable=True)
    payment_methods = db.Column(db.Text, nullable=True)
    captain_to_captain = db.Column(db.String(10), nullable=True)
    customer_suggestions = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'phone': self.phone,
            'current_app': self.current_app,
            'usage_frequency': self.usage_frequency,
            'important_factors': self.important_factors,
            'additional_features': self.additional_features,
            'current_problems': self.current_problems,
            'additional_problems': self.additional_problems,
            'try_saudi_app': self.try_saudi_app,
            'preferred_payment': self.preferred_payment,
            'female_captain_service': self.female_captain_service,
            'female_service_suggestions': self.female_service_suggestions,
            'price_suggestions': self.price_suggestions,
            'payment_methods': self.payment_methods,
            'captain_to_captain': self.captain_to_captain,
            'customer_suggestions': self.customer_suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ip_address': self.ip_address
        }

