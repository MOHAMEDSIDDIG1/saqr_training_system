#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة "الأداة تعمل بالفعل"
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_already_running_fix():
    """اختبار إصلاح مشكلة الأداة تعمل بالفعل"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, force_reset_and_start
        
        print("🔍 فحص الحالة الحالية...")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        
        print("\n🔄 اختبار إجبار إعادة التعيين والبدء...")
        result = force_reset_and_start()
        
        print(f"📊 النتيجة: {result['status']}")
        print(f"   الرسالة: {result['message']}")
        
        if result['status'] == 'success':
            print("✅ تم إصلاح المشكلة بنجاح!")
            print(f"   is_running بعد الإصلاح: {finger_counter.is_running}")
            print(f"   thread بعد الإصلاح: {finger_counter.thread}")
            print(f"   hands بعد الإصلاح: {finger_counter.hands}")
        else:
            print(f"❌ فشل في الإصلاح: {result['message']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_start_after_fix():
    """اختبار البدء بعد الإصلاح"""
    try:
        from ai_tools.projects.finger_counter import start_finger_counter
        
        print("\n🚀 اختبار البدء بعد الإصلاح...")
        result = start_finger_counter()
        
        print(f"📊 النتيجة: {result['status']}")
        print(f"   الرسالة: {result['message']}")
        
        if result['status'] == 'success':
            print("✅ تم بدء الأداة بنجاح بعد الإصلاح!")
        elif result['status'] == 'error' and 'تعمل بالفعل' in result['message']:
            print("⚠️ لا تزال هناك مشكلة - الأداة تظهر أنها تعمل بالفعل")
        else:
            print(f"❌ خطأ آخر: {result['message']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في اختبار البدء: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار إصلاح مشكلة 'الأداة تعمل بالفعل'")
    print("=" * 60)
    
    # اختبار الإصلاح
    fix_success = test_already_running_fix()
    
    # اختبار البدء بعد الإصلاح
    start_success = test_start_after_fix()
    
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print(f"   إصلاح المشكلة: {'✅ نجح' if fix_success else '❌ فشل'}")
    print(f"   البدء بعد الإصلاح: {'✅ نجح' if start_success else '❌ فشل'}")
    
    if fix_success and start_success:
        print("\n🎉 تم إصلاح المشكلة بالكامل!")
        print("💡 يمكنك الآن استخدام الأداة بدون مشاكل")
    elif fix_success:
        print("\n⚠️ تم إصلاح المشكلة لكن لا تزال هناك مشاكل في البدء")
        print("💡 جرب استخدام زر 'إجبار إعادة التعيين والبدء' في الواجهة")
    else:
        print("\n❌ فشل في إصلاح المشكلة")
        print("💡 جرب استخدام زر 'إجبار إعادة التعيين والبدء' في الواجهة")
    
    print("\nانتهى الاختبار")

