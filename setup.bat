@echo off
echo ========================================
echo    شركة صقر للتدريب والاستشارات
echo    إعداد منصة الأدوات الذكية
echo ========================================
echo.

echo جاري إنشاء البيئة الافتراضية...
python -m venv venv

echo.
echo جاري تفعيل البيئة الافتراضية...
call venv\Scripts\activate

echo.
echo جاري تثبيت المتطلبات...
pip install -r requirements.txt

echo.
echo جاري إنشاء قاعدة البيانات...
cd saqr_training_system
python manage.py migrate

echo.
echo ========================================
echo    تم الإعداد بنجاح!
echo ========================================
echo.
echo لتشغيل المشروع، استخدم ملف run.bat
echo أو قم بتشغيل الأمر التالي:
echo python manage.py runserver
echo.
pause
