import zipfile
import os
import datetime

def create_backup():
    """إنشاء نسخة احتياطية مضغوطة من المشروع"""
    # اسم الملف مع التاريخ والوقت
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f'saqr_training_system_backup_{timestamp}.zip'
    
    # قائمة الملفات والمجلدات المستبعدة
    exclude_dirs = ['__pycache__', '.git', 'node_modules', '.vscode']
    exclude_files = ['.pyc', '.pyo', '.pyd', '.log', '.tmp']
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            # استبعاد المجلدات غير المرغوب فيها
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                # استبعاد الملفات غير المرغوب فيها
                if not any(file.endswith(ext) for ext in exclude_files):
                    # إضافة الملف إلى الأرشيف
                    arcname = os.path.relpath(file_path, '.')
                    zf.write(file_path, arcname)
                    print(f"تم إضافة: {arcname}")
    
    print(f"\n✅ تم إنشاء النسخة الاحتياطية بنجاح: {zip_name}")
    print(f"📁 حجم الملف: {os.path.getsize(zip_name) / (1024*1024):.2f} MB")
    return zip_name

if __name__ == "__main__":
    backup_file = create_backup()

