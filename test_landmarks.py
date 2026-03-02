#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ظهور نقاط التقاط اليد في finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_landmark_detection():
    """اختبار اكتشاف النقاط"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, test_landmark_drawing
        
        print("🎨 اختبار اكتشاف نقاط اليد...")
        result = test_landmark_drawing()
        
        print(f"📊 النتيجة: {result['status']}")
        print(f"   الرسالة: {result['message']}")
        
        if result['status'] == 'success':
            print(f"✅ تم اكتشاف {result['hands_detected']} يد")
            print(f"✅ النقاط متاحة: {result['landmarks_available']}")
            print("🎯 النقاط يجب أن تظهر على الكاميرا!")
        elif result['status'] == 'warning':
            print(f"⚠️ {result['message']}")
            print(f"   عدد الأيدي: {result['hands_detected']}")
            print(f"   النقاط متاحة: {result['landmarks_available']}")
            if 'suggestions' in result:
                print("💡 الاقتراحات:")
                for suggestion in result['suggestions']:
                    print(f"   - {suggestion}")
        else:
            print(f"❌ خطأ: {result['message']}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_finger_counter_status():
    """اختبار حالة finger_counter"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("\n🔍 فحص حالة finger_counter...")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        print(f"   finger_count: {finger_counter.finger_count}")
        
        if finger_counter.is_running:
            print("✅ الأداة نشطة")
            if finger_counter.thread and finger_counter.thread.is_alive():
                print("✅ Thread نشط")
            else:
                print("❌ Thread غير نشط")
            
            if finger_counter.hands:
                print("✅ MediaPipe مُهيأ")
            else:
                print("❌ MediaPipe غير مُهيأ")
        else:
            print("❌ الأداة غير نشطة")
        
        return finger_counter.is_running
        
    except Exception as e:
        print(f"❌ خطأ في فحص الحالة: {e}")
        return False

def test_camera_frame():
    """اختبار إطار الكاميرا"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("\n📸 فحص إطار الكاميرا...")
        
        with finger_counter.frame_lock:
            if finger_counter.current_frame is not None:
                print(f"✅ الإطار متاح: {finger_counter.current_frame.shape}")
                return True
            else:
                print("❌ لا يوجد إطار متاح")
                return False
        
    except Exception as e:
        print(f"❌ خطأ في فحص الإطار: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار ظهور نقاط التقاط اليد")
    print("=" * 50)
    
    # اختبار الحالة
    status_ok = test_finger_counter_status()
    
    # اختبار الإطار
    frame_ok = test_camera_frame()
    
    # اختبار النقاط
    landmarks_ok = test_landmark_detection()
    
    print("\n" + "=" * 50)
    print("📊 ملخص النتائج:")
    print(f"   حالة الأداة: {'✅ جيدة' if status_ok else '❌ مشكلة'}")
    print(f"   إطار الكاميرا: {'✅ متاح' if frame_ok else '❌ غير متاح'}")
    print(f"   النقاط: {'✅ تظهر' if landmarks_ok else '❌ لا تظهر'}")
    
    if all([status_ok, frame_ok, landmarks_ok]):
        print("\n🎉 النقاط يجب أن تظهر على الكاميرا!")
    else:
        print("\n⚠️ هناك مشاكل تمنع ظهور النقاط")
        print("💡 جرب استخدام:")
        print("   - زر 'تشخيص الكاميرا'")
        print("   - زر 'إعادة تعيين كامل'")
        print("   - زر 'إجبار البدء'")
    
    print("\nانتهى الاختبار")

