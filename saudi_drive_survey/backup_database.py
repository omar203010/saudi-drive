#!/usr/bin/env python3
"""
سكريبت النسخ الاحتياطي لقاعدة بيانات سعودي درايف
يحفظ نسخة احتياطية من قاعدة البيانات كل ساعة
"""

import sqlite3
import shutil
import os
from datetime import datetime
import json

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    
    # مسارات الملفات
    source_db = '/home/ubuntu/saudi_drive_survey/src/database/app.db'
    backup_dir = '/home/ubuntu/saudi_drive_backups'
    
    # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
    os.makedirs(backup_dir, exist_ok=True)
    
    # تاريخ ووقت النسخة الاحتياطية
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'saudi_drive_backup_{timestamp}.db')
    
    try:
        # نسخ قاعدة البيانات
        shutil.copy2(source_db, backup_file)
        
        # تصدير البيانات إلى JSON أيضاً
        export_to_json(source_db, backup_dir, timestamp)
        
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        
        # حذف النسخ القديمة (الاحتفاظ بآخر 100 نسخة)
        cleanup_old_backups(backup_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return False

def export_to_json(db_path, backup_dir, timestamp):
    """تصدير البيانات إلى ملف JSON"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
        cursor = conn.cursor()
        
        # استخراج جميع البيانات
        cursor.execute('SELECT * FROM survey_response')
        rows = cursor.fetchall()
        
        # تحويل إلى قائمة من القواميس
        data = []
        for row in rows:
            data.append(dict(row))
        
        # حفظ في ملف JSON
        json_file = os.path.join(backup_dir, f'saudi_drive_data_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ تم تصدير البيانات إلى JSON: {json_file}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في تصدير JSON: {e}")

def cleanup_old_backups(backup_dir, keep_count=100):
    """حذف النسخ الاحتياطية القديمة"""
    
    try:
        # الحصول على جميع ملفات النسخ الاحتياطية
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith('saudi_drive_backup_') and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                backup_files.append((file_path, os.path.getctime(file_path)))
        
        # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # حذف الملفات الزائدة
        if len(backup_files) > keep_count:
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                print(f"🗑️ تم حذف النسخة القديمة: {os.path.basename(file_path)}")
                
    except Exception as e:
        print(f"❌ خطأ في تنظيف النسخ القديمة: {e}")

def restore_database(backup_file):
    """استعادة قاعدة البيانات من نسخة احتياطية"""
    
    source_db = '/home/ubuntu/saudi_drive_survey/src/database/app.db'
    
    try:
        # إنشاء نسخة احتياطية من الحالة الحالية أولاً
        current_backup = f"{source_db}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(source_db, current_backup)
        
        # استعادة من النسخة الاحتياطية
        shutil.copy2(backup_file, source_db)
        
        print(f"✅ تم استعادة قاعدة البيانات من: {backup_file}")
        print(f"📁 النسخة السابقة محفوظة في: {current_backup}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في استعادة قاعدة البيانات: {e}")
        return False

def get_database_stats():
    """عرض إحصائيات قاعدة البيانات"""
    
    db_path = '/home/ubuntu/saudi_drive_survey/src/database/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # عدد الردود
        cursor.execute('SELECT COUNT(*) FROM survey_response')
        total_responses = cursor.fetchone()[0]
        
        # عدد الردود مع أرقام الجوال
        cursor.execute('SELECT COUNT(*) FROM survey_response WHERE phone IS NOT NULL AND phone != ""')
        responses_with_phone = cursor.fetchone()[0]
        
        # آخر رد
        cursor.execute('SELECT created_at FROM survey_response ORDER BY created_at DESC LIMIT 1')
        last_response = cursor.fetchone()
        last_response_time = last_response[0] if last_response else "لا توجد ردود"
        
        print("📊 إحصائيات قاعدة البيانات:")
        print(f"   📝 إجمالي الردود: {total_responses}")
        print(f"   📱 ردود مع أرقام جوال: {responses_with_phone}")
        print(f"   🕐 آخر رد: {last_response_time}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الإحصائيات: {e}")

if __name__ == "__main__":
    print("🔄 بدء النسخ الاحتياطي لقاعدة بيانات سعودي درايف...")
    
    # عرض الإحصائيات الحالية
    get_database_stats()
    
    # إنشاء نسخة احتياطية
    if backup_database():
        print("✅ تم إنجاز النسخ الاحتياطي بنجاح!")
    else:
        print("❌ فشل في إنشاء النسخة الاحتياطية!")

