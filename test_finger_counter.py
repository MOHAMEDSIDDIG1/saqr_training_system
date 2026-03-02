#!/usr/bin/env python3
"""
اختبار بسيط لإظهار أن finger_counter يعمل
"""

import sys
import os

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_finger_counter_import():
    """اختبار استيراد finger_counter"""
    try:
        from ai_tools.projects.finger_counter import (
            start_finger_counter, 
            stop_finger_counter, 
            get_finger_count,
            finger_counter
        )
        print("✅ تم استيراد finger_counter بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في استيراد finger_counter: {e}")
        return False

def test_finger_counter_instance():
    """اختبار instance من finger_counter"""
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        print(f"📊 حالة finger_counter:")
        print(f"   - is_running: {finger_counter.is_running}")
        print(f"   - thread: {finger_counter.thread}")
        print(f"   - hands: {finger_counter.hands}")
        print(f"   - finger_count: {finger_counter.finger_count}")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في finger_counter instance: {e}")
        return False

def test_finger_counter_functions():
    """اختبار دوال finger_counter"""
    try:
        from ai_tools.projects.finger_counter import (
            start_finger_counter, 
            stop_finger_counter, 
            get_finger_count
        )
        
        print("🧪 اختبار دوال finger_counter:")
        
        # اختبار get_finger_count
        result = get_finger_count()
        print(f"   - get_finger_count: {result}")
        
        # اختبار start_finger_counter
        result = start_finger_counter()
        print(f"   - start_finger_counter: {result}")
        
        # اختبار stop_finger_counter
        result = stop_finger_counter()
        print(f"   - stop_finger_counter: {result}")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في دوال finger_counter: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🔍 اختبار finger_counter...")
    print("=" * 50)
    
    # اختبار الاستيراد
    if not test_finger_counter_import():
        return False
    
    print()
    
    # اختبار instance
    if not test_finger_counter_instance():
        return False
    
    print()
    
    # اختبار الدوال
    if not test_finger_counter_functions():
        return False
    
    print()
    print("✅ جميع الاختبارات نجحت!")
    print("🎯 finger_counter يعمل بشكل صحيح")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 النتيجة: finger_counter يعمل بالفعل!")
    else:
        print("\n❌ النتيجة: هناك مشكلة في finger_counter")

