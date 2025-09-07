#!/usr/bin/env python3
"""
سكريبت بدء تطبيق سعودي درايف مع ضمان استمرارية البيانات
يضمن عدم فقدان البيانات أبداً
"""

import os
import sys
import threading
import time
from persistent_database import PersistentDatabase

# إضافة مسار المشروع إلى Python path
sys.path.insert(0, '/home/ubuntu/saudi_drive_survey/src')

from main import app

def start_database_system():
    """بدء نظام ضمان استمرارية قاعدة البيانات"""
    
    print("🔧 بدء نظام حماية البيانات...")
    
    # إنشاء نظام قاعدة البيانات المستمرة
    db_system = PersistentDatabase()
    
    # إنشاء نسخة احتياطية فورية
    db_system.create_backup()
    
    # بدء النسخ الاحتياطي التلقائي
    db_system.start_automatic_backup()
    
    print("✅ نظام حماية البيانات جاهز!")
    print("📅 البيانات محمية لمدة 5 أشهر")
    print("🔄 نسخ احتياطية تلقائية كل ساعة")
    
    return db_system

def monitor_database():
    """مراقبة قاعدة البيانات باستمرار"""
    
    db_system = PersistentDatabase()
    
    while True:
        try:
            # فحص سلامة قاعدة البيانات كل 10 دقائق
            db_system.verify_database_integrity()
            time.sleep(600)  # 10 دقائق
            
        except Exception as e:
            print(f"⚠️ خطأ في مراقبة قاعدة البيانات: {e}")
            time.sleep(60)  # إعادة المحاولة بعد دقيقة

def main():
    """الدالة الرئيسية"""
    
    print("🚀 بدء تطبيق سعودي درايف مع حماية البيانات...")
    
    # بدء نظام حماية البيانات
    db_system = start_database_system()
    
    # بدء مراقبة قاعدة البيانات في خيط منفصل
    monitor_thread = threading.Thread(target=monitor_database, daemon=True)
    monitor_thread.start()
    
    print("🌐 بدء خادم الويب...")
    
    # تشغيل التطبيق
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # إيقاف وضع التطوير لضمان الاستقرار
            threaded=True  # دعم عدة اتصالات متزامنة
        )
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف التطبيق بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        
        # إنشاء نسخة احتياطية طارئة قبل الإغلاق
        print("💾 إنشاء نسخة احتياطية طارئة...")
        db_system.create_backup()
        
    finally:
        print("📊 إحصائيات نهائية:")
        db_system.get_statistics()
        print("✅ تم إغلاق التطبيق بأمان")

if __name__ == "__main__":
    main()

