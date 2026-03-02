#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح أداة finger_counter
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_finger_counter_reset():
    """اختبار إعادة تعيين finger_counter"""
    try:
        from ai_tools.projects.finger_counter import finger_counter, reset_completely
        
        print("🔍 فحص الحالة الحالية:")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        print(f"   finger_count: {finger_counter.finger_count}")
        
        print("\n🔄 إعادة تعيين كامل...")
        result = reset_completely()
        print(f"   النتيجة: {result}")
        
        print("\n✅ فحص الحالة بعد الإعادة تعيين:")
        print(f"   is_running: {finger_counter.is_running}")
        print(f"   thread: {finger_counter.thread}")
        print(f"   hands: {finger_counter.hands}")
        print(f"   finger_count: {finger_counter.finger_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_finger_counter_start():
    """اختبار بدء finger_counter"""
    try:
        from ai_tools.projects.finger_counter import start_finger_counter
        
        print("\n🚀 محاولة بدء الأداة...")
        result = start_finger_counter()
        print(f"   النتيجة: {result}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ خطأ في بدء الأداة: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار إصلاح finger_counter")
    print("=" * 50)
    
    # اختبار إعادة التعيين
    reset_success = test_finger_counter_reset()
    
    if reset_success:
        # اختبار البدء
        start_success = test_finger_counter_start()
        
        if start_success:
            print("\n✅ تم إصلاح الأداة بنجاح!")
        else:
            print("\n⚠️ الأداة تم إعادة تعيينها لكن لا تزال هناك مشاكل في البدء")
    else:
        print("\n❌ فشل في إعادة تعيين الأداة")
    
    print("\n" + "=" * 50)
    print("انتهى الاختبار")

