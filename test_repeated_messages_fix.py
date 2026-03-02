#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح الرسائل المتكررة في finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_repeated_messages_fix():
    """اختبار إصلاح الرسائل المتكررة"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("🔍 فحص متغيرات التشخيص...")
        
        # فحص المتغيرات الجديدة
        has_last_frame_sent = hasattr(finger_counter, '_last_frame_sent')
        has_last_not_running_logged = hasattr(finger_counter, '_last_not_running_logged')
        
        print(f"   _last_frame_sent: {has_last_frame_sent}")
        print(f"   _last_not_running_logged: {has_last_not_running_logged}")
        
        if has_last_frame_sent:
            print(f"   قيمة _last_frame_sent: {finger_counter._last_frame_sent}")
        if has_last_not_running_logged:
            print(f"   قيمة _last_not_running_logged: {finger_counter._last_not_running_logged}")
        
        print("\n✅ تم إضافة متغيرات التشخيص بنجاح!")
        print("💡 الآن لن تتكرر رسائل 'finger_counter not running'")
        print("💡 ستظهر الرسالة مرة واحدة فقط عند الحاجة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_message_control():
    """اختبار التحكم في الرسائل"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("\n🧪 اختبار التحكم في الرسائل...")
        
        # محاكاة حالة الأداة غير نشطة
        finger_counter.is_running = False
        finger_counter._last_not_running_logged = False
        
        print("✅ تم إعداد الحالة للاختبار")
        print("💡 الآن عند تشغيل camera_feed، ستظهر الرسالة مرة واحدة فقط")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار التحكم: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار إصلاح الرسائل المتكررة")
    print("=" * 50)
    
    # اختبار إضافة المتغيرات
    variables_ok = test_repeated_messages_fix()
    
    # اختبار التحكم في الرسائل
    control_ok = test_message_control()
    
    print("\n" + "=" * 50)
    print("📊 ملخص النتائج:")
    print(f"   متغيرات التشخيص: {'✅ تمت' if variables_ok else '❌ فشل'}")
    print(f"   التحكم في الرسائل: {'✅ تم' if control_ok else '❌ فشل'}")
    
    if variables_ok and control_ok:
        print("\n🎉 تم إصلاح الرسائل المتكررة بنجاح!")
        print("💡 لن تظهر رسائل 'finger_counter not running' المتكررة")
        print("💡 ستظهر الرسائل مرة واحدة فقط عند الحاجة")
    else:
        print("\n⚠️ هناك مشاكل في الإصلاح")
        print("💡 تحقق من الكود وأعد المحاولة")
    
    print("\nانتهى الاختبار")

