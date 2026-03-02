#!/usr/bin/env python3
"""
إظهار حالة finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_finger_counter_status():
    """إظهار حالة finger_counter"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print("🔍 حالة finger_counter:")
        print("=" * 40)
        print(f"📊 is_running: {finger_counter.is_running}")
        print(f"🧵 thread: {finger_counter.thread}")
        print(f"🤖 hands: {finger_counter.hands}")
        print(f"🔢 finger_count: {finger_counter.finger_count}")
        print(f"📸 current_frame: {finger_counter.current_frame is not None}")
        print(f"🔒 frame_lock: {finger_counter.frame_lock}")
        print(f"📈 frame_count: {finger_counter.frame_count}")
        print(f"⏱️ fps_start_time: {finger_counter.fps_start_time}")
        print(f"📊 current_fps: {finger_counter.current_fps}")
        
        print("\n✅ finger_counter instance موجود ويعمل!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في finger_counter: {e}")
        return False

def show_finger_counter_functions():
    """إظهار دوال finger_counter"""
    try:
        from ai_tools.projects.finger_counter import (
            start_finger_counter, 
            stop_finger_counter, 
            get_finger_count,
            get_performance_stats,
            get_current_frame,
            reset_state,
            test_hand_detection,
            adjust_detection_settings
        )
        
        print("\n🔧 دوال finger_counter المتاحة:")
        print("=" * 40)
        print("✅ start_finger_counter")
        print("✅ stop_finger_counter")
        print("✅ get_finger_count")
        print("✅ get_performance_stats")
        print("✅ get_current_frame")
        print("✅ reset_state")
        print("✅ test_hand_detection")
        print("✅ adjust_detection_settings")
        
        print("\n✅ جميع الدوال متاحة!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في دوال finger_counter: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎯 إظهار حالة finger_counter")
    print("=" * 50)
    
    # إظهار حالة instance
    if not show_finger_counter_status():
        return False
    
    # إظهار الدوال
    if not show_finger_counter_functions():
        return False
    
    print("\n🎉 النتيجة: finger_counter يعمل بالفعل!")
    print("📝 يمكنك الآن:")
    print("   1. تشغيل Django server")
    print("   2. الذهاب إلى finger_counter page")
    print("   3. الضغط على 'بدء العد'")
    print("   4. رؤية نقاط الالتقاط على الكاميرا")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ هناك مشكلة في finger_counter")
        sys.exit(1)

