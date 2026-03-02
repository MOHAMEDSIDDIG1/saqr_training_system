#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة الكاميرا في finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_camera_diagnosis():
    """اختبار تشخيص الكاميرا"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, diagnose_camera_issue
        
        print("🔍 تشخيص مشاكل الكاميرا...")
        result = diagnose_camera_issue()
        
        print(f"📊 النتيجة: {result['status']}")
        if result['status'] == 'success':
            diagnosis = result['diagnosis']
            print(f"   الأداة نشطة: {diagnosis['is_running']}")
            print(f"   Thread نشط: {diagnosis['thread_alive']}")
            print(f"   MediaPipe مُهيأ: {diagnosis['hands_initialized']}")
            print(f"   الإطار متاح: {diagnosis['frame_available']}")
            print(f"   حجم الإطار: {diagnosis['frame_shape']}")
            
            if diagnosis['issues']:
                print("❌ المشاكل المكتشفة:")
                for issue in diagnosis['issues']:
                    print(f"   - {issue}")
            else:
                print("✅ لا توجد مشاكل مكتشفة")
            
            if result['suggestions']:
                print("💡 الاقتراحات:")
                for suggestion in result['suggestions']:
                    print(f"   - {suggestion}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في التشخيص: {e}")
        return False

def test_frame_status():
    """اختبار حالة الإطار"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, check_frame_status
        
        print("\n🔍 فحص حالة الإطار...")
        result = check_frame_status()
        
        print(f"📊 النتيجة: {result['status']}")
        if result['status'] == 'success':
            print(f"   الأداة نشطة: {result['is_running']}")
            print(f"   الإطار متاح: {result['frame_available']}")
            print(f"   حجم الإطار: {result['frame_shape']}")
            print(f"   Thread نشط: {result['thread_alive']}")
            print(f"   MediaPipe مُهيأ: {result['hands_initialized']}")
            print(f"   عدد الأصابع: {result['finger_count']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في فحص الإطار: {e}")
        return False

def test_reset_completely():
    """اختبار إعادة تعيين كامل"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, reset_completely
        
        print("\n🔄 اختبار إعادة تعيين كامل...")
        result = reset_completely()
        
        print(f"📊 النتيجة: {result['status']}")
        if result['status'] == 'success':
            print(f"   الرسالة: {result['message']}")
            print(f"   الأداة نشطة بعد الإعادة تعيين: {finger_counter.is_running}")
            print(f"   Thread بعد الإعادة تعيين: {finger_counter.thread}")
            print(f"   MediaPipe بعد الإعادة تعيين: {finger_counter.hands}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في إعادة التعيين: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار إصلاح مشكلة الكاميرا")
    print("=" * 50)
    
    # اختبار التشخيص
    diagnosis_success = test_camera_diagnosis()
    
    # اختبار حالة الإطار
    frame_success = test_frame_status()
    
    # اختبار إعادة التعيين
    reset_success = test_reset_completely()
    
    print("\n" + "=" * 50)
    print("📊 ملخص النتائج:")
    print(f"   تشخيص الكاميرا: {'✅ نجح' if diagnosis_success else '❌ فشل'}")
    print(f"   فحص الإطار: {'✅ نجح' if frame_success else '❌ فشل'}")
    print(f"   إعادة التعيين: {'✅ نجح' if reset_success else '❌ فشل'}")
    
    if all([diagnosis_success, frame_success, reset_success]):
        print("\n🎉 تم إصلاح جميع المشاكل بنجاح!")
    else:
        print("\n⚠️ بعض المشاكل لا تزال موجودة")
    
    print("\nانتهى الاختبار")

