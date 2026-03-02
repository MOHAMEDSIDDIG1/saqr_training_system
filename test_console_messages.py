#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار رسائل الكونسول المتكررة
"""

import time
import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_console_messages():
    """اختبار رسائل الكونسول المتكررة"""
    print("🧪 اختبار رسائل الكونسول المتكررة")
    print("=" * 50)
    
    try:
        # استيراد finger_counter
        from ai_tools.projects.finger_counter import finger_counter
        
        print("✅ تم استيراد finger_counter بنجاح")
        
        # فحص الحالة الأولية
        print(f"📊 الحالة الأولية:")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        
        # فحص متغيرات التشخيص
        print(f"🔍 متغيرات التشخيص:")
        print(f"   _last_frame_sent: {getattr(finger_counter, '_last_frame_sent', 'غير موجود')}")
        print(f"   _last_not_running_logged: {getattr(finger_counter, '_last_not_running_logged', 'غير موجود')}")
        print(f"   _last_hand_detected: {getattr(finger_counter, '_last_hand_detected', 'غير موجود')}")
        
        # اختبار إعادة تعيين الحالة
        print("\n🔄 اختبار إعادة تعيين الحالة...")
        result = finger_counter.reset_completely()
        print(f"   النتيجة: {result}")
        
        # فحص الحالة بعد الإعادة تعيين
        print(f"📊 الحالة بعد الإعادة تعيين:")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        
        # فحص متغيرات التشخيص بعد الإعادة تعيين
        print(f"🔍 متغيرات التشخيص بعد الإعادة تعيين:")
        print(f"   _last_frame_sent: {getattr(finger_counter, '_last_frame_sent', 'غير موجود')}")
        print(f"   _last_not_running_logged: {getattr(finger_counter, '_last_not_running_logged', 'غير موجود')}")
        print(f"   _last_hand_detected: {getattr(finger_counter, '_last_hand_detected', 'غير موجود')}")
        
        print("\n✅ تم اختبار رسائل الكونسول بنجاح")
        print("💡 يجب ألا تظهر رسائل متكررة في الكونسول")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار رسائل الكونسول: {e}")
        return False

if __name__ == "__main__":
    test_console_messages()

