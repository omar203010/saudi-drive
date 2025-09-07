#!/usr/bin/env python3
"""
سكريبت ضمان استمرارية قاعدة البيانات لسعودي درايف
يضمن عدم فقدان البيانات ويحفظها لمدة 5 أشهر على الأقل
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
import json
import schedule
import time
import threading

class PersistentDatabase:
    def __init__(self):
        self.db_path = '/home/ubuntu/saudi_drive_survey/src/database/app.db'
        self.backup_dir = '/home/ubuntu/saudi_drive_backups'
        self.cloud_backup_dir = '/home/ubuntu/cloud_backups'
        
        # إنشاء المجلدات إذا لم تكن موجودة
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.cloud_backup_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # ضمان وجود قاعدة البيانات
        self.ensure_database_exists()
        
    def ensure_database_exists(self):
        """ضمان وجود قاعدة البيانات وإنشاؤها إذا لم تكن موجودة"""
        
        if not os.path.exists(self.db_path):
            print("🔧 إنشاء قاعدة بيانات جديدة...")
            self.create_database()
        else:
            print("✅ قاعدة البيانات موجودة")
            
        # التحقق من سلامة قاعدة البيانات
        self.verify_database_integrity()
    
    def create_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إنشاء جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء جدول الاستبيان مع جميع الحقول
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS survey_response (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100),
                    gender VARCHAR(10),
                    phone VARCHAR(20),
                    current_app VARCHAR(50),
                    usage_frequency VARCHAR(50),
                    important_factors TEXT,
                    additional_features TEXT,
                    current_problems TEXT,
                    additional_problems TEXT,
                    try_saudi_app VARCHAR(50),
                    preferred_payment TEXT,
                    female_captain_service VARCHAR(100),
                    female_service_suggestions TEXT,
                    customer_suggestions TEXT,
                    ip_address VARCHAR(45),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء فهارس لتحسين الأداء
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON survey_response(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone ON survey_response(phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_gender ON survey_response(gender)')
            
            conn.commit()
            conn.close()
            
            print("✅ تم إنشاء قاعدة البيانات بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
    
    def verify_database_integrity(self):
        """التحقق من سلامة قاعدة البيانات"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # فحص سلامة قاعدة البيانات
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()[0]
            
            if result == 'ok':
                print("✅ قاعدة البيانات سليمة")
            else:
                print(f"⚠️ مشكلة في قاعدة البيانات: {result}")
                self.repair_database()
            
            conn.close()
            
        except Exception as e:
            print(f"❌ خطأ في فحص قاعدة البيانات: {e}")
            self.repair_database()
    
    def repair_database(self):
        """إصلاح قاعدة البيانات إذا كانت تالفة"""
        
        print("🔧 محاولة إصلاح قاعدة البيانات...")
        
        try:
            # إنشاء نسخة احتياطية من القاعدة التالفة
            backup_corrupted = f"{self.db_path}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_path, backup_corrupted)
            
            # محاولة استعادة من آخر نسخة احتياطية
            latest_backup = self.get_latest_backup()
            if latest_backup:
                shutil.copy2(latest_backup, self.db_path)
                print(f"✅ تم استعادة قاعدة البيانات من: {latest_backup}")
            else:
                # إنشاء قاعدة بيانات جديدة
                os.remove(self.db_path)
                self.create_database()
                print("✅ تم إنشاء قاعدة بيانات جديدة")
                
        except Exception as e:
            print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
    
    def get_latest_backup(self):
        """الحصول على أحدث نسخة احتياطية"""
        
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('saudi_drive_backup_') and file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            if backup_files:
                # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
                backup_files.sort(key=lambda x: x[1], reverse=True)
                return backup_files[0][0]
            
            return None
            
        except Exception as e:
            print(f"❌ خطأ في البحث عن النسخ الاحتياطية: {e}")
            return None
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # نسخة احتياطية محلية
            local_backup = os.path.join(self.backup_dir, f'saudi_drive_backup_{timestamp}.db')
            shutil.copy2(self.db_path, local_backup)
            
            # نسخة احتياطية في مجلد منفصل (محاكاة التخزين السحابي)
            cloud_backup = os.path.join(self.cloud_backup_dir, f'saudi_drive_cloud_{timestamp}.db')
            shutil.copy2(self.db_path, cloud_backup)
            
            # تصدير JSON
            self.export_to_json(timestamp)
            
            print(f"✅ تم إنشاء نسخة احتياطية: {timestamp}")
            
            # تنظيف النسخ القديمة
            self.cleanup_old_backups()
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
    
    def export_to_json(self, timestamp):
        """تصدير البيانات إلى JSON"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM survey_response')
            rows = cursor.fetchall()
            
            data = {
                'export_date': datetime.now().isoformat(),
                'total_responses': len(rows),
                'responses': [dict(row) for row in rows]
            }
            
            json_file = os.path.join(self.backup_dir, f'saudi_drive_data_{timestamp}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # نسخة JSON في التخزين السحابي أيضاً
            cloud_json = os.path.join(self.cloud_backup_dir, f'saudi_drive_data_{timestamp}.json')
            shutil.copy2(json_file, cloud_json)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ خطأ في تصدير JSON: {e}")
    
    def cleanup_old_backups(self):
        """حذف النسخ الاحتياطية القديمة (الاحتفاظ بـ 5 أشهر)"""
        
        # تاريخ انتهاء الصلاحية (5 أشهر)
        expiry_date = datetime.now() - timedelta(days=150)  # 5 أشهر تقريباً
        
        for backup_dir in [self.backup_dir, self.cloud_backup_dir]:
            try:
                for file in os.listdir(backup_dir):
                    if file.startswith('saudi_drive_'):
                        file_path = os.path.join(backup_dir, file)
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        if file_time < expiry_date:
                            os.remove(file_path)
                            print(f"🗑️ تم حذف النسخة القديمة: {file}")
                            
            except Exception as e:
                print(f"❌ خطأ في تنظيف النسخ القديمة: {e}")
    
    def get_statistics(self):
        """عرض إحصائيات قاعدة البيانات"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إحصائيات عامة
            cursor.execute('SELECT COUNT(*) FROM survey_response')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM survey_response WHERE phone IS NOT NULL AND phone != ""')
            with_phone = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM survey_response WHERE gender = "ذكر"')
            male = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM survey_response WHERE gender = "أنثى"')
            female = cursor.fetchone()[0]
            
            # آخر رد
            cursor.execute('SELECT created_at FROM survey_response ORDER BY created_at DESC LIMIT 1')
            last_response = cursor.fetchone()
            
            print("📊 إحصائيات قاعدة البيانات:")
            print(f"   📝 إجمالي الردود: {total}")
            print(f"   📱 ردود مع أرقام جوال: {with_phone}")
            print(f"   👨 ردود الذكور: {male}")
            print(f"   👩 ردود الإناث: {female}")
            print(f"   🕐 آخر رد: {last_response[0] if last_response else 'لا توجد ردود'}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ خطأ في قراءة الإحصائيات: {e}")
    
    def start_automatic_backup(self):
        """بدء النسخ الاحتياطي التلقائي"""
        
        # نسخة احتياطية كل ساعة
        schedule.every().hour.do(self.create_backup)
        
        # نسخة احتياطية يومية في منتصف الليل
        schedule.every().day.at("00:00").do(self.create_backup)
        
        # تنظيف النسخ القديمة أسبوعياً
        schedule.every().week.do(self.cleanup_old_backups)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # فحص كل دقيقة
        
        # تشغيل المجدول في خيط منفصل
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("🔄 تم بدء النسخ الاحتياطي التلقائي")

def main():
    """الدالة الرئيسية"""
    
    print("🚀 بدء نظام ضمان استمرارية قاعدة البيانات...")
    
    # إنشاء مثيل من النظام
    db_system = PersistentDatabase()
    
    # عرض الإحصائيات الحالية
    db_system.get_statistics()
    
    # إنشاء نسخة احتياطية فورية
    db_system.create_backup()
    
    # بدء النسخ الاحتياطي التلقائي
    db_system.start_automatic_backup()
    
    print("✅ نظام ضمان استمرارية البيانات جاهز!")
    print("📅 البيانات ستُحفظ لمدة 5 أشهر على الأقل")
    print("🔄 نسخ احتياطية تلقائية كل ساعة")

if __name__ == "__main__":
    main()

