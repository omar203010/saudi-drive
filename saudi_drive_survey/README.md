# 🇸🇦 سعودي درايف - استبيان التطبيق السعودي للتوصيل

## 📋 نظرة عامة

استبيان تفاعلي لجمع آراء واقتراحات العملاء حول تطبيق "سعودي درايف" - التطبيق السعودي 100% للتوصيل الذي يدعم السائقين السعوديين بدون أخذ أي نسبة من دخلهم.

## ✨ المميزات

### 🎨 **التصميم**
- تصميم سعودي أصيل بالألوان الوطنية
- واجهة سهلة ومتجاوبة مع جميع الأجهزة
- علم المملكة العربية السعودية
- مقولات الأمير محمد بن سلمان

### 📊 **الاستبيان**
- جميع الحقول اختيارية (لا إجبار)
- أسئلة شاملة عن تطبيقات التوصيل الحالية
- تجميع اقتراحات العملاء والميزات المطلوبة
- دعم خدمة "كابتنة لكابتنة" بسعر عادل

### 🛡️ **حماية البيانات**
- نظام حماية متعدد الطبقات
- نسخ احتياطية تلقائية كل ساعة
- حفظ البيانات لمدة 5 أشهر
- استعادة تلقائية في حالة التلف

### 🔐 **لوحة التحكم الآمنة**
- تسجيل دخول محمي
- عرض جميع الردود مع تفاصيل كاملة
- إحصائيات مباشرة
- تصدير البيانات (Excel + JSON)

## 🚀 التثبيت والتشغيل

### 1️⃣ **متطلبات النظام**
```bash
Python 3.8+
Flask
SQLAlchemy
Schedule
```

### 2️⃣ **التثبيت**
```bash
# استنساخ المشروع
git clone https://github.com/your-username/saudi-drive-survey.git
cd saudi-drive-survey

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 3️⃣ **التشغيل العادي**
```bash
cd src
python main.py
```

### 4️⃣ **التشغيل مع حماية البيانات**
```bash
python start_with_persistence.py
```

## 📁 بنية المشروع

```
saudi_drive_survey/
├── src/
│   ├── main.py              # الملف الرئيسي
│   ├── database/            # قاعدة البيانات
│   │   └── app.db          # SQLite database
│   ├── models/             # نماذج البيانات
│   │   ├── user.py         # نموذج المستخدم
│   │   └── survey.py       # نموذج الاستبيان
│   ├── routes/             # مسارات API
│   │   ├── user.py         # مسارات المستخدم
│   │   ├── survey.py       # مسارات الاستبيان
│   │   └── admin.py        # لوحة التحكم
│   └── static/             # الواجهات والتصميم
│       ├── index.html      # صفحة الاستبيان
│       ├── styles.css      # التصميم السعودي
│       ├── script.js       # التفاعل والوظائف
│       └── saudi_flag.jpg  # علم السعودية
├── backup_database.py      # نسخ احتياطي
├── persistent_database.py  # حماية البيانات
├── start_with_persistence.py # تشغيل محمي
└── requirements.txt        # المتطلبات
```

## 🔗 الروابط

### 📋 **الاستبيان العام:**
```
https://your-domain.com
```

### 🛡️ **لوحة التحكم:**
```
https://your-domain.com/admin
```

## 🔐 بيانات الدخول الافتراضية

- **اسم المستخدم:** `omar_admin`
- **كلمة المرور:** `SaudiDrive2025!`

⚠️ **مهم:** غيّر بيانات الدخول بعد التثبيت!

## 📊 API المتاحة

### 📝 **إرسال استبيان:**
```http
POST /api/survey/submit
Content-Type: application/json

{
  "name": "اسم العميل",
  "gender": "ذكر",
  "phone": "0551234567",
  "current_app": "أوبر",
  "usage_frequency": "يومياً",
  "important_factors": ["السعر", "الأمان"],
  "customer_suggestions": "اقتراحات العميل..."
}
```

### 📈 **الحصول على الإحصائيات:**
```http
GET /api/survey/stats
```

### 📋 **جميع الردود:**
```http
GET /api/survey/responses
```

## 🛡️ نظام حماية البيانات

### 🔄 **النسخ الاحتياطي التلقائي:**
- نسخة كل ساعة
- نسخة يومية في منتصف الليل
- حفظ في مواقع متعددة
- تصدير JSON مع كل نسخة

### 📁 **مواقع النسخ:**
```
/backups/local/     # نسخ محلية
/backups/cloud/     # نسخ سحابية
```

### 🔧 **أدوات الصيانة:**
```bash
# نسخة احتياطية فورية
python backup_database.py

# فحص سلامة قاعدة البيانات
python persistent_database.py

# عرض الإحصائيات
python -c "from persistent_database import PersistentDatabase; PersistentDatabase().get_statistics()"
```

## 🌐 النشر على الاستضافة

### 1️⃣ **Heroku:**
```bash
# إنشاء تطبيق Heroku
heroku create saudi-drive-survey

# رفع المشروع
git push heroku main

# تشغيل قاعدة البيانات
heroku run python src/main.py
```

### 2️⃣ **Railway:**
```bash
# ربط مع Railway
railway login
railway init
railway up
```

### 3️⃣ **DigitalOcean App Platform:**
- رفع المشروع على GitHub
- ربط مع DigitalOcean
- تحديد `src/main.py` كنقطة البداية

## 📱 QR Code

يتم إنشاء QR Code تلقائياً مع:
- تصميم سعودي أصيل
- الألوان الوطنية
- علم المملكة
- معلومات التواصل

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📞 التواصل

- **المطور:** عمر من فريق سعودي درايف
- **الهاتف:** 0551755479
- **البريد الإلكتروني:** omar@saudidrive.com

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

- فريق سعودي درايف
- المجتمع السعودي للتطوير
- جميع المساهمين في المشروع

---

**🇸🇦 نكمل بعضنا - سعودي درايف**

*تطبيق سعودي 100% يدعم السائقين السعوديين بدون أخذ أي نسبة من دخلهم*

