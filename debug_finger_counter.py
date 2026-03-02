#!/usr/bin/env python3
"""
تشخيص مشكلة عدم ظهور نقاط الالتقاط في finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_finger_counter():
    """تشخيص finger_counter"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("🔍 تشخيص finger_counter:")
        print("=" * 50)
        
        # فحص الحالة
        print(f"📊 is_running: {finger_counter.is_running}")
        print(f"🧵 thread: {finger_counter.thread}")
        print(f"🤖 hands: {finger_counter.hands}")
        print(f"🔢 finger_count: {finger_counter.finger_count}")
        print(f"📸 current_frame: {finger_counter.current_frame is not None}")
        
        # فحص الإعدادات
        print(f"🎯 tip_ids: {finger_counter.tip_ids}")
        print(f"📈 frame_count: {finger_counter.frame_count}")
        print(f"⏱️ fps_start_time: {finger_counter.fps_start_time}")
        print(f"📊 current_fps: {finger_counter.current_fps}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تشخيص finger_counter: {e}")
        return False

def debug_views_integration():
    """تشخيص التكامل مع views.py"""
    try:
        from ai_tools.views import finger_counter
        
        print("\n🔍 تشخيص التكامل مع views.py:")
        print("=" * 50)
        
        # فحص الحالة
        print(f"📊 is_running: {finger_counter.is_running}")
        print(f"🧵 thread: {finger_counter.thread}")
        print(f"🤖 hands: {finger_counter.hands}")
        print(f"🔢 finger_count: {finger_counter.finger_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التكامل مع views.py: {e}")
        return False

def debug_mediapipe():
    """تشخيص MediaPipe"""
    try:
        import mediapipe as mp
        print("\n🔍 تشخيص MediaPipe:")
        print("=" * 50)
        
        # فحص MediaPipe
        mp_hands = mp.solutions.hands
        print(f"✅ MediaPipe hands: {mp_hands}")
        
        # إنشاء instance تجريبي
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
            model_complexity=1
        )
        print(f"✅ MediaPipe hands instance: {hands}")
        
        # تنظيف
        hands.close()
        print("✅ تم تنظيف MediaPipe")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في MediaPipe: {e}")
        return False

def debug_opencv():
    """تشخيص OpenCV"""
    try:
        import cv2
        print("\n🔍 تشخيص OpenCV:")
        print("=" * 50)
        
        # فحص OpenCV
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # فحص الكاميرا
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ الكاميرا متاحة")
            ret, frame = cap.read()
            if ret:
                print(f"✅ تم قراءة الإطار - حجم: {frame.shape}")
            else:
                print("❌ فشل في قراءة الإطار")
            cap.release()
        else:
            print("❌ الكاميرا غير متاحة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في OpenCV: {e}")
        return False

def main():
    """الدالة الرئيسية للتشخيص"""
    print("🔍 تشخيص مشكلة عدم ظهور نقاط الالتقاط")
    print("=" * 60)
    
    # تشخيص finger_counter
    if not debug_finger_counter():
        print("\n❌ مشكلة في finger_counter")
        return False
    
    # تشخيص التكامل مع views.py
    if not debug_views_integration():
        print("\n❌ مشكلة في التكامل مع views.py")
        return False
    
    # تشخيص MediaPipe
    if not debug_mediapipe():
        print("\n❌ مشكلة في MediaPipe")
        return False
    
    # تشخيص OpenCV
    if not debug_opencv():
        print("\n❌ مشكلة في OpenCV")
        return False
    
    print("\n✅ جميع التشخيصات نجحت!")
    print("🎯 المشكلة قد تكون في:")
    print("   1. الأداة غير نشطة (is_running = False)")
    print("   2. الإطار لا يُرسل إلى finger_counter")
    print("   3. MediaPipe لا يكتشف اليد")
    print("   4. نقاط الالتقاط لا تُرسم على الإطار")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ هناك مشكلة في التشخيص")
        sys.exit(1)

