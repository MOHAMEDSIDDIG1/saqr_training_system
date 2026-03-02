@echo off
echo ========================================
echo    شركة صقر للتدريب والاستشارات
echo    منصة الأدوات الذكية
echo ========================================
echo.

echo جاري تفعيل البيئة الافتراضية...
call venv\Scripts\activate

echo.
echo جاري تشغيل الخادم...
cd saqr_training_system
python manage.py runserver

pause
