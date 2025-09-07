from flask import Blueprint, request, jsonify, render_template_string, session, redirect, url_for
from src.models.survey import SurveyResponse
from src.models.user import db
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# بيانات الدخول الآمنة (يمكنك تغييرها)
ADMIN_USERNAME = "omar_admin"
ADMIN_PASSWORD_HASH = generate_password_hash("SaudiDrive2025!")  # كلمة المرور: SaudiDrive2025!

# صفحة تسجيل الدخول
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم سعودي درايف</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Tajawal', Arial, sans-serif;
            background: linear-gradient(135deg, #006C35, #00A651);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .logo {
            color: #006C35;
            font-size: 2rem;
            font-weight: 900;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: right;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            font-family: 'Tajawal', Arial, sans-serif;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #006C35;
        }
        .login-btn {
            width: 100%;
            background: linear-gradient(45deg, #006C35, #00A651);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s;
            font-family: 'Tajawal', Arial, sans-serif;
        }
        .login-btn:hover {
            transform: translateY(-2px);
        }
        .error {
            color: #ff4444;
            margin-top: 15px;
            padding: 10px;
            background: #ffe6e6;
            border-radius: 5px;
        }
        .security-note {
            margin-top: 20px;
            padding: 15px;
            background: #f0f8ff;
            border-radius: 10px;
            font-size: 0.9rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🛡️ سعودي درايف</div>
        <div class="subtitle">لوحة التحكم الآمنة</div>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">اسم المستخدم:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">كلمة المرور:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">تسجيل الدخول</button>
        </form>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <div class="security-note">
            🔒 هذه لوحة تحكم آمنة محمية بكلمة مرور قوية
        </div>
    </div>
</body>
</html>
"""

# صفحة لوحة التحكم
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم سعودي درايف - البيانات</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Tajawal', Arial, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(45deg, #006C35, #00A651);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo { font-size: 1.5rem; font-weight: 900; }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }
        .container { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 900;
            color: #006C35;
            margin-bottom: 5px;
        }
        .stat-label { color: #666; }
        .data-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .section-header {
            background: #006C35;
            color: white;
            padding: 15px 20px;
            font-weight: 600;
        }
        .table-container {
            overflow-x: auto;
            max-height: 800px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }
        th, td {
            padding: 15px 10px;
            text-align: right;
            border-bottom: 1px solid #eee;
            vertical-align: top;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        /* تحديد عرض الأعمدة */
        .col-id { width: 60px; }
        .col-name { width: 120px; }
        .col-gender { width: 80px; }
        .col-phone { width: 120px; }
        .col-app { width: 100px; }
        .col-frequency { width: 100px; }
        .col-factors { width: 200px; }
        .col-additional-features { width: 250px; }
        .col-problems { width: 200px; }
        .col-additional-problems { width: 250px; }
        .col-try-app { width: 100px; }
        .col-payment { width: 150px; }
        .col-female-service { width: 150px; }
        .col-female-suggestions { width: 250px; }
        .col-suggestions { width: 300px; }
        .col-date { width: 120px; }
        .col-ip { width: 100px; }
        
        /* تنسيق النصوص الطويلة */
        .text-content {
            max-height: 150px;
            overflow-y: auto;
            line-height: 1.4;
            font-size: 0.9rem;
            padding: 8px;
            background: #f9f9f9;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        
        .text-content:empty::before {
            content: "لا يوجد";
            color: #999;
            font-style: italic;
        }
        
        /* تمييز النصوص المهمة */
        .phone-highlight { 
            background: #fffacd; 
            font-weight: bold; 
            color: #006C35;
            padding: 5px;
            border-radius: 3px;
        }
        
        .important-text {
            background: #e8f5e8;
            padding: 8px;
            border-radius: 5px;
            border-left: 4px solid #006C35;
        }
        
        /* تحسين التمرير */
        .text-content::-webkit-scrollbar {
            width: 6px;
        }
        
        .text-content::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        
        .text-content::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        
        .text-content::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        tr:hover { 
            background: #f8f9fa; 
        }
        
        tr:hover .text-content {
            background: #ffffff;
        }
        
        .export-btn {
            background: #00A651;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }
        
        .export-btn:hover {
            background: #008a43;
        }
        
        /* تحسين الاستجابة للشاشات الصغيرة */
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .table-container {
                font-size: 0.8rem;
            }
            
            .text-content {
                max-height: 100px;
                font-size: 0.8rem;
            }
            
            th, td {
                padding: 8px 5px;
            }
        }
        
        /* تحسين طباعة الجدول */
        @media print {
            .header, .export-btn {
                display: none;
            }
            
            .table-container {
                max-height: none;
                overflow: visible;
            }
            
            .text-content {
                max-height: none;
                overflow: visible;
                border: none;
                background: transparent;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🛡️ لوحة تحكم سعودي درايف</div>
        <a href="/admin/logout" class="logout-btn">تسجيل الخروج</a>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_responses }}</div>
                <div class="stat-label">إجمالي الردود</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.responses_with_phone }}</div>
                <div class="stat-label">ردود مع رقم الجوال</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.male_responses }}</div>
                <div class="stat-label">ردود الذكور</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.female_responses }}</div>
                <div class="stat-label">ردود الإناث</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.captain_to_captain_preference }}</div>
                <div class="stat-label">يفضلون كابتنة لكابتنة</div>
            </div>
        </div>
        
        <div class="data-section">
            <div class="section-header">
                بيانات الاستبيان
                <a href="/admin/export" class="export-btn">تصدير Excel</a>
                <a href="/admin/export-phones" class="export-btn">تصدير أرقام الجوال فقط</a>
            </div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="col-id">ID</th>
                            <th class="col-name">الاسم</th>
                            <th class="col-gender">الجنس</th>
                            <th class="col-phone">رقم الجوال</th>
                            <th class="col-app">التطبيق الحالي</th>
                            <th class="col-frequency">تكرار الاستخدام</th>
                            <th class="col-factors">العوامل المهمة</th>
                            <th class="col-additional-features">ميزات إضافية مطلوبة</th>
                            <th class="col-problems">المشاكل الحالية</th>
                            <th class="col-additional-problems">مشاكل إضافية</th>
                            <th class="col-try-app">تجربة التطبيق السعودي</th>
                            <th class="col-payment">طرق الدفع المفضلة</th>
                            <th class="col-female-service">خدمة الكابتنة</th>
                            <th class="col-female-suggestions">اقتراحات الكابتنة</th>
                            <th class="col-suggestions">اقتراحات العملاء</th>
                            <th class="col-date">التاريخ</th>
                            <th class="col-ip">IP</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for response in responses %}
                        <tr>
                            <td class="col-id">{{ response.id }}</td>
                            <td class="col-name">{{ response.name or '-' }}</td>
                            <td class="col-gender">{{ response.gender or '-' }}</td>
                            <td class="col-phone {% if response.phone %}phone-highlight{% endif %}">
                                {{ response.phone or '-' }}
                            </td>
                            <td class="col-app">{{ response.current_app or '-' }}</td>
                            <td class="col-frequency">{{ response.usage_frequency or '-' }}</td>
                            <td class="col-factors">
                                <div class="text-content">{{ response.important_factors or '' }}</div>
                            </td>
                            <td class="col-additional-features">
                                <div class="text-content important-text">{{ response.additional_features or '' }}</div>
                            </td>
                            <td class="col-problems">
                                <div class="text-content">{{ response.current_problems or '' }}</div>
                            </td>
                            <td class="col-additional-problems">
                                <div class="text-content important-text">{{ response.additional_problems or '' }}</div>
                            </td>
                            <td class="col-try-app">{{ response.try_saudi_app or '-' }}</td>
                            <td class="col-payment">
                                <div class="text-content">{{ response.preferred_payment or '' }}</div>
                            </td>
                            <td class="col-female-service">{{ response.female_captain_service or '-' }}</td>
                            <td class="col-female-suggestions">
                                <div class="text-content important-text">{{ response.female_service_suggestions or '' }}</div>
                            </td>
                            <td class="col-suggestions">
                                <div class="text-content important-text">{{ response.customer_suggestions or '' }}</div>
                            </td>
                            <td class="col-date">{{ response.created_at.strftime('%Y-%m-%d %H:%M') if response.created_at else '-' }}</td>
                            <td class="col-ip">{{ response.ip_address or '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

def check_auth():
    """التحقق من تسجيل الدخول"""
    return session.get('admin_logged_in') == True

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template_string(LOGIN_TEMPLATE, error="اسم المستخدم أو كلمة المرور غير صحيحة")
    
    return render_template_string(LOGIN_TEMPLATE)

@admin_bp.route('/admin/dashboard')
def dashboard():
    if not check_auth():
        return redirect('/admin/login')
    
    try:
        # جلب الإحصائيات
        total_responses = SurveyResponse.query.count()
        with_phone = SurveyResponse.query.filter(SurveyResponse.phone.isnot(None), SurveyResponse.phone != '').count()
        male_count = SurveyResponse.query.filter_by(gender='ذكر').count()
        female_count = SurveyResponse.query.filter_by(gender='أنثى').count()
        captain_to_captain_yes = SurveyResponse.query.filter_by(captain_to_captain='نعم').count()
        
        stats = {
            'total_responses': total_responses,
            'responses_with_phone': with_phone,
            'male_responses': male_count,
            'female_responses': female_count,
            'captain_to_captain_preference': captain_to_captain_yes
        }
        
        # جلب جميع الردود
        responses = SurveyResponse.query.order_by(SurveyResponse.created_at.desc()).all()
        
        return render_template_string(DASHBOARD_TEMPLATE, stats=stats, responses=responses)
    except Exception as e:
        return f"خطأ في جلب البيانات: {str(e)}"

@admin_bp.route('/admin/export')
def export_excel():
    if not check_auth():
        return redirect('/admin/login')
    
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        # جلب البيانات
        responses = SurveyResponse.query.order_by(SurveyResponse.created_at.desc()).all()
        
        # تحويل لـ DataFrame
        data = []
        for response in responses:
            data.append({
                'ID': response.id,
                'الاسم': response.name or '',
                'الجنس': response.gender or '',
                'رقم الجوال': response.phone or '',
                'اقتراحات الأسعار': response.price_suggestions or '',
                'طرق الدفع': response.payment_methods or '',
                'كابتنة لكابتنة': response.captain_to_captain or '',
                'اقتراحات العملاء': response.customer_suggestions or '',
                'تاريخ الإرسال': response.created_at.strftime('%Y-%m-%d %H:%M:%S') if response.created_at else '',
                'عنوان IP': response.ip_address or ''
            })
        
        df = pd.DataFrame(data)
        
        # حفظ في ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='بيانات الاستبيان', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'saudi_drive_survey_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return f"خطأ في تصدير البيانات: {str(e)}"

@admin_bp.route('/admin/export-phones')
def export_phones():
    if not check_auth():
        return redirect('/admin/login')
    
    try:
        # جلب أرقام الجوال فقط
        responses = SurveyResponse.query.filter(
            SurveyResponse.phone.isnot(None), 
            SurveyResponse.phone != ''
        ).order_by(SurveyResponse.created_at.desc()).all()
        
        phones_text = "أرقام جوال المشاركين في استبيان سعودي درايف\n"
        phones_text += "=" * 50 + "\n\n"
        
        for i, response in enumerate(responses, 1):
            phones_text += f"{i}. {response.phone}"
            if response.name:
                phones_text += f" - {response.name}"
            phones_text += f" ({response.created_at.strftime('%Y-%m-%d')})\n"
        
        phones_text += f"\n\nإجمالي الأرقام: {len(responses)}"
        
        from flask import Response
        return Response(
            phones_text,
            mimetype='text/plain; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename=saudi_drive_phones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'}
        )
    except Exception as e:
        return f"خطأ في تصدير أرقام الجوال: {str(e)}"

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

@admin_bp.route('/admin')
def admin_redirect():
    return redirect('/admin/login')

