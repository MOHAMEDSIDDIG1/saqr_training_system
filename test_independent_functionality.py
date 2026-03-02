#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عمل الكود بشكل مستقل
"""

import sys
import os
import time

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد جميع الوحدات"""
    print("🔍 اختبار استيراد الوحدات...")
    
    try:
        from ai_tools.projects.finger_counter import (
            finger_counter, 
            start_finger_counter, 
            stop_finger_counter, 
            get_finger_count,
            get_performance_stats,
            get_current_frame,
            reset_state,
            test_hand_detection,
            adjust_detection_settings,
            check_frame_status,
            force_start,
            reset_completely,
            diagnose_camera_issue,
            test_landmark_drawing,
            force_reset_and_start
        )
        print("✅ تم استيراد جميع الدوال بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False

def test_finger_counter_initialization():
    """اختبار تهيئة finger_counter"""
    print("\n🔧 اختبار تهيئة finger_counter...")
    
    try:
        from ai_tools.projects.finger_counter import finger_counter
        
        # فحص الخصائص الأساسية
        assert hasattr(finger_counter, 'is_running'), "is_running غير موجود"
        assert hasattr(finger_counter, 'thread'), "thread غير موجود"
        assert hasattr(finger_counter, 'hands'), "hands غير موجود"
        assert hasattr(finger_counter, 'finger_count'), "finger_count غير موجود"
        assert hasattr(finger_counter, 'current_frame'), "current_frame غير موجود"
        assert hasattr(finger_counter, 'frame_lock'), "frame_lock غير موجود"
        
        # فحص القيم الافتراضية
        assert finger_counter.is_running == False, f"is_running يجب أن يكون False، لكنه {finger_counter.is_running}"
        assert finger_counter.thread is None, f"thread يجب أن يكون None، لكنه {finger_counter.thread}"
        assert finger_counter.hands is None, f"hands يجب أن يكون None، لكنه {finger_counter.hands}"
        assert finger_counter.finger_count == 0, f"finger_count يجب أن يكون 0، لكنه {finger_counter.finger_count}"
        
        print("✅ تم تهيئة finger_counter بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في التهيئة: {e}")
        return False

def test_start_stop_cycle():
    """اختبار دورة البدء والإيقاف"""
    print("\n🔄 اختبار دورة البدء والإيقاف...")
    
    try:
        from ai_tools.projects.finger_counter import start_finger_counter, stop_finger_counter, finger_counter
        
        # اختبار البدء
        print("   بدء الأداة...")
        result = start_finger_counter()
        assert result['status'] == 'success', f"فشل في البدء: {result}"
        assert finger_counter.is_running == True, "is_running يجب أن يكون True"
        assert finger_counter.thread is not None, "thread يجب أن يكون موجود"
        assert finger_counter.hands is not None, "hands يجب أن يكون موجود"
        print("   ✅ تم بدء الأداة بنجاح")
        
        # انتظار قصير
        time.sleep(0.5)
        
        # اختبار الإيقاف
        print("   إيقاف الأداة...")
        result = stop_finger_counter()
        assert result['status'] == 'success', f"فشل في الإيقاف: {result}"
        assert finger_counter.is_running == False, "is_running يجب أن يكون False"
        print("   ✅ تم إيقاف الأداة بنجاح")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في دورة البدء والإيقاف: {e}")
        return False

def test_diagnostic_functions():
    """اختبار الدوال التشخيصية"""
    print("\n🔍 اختبار الدوال التشخيصية...")
    
    try:
        from ai_tools.projects.finger_counter import (
            check_frame_status, 
            diagnose_camera_issue, 
            test_landmark_drawing
        )
        
        # اختبار check_frame_status
        print("   اختبار check_frame_status...")
        result = check_frame_status()
        assert result['status'] == 'success', f"فشل في check_frame_status: {result}"
        assert 'is_running' in result, "is_running غير موجود في النتيجة"
        assert 'frame_available' in result, "frame_available غير موجود في النتيجة"
        print("   ✅ check_frame_status يعمل")
        
        # اختبار diagnose_camera_issue
        print("   اختبار diagnose_camera_issue...")
        result = diagnose_camera_issue()
        assert result['status'] == 'success', f"فشل في diagnose_camera_issue: {result}"
        assert 'diagnosis' in result, "diagnosis غير موجود في النتيجة"
        assert 'suggestions' in result, "suggestions غير موجود في النتيجة"
        print("   ✅ diagnose_camera_issue يعمل")
        
        # اختبار test_landmark_drawing
        print("   اختبار test_landmark_drawing...")
        result = test_landmark_drawing()
        # قد يكون error أو warning، وهذا طبيعي إذا لم تكن الأداة تعمل
        assert 'status' in result, "status غير موجود في النتيجة"
        assert 'message' in result, "message غير موجود في النتيجة"
        print("   ✅ test_landmark_drawing يعمل")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في الدوال التشخيصية: {e}")
        return False

def test_reset_functions():
    """اختبار دوال الإعادة تعيين"""
    print("\n🔄 اختبار دوال الإعادة تعيين...")
    
    try:
        from ai_tools.projects.finger_counter import (
            reset_state, 
            reset_completely, 
            force_reset_and_start
        )
        
        # اختبار reset_state
        print("   اختبار reset_state...")
        result = reset_state()
        assert result['status'] == 'success', f"فشل في reset_state: {result}"
        print("   ✅ reset_state يعمل")
        
        # اختبار reset_completely
        print("   اختبار reset_completely...")
        result = reset_completely()
        assert result['status'] == 'success', f"فشل في reset_completely: {result}"
        print("   ✅ reset_completely يعمل")
        
        # اختبار force_reset_and_start
        print("   اختبار force_reset_and_start...")
        result = force_reset_and_start()
        assert result['status'] == 'success', f"فشل في force_reset_and_start: {result}"
        print("   ✅ force_reset_and_start يعمل")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في دوال الإعادة تعيين: {e}")
        return False

def test_performance_stats():
    """اختبار إحصائيات الأداء"""
    print("\n📊 اختبار إحصائيات الأداء...")
    
    try:
        from ai_tools.projects.finger_counter import get_performance_stats
        
        result = get_performance_stats()
        assert 'status' in result, "status غير موجود في النتيجة"
        assert 'fps' in result, "fps غير موجود في النتيجة"
        assert 'frame_count' in result, "frame_count غير موجود في النتيجة"
        
        print("✅ get_performance_stats يعمل")
        return True
    except Exception as e:
        print(f"❌ خطأ في إحصائيات الأداء: {e}")
        return False

def test_error_handling():
    """اختبار معالجة الأخطاء"""
    print("\n⚠️ اختبار معالجة الأخطاء...")
    
    try:
        from ai_tools.projects.finger_counter import finger_counter, get_finger_count
        
        # اختبار get_finger_count عندما تكون الأداة معطلة
        result = get_finger_count()
        assert result['status'] == 'success', f"فشل في get_finger_count: {result}"
        assert 'count' in result, "count غير موجود في النتيجة"
        
        print("✅ معالجة الأخطاء تعمل")
        return True
    except Exception as e:
        print(f"❌ خطأ في معالجة الأخطاء: {e}")
        return False

if __name__ == "__main__":
    print("🧪 اختبار عمل الكود بشكل مستقل")
    print("=" * 60)
    
    # قائمة الاختبارات
    tests = [
        ("استيراد الوحدات", test_imports),
        ("تهيئة finger_counter", test_finger_counter_initialization),
        ("دورة البدء والإيقاف", test_start_stop_cycle),
        ("الدوال التشخيصية", test_diagnostic_functions),
        ("دوال الإعادة تعيين", test_reset_functions),
        ("إحصائيات الأداء", test_performance_stats),
        ("معالجة الأخطاء", test_error_handling)
    ]
    
    results = []
    
    # تشغيل الاختبارات
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
            results.append((test_name, False))
    
    # ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ نجح" if success else "❌ فشل"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"النتيجة النهائية: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الكود يعمل بشكل مستقل")
    else:
        print("⚠️ بعض الاختبارات فشلت. تحقق من الأخطاء أعلاه")
    
    print("\nانتهى الاختبار")

