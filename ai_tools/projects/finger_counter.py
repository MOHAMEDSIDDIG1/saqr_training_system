import cv2
import mediapipe as mp
import threading
import time
import numpy as np

class FingerCounter:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.is_running = False
        self.thread = None
        self.tip_ids = [4, 8, 12, 16, 20]  # نقاط أطراف الأصابع
        self.finger_count = 0
        
        # إعدادات التكامل مع camera_feed
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # إحصائيات الأداء
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def start_finger_counter(self):
        """بدء التعرف على عدد الأصابع"""
        # فحص شامل للحالة وإعادة تعيين تلقائي
        if self.is_running:
            # فحص Thread بشكل أكثر دقة
            thread_alive = self.thread and self.thread.is_alive()
            if thread_alive:
                return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            else:
                print("🔄 إعادة تعيين الحالة - Thread معطل أو غير موجود")
                # print(f"   is_running: {self.is_running}")
                # print(f"   thread: {self.thread}")
                # print(f"   thread_alive: {thread_alive}")
                
                # إعادة تعيين كامل
                self.is_running = False
                self.thread = None
                if self.hands:
                    try:
                        self.hands.close()
                    except:
                        pass
                    self.hands = None
                
                print("✅ تم إعادة تعيين الحالة بنجاح")
            
        try:
            # تحسين إعدادات MediaPipe لاكتشاف أفضل
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.4,  # تقليل عتبة الكشف
                min_tracking_confidence=0.4,  # تقليل عتبة التتبع
                model_complexity=1  # زيادة تعقيد النموذج
            )
            
            self.is_running = True
            self.finger_count = 0
            
            # إعادة تعيين متغيرات التشخيص
            self._last_frame_sent = False
            self._last_not_running_logged = False
            self._last_hand_detected = False
            
            print(f"✅ بدء finger_counter - is_running: {self.is_running}")
            print(f"🤖 MediaPipe hands: {self.hands}")
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_finger_counter)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"🧵 Thread started: {self.thread.is_alive()}")
            
            return {'status': 'success', 'message': 'تم بدء التعرف على عدد الأصابع'}
        except Exception as e:
            print(f"❌ خطأ في بدء finger_counter: {e}")
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_finger_counter(self):
        """إيقاف التعرف على عدد الأصابع"""
        self.is_running = False
        
        # انتظار انتهاء Thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        # تنظيف الموارد
        if self.hands:
            try:
                self.hands.close()
            except:
                pass
        
        # إعادة تعيين الحالة
        self.thread = None
        with self.frame_lock:
            self.current_frame = None
        
        # إعادة تعيين متغيرات التشخيص
        self._last_frame_sent = False
        self._last_not_running_logged = False
        self._last_hand_detected = False
        
        return {'status': 'success', 'message': 'تم إيقاف التعرف على عدد الأصابع'}
    
    def get_finger_count(self):
        """الحصول على عدد الأصابع الحالي"""
        return {'status': 'success', 'count': self.finger_count}
    
    def _calculate_fps(self):
        """حساب معدل الإطارات"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.fps_start_time = current_time
    
    def get_performance_stats(self):
        """الحصول على إحصائيات الأداء"""
        return {
            'fps': self.current_fps,
            'is_running': self.is_running,
            'finger_count': self.finger_count
        }
    
    def get_current_frame(self):
        """الحصول على الإطار الحالي من الكاميرا"""
        with self.frame_lock:
            if self.current_frame is not None:
                import base64
                _, buffer = cv2.imencode('.jpg', self.current_frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return frame_base64
        return None
    
    def reset_state(self):
        """إعادة تعيين حالة الأداة بالكامل"""
        self.stop_finger_counter()
        
        # إعادة تعيين جميع المتغيرات
        self.is_running = False
        self.thread = None
        self.hands = None
        self.finger_count = 0
        
        # تنظيف الإطار
        with self.frame_lock:
            self.current_frame = None
        
        # إعادة تعيين الإحصائيات
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        return {'status': 'success', 'message': 'تم إعادة تعيين حالة الأداة'}
    
    def test_hand_detection(self):
        """اختبار اكتشاف اليد"""
        if not self.is_running:
            return {'status': 'error', 'message': 'الأداة غير نشطة'}
        
        with self.frame_lock:
            if self.current_frame is None:
                return {
                    'status': 'warning', 
                    'message': 'لا يوجد إطار متاح - تأكد من تشغيل الكاميرا',
                    'hands_detected': 0,
                    'suggestions': [
                        'تأكد من تشغيل الكاميرا',
                        'تحقق من اتصال الكاميرا',
                        'أعد تشغيل الأداة',
                        'تحقق من الإعدادات'
                    ]
                }
            
            img = self.current_frame.copy()
        
        if img is None:
            return {
                'status': 'warning', 
                'message': 'الإطار فارغ - تحقق من الكاميرا',
                'hands_detected': 0,
                'suggestions': [
                    'تحقق من اتصال الكاميرا',
                    'أعد تشغيل الأداة',
                    'تحقق من الإعدادات'
                ]
            }
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            return {
                'status': 'success', 
                'message': f'تم اكتشاف {len(results.multi_hand_landmarks)} يد',
                'hands_detected': len(results.multi_hand_landmarks)
            }
        else:
            return {
                'status': 'warning', 
                'message': 'لم يتم اكتشاف أي يد',
                'hands_detected': 0,
                'suggestions': [
                    'تحقق من الإضاءة الجيدة',
                    'ضع اليد أمام الكاميرا',
                    'تجنب الخلفيات المعقدة',
                    'تأكد من وضوح اليد'
                ]
            }
    
    def adjust_detection_settings(self, confidence=None, complexity=None):
        """تعديل إعدادات الكشف"""
        if self.is_running:
            return {'status': 'error', 'message': 'لا يمكن تعديل الإعدادات أثناء التشغيل'}
        
        if confidence is not None:
            self.detection_confidence = max(0.1, min(1.0, confidence))
        
        if complexity is not None:
            self.model_complexity = max(0, min(2, complexity))
        
        return {
            'status': 'success', 
            'message': 'تم تحديث إعدادات الكشف',
            'detection_confidence': getattr(self, 'detection_confidence', 0.4),
            'model_complexity': getattr(self, 'model_complexity', 1)
        }
    
    def check_frame_status(self):
        """التحقق من حالة الإطار"""
        # فحص وإصلاح الحالة تلقائياً
        if self.is_running and self.thread and not self.thread.is_alive():
            print("🔄 إصلاح تلقائي - Thread غير نشط")
            self.is_running = False
            self.thread = None
        
        with self.frame_lock:
            frame_available = self.current_frame is not None
            frame_shape = self.current_frame.shape if self.current_frame is not None else None
        
        return {
            'status': 'success',
            'is_running': self.is_running,
            'frame_available': frame_available,
            'frame_shape': frame_shape,
            'thread_alive': self.thread.is_alive() if self.thread else False,
            'hands_initialized': self.hands is not None,
            'finger_count': self.finger_count
        }
    
    def diagnose_camera_issue(self):
        """تشخيص مشاكل الكاميرا"""
        print("🔍 تشخيص مشاكل الكاميرا...")
        
        # فحص الحالة العامة
        status = {
            'is_running': self.is_running,
            'thread_alive': self.thread.is_alive() if self.thread else False,
            'hands_initialized': self.hands is not None,
            'frame_available': False,
            'frame_shape': None,
            'issues': []
        }
        
        # فحص الإطار
        with self.frame_lock:
            if self.current_frame is not None:
                status['frame_available'] = True
                status['frame_shape'] = self.current_frame.shape
                print(f"✅ الإطار متاح: {self.current_frame.shape}")
            else:
                status['issues'].append("لا يوجد إطار متاح")
                print("❌ لا يوجد إطار متاح")
        
        # فحص Thread
        if not self.is_running:
            status['issues'].append("الأداة غير نشطة")
        elif not status['thread_alive']:
            status['issues'].append("Thread غير نشط")
        
        # فحص MediaPipe
        if not status['hands_initialized']:
            status['issues'].append("MediaPipe غير مُهيأ")
        
        return {
            'status': 'success',
            'diagnosis': status,
            'suggestions': [
                "تأكد من تشغيل الكاميرا في المتصفح",
                "تحقق من أن finger_counter يعمل",
                "أعد تشغيل الأداة",
                "استخدم زر 'إعادة تعيين كامل'"
            ]
        }
    
    def test_landmark_drawing(self):
        """اختبار رسم النقاط"""
        print("🎨 اختبار رسم النقاط...")
        
        if not self.is_running:
            return {
                'status': 'error',
                'message': 'الأداة غير نشطة - يجب تشغيل الأداة أولاً'
            }
        
        with self.frame_lock:
            if self.current_frame is None:
                return {
                    'status': 'error',
                    'message': 'لا يوجد إطار متاح - تأكد من تشغيل الكاميرا'
                }
            
            # اختبار MediaPipe على الإطار الحالي
            import cv2
            img_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                return {
                    'status': 'success',
                    'message': f'تم اكتشاف {len(results.multi_hand_landmarks)} يد',
                    'hands_detected': len(results.multi_hand_landmarks),
                    'landmarks_available': True
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'لم يتم اكتشاف أي يد في الإطار الحالي',
                    'hands_detected': 0,
                    'landmarks_available': False,
                    'suggestions': [
                        'تأكد من وجود اليد في الإطار',
                        'تحقق من الإضاءة الجيدة',
                        'تجنب الخلفيات المعقدة',
                        'حرك اليد أمام الكاميرا'
                    ]
                }
    
    def force_start(self):
        """إجبار بدء الأداة"""
        print("🚀 إجبار بدء finger_counter")
        
        # إعادة تعيين كامل
        self.is_running = False
        if self.thread:
            self.thread = None
        if self.hands:
            try:
                self.hands.close()
            except:
                pass
            self.hands = None
        
        # بدء جديد
        return self.start_finger_counter()
    
    def force_reset_and_start(self):
        """إجبار إعادة تعيين وبدء الأداة حتى لو كانت تعمل"""
        print("🔄 إجبار إعادة تعيين وبدء finger_counter")
        
        # إيقاف الأداة بقوة
        self.is_running = False
        
        # إغلاق Thread بقوة
        if self.thread:
            try:
                self.thread.join(timeout=1.0)
            except:
                pass
            self.thread = None
        
        # إغلاق MediaPipe بقوة
        if self.hands:
            try:
                self.hands.close()
            except:
                pass
            self.hands = None
        
        # إعادة تعيين المتغيرات
        self.finger_count = 0
        self.current_frame = None
        self.frame_count = 0
        self.current_fps = 0
        
        print("✅ تم إعادة تعيين الحالة بقوة")
        
        # بدء جديد
        return self.start_finger_counter()
    
    def reset_completely(self):
        """إعادة تعيين كامل للأداة"""
        print("🔄 إعادة تعيين كامل للأداة")
        
        # إيقاف الأداة
        self.is_running = False
        
        # إغلاق Thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.thread = None
        
        # إغلاق MediaPipe
        if self.hands:
            try:
                self.hands.close()
            except:
                pass
            self.hands = None
        
        # إعادة تعيين المتغيرات
        self.finger_count = 0
        self.current_frame = None
        self.frame_count = 0
        self.current_fps = 0
        
        # إعادة تعيين متغيرات التشخيص
        self._last_frame_sent = False
        self._last_not_running_logged = False
        self._last_hand_detected = False
        
        return {'status': 'success', 'message': 'تم إعادة تعيين الأداة بالكامل'}
    
    def _run_finger_counter(self):
        """تشغيل منطق التعرف على عدد الأصابع"""
        print(f"🔄 بدء _run_finger_counter - is_running: {self.is_running}")
        while self.is_running:
            try:
                # الحصول على الإطار من camera_feed
                with self.frame_lock:
                    if self.current_frame is None:
                        time.sleep(0.01)
                        continue
                    img = self.current_frame.copy()
                
                if img is None:
                    time.sleep(0.01)
                    continue
                
                print(f"📸 تم الحصول على إطار في finger_counter - حجم: {img.shape}")

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)

                # إعادة تعيين عدد الأصابع
                self.finger_count = 0

                if results.multi_hand_landmarks:
                    print(results.multi_hand_landmarks)
                    print(f"✅ تم اكتشاف {len(results.multi_hand_landmarks)} يد في finger_counter")
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        print(f"🎯 معالجة اليد رقم {i+1}")
                        
                        # جمع نقاط اليد
                        lm_list = []
                        for id, lm in enumerate(hand_landmarks.landmark):
                            h, w, c = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            lm_list.append([id, cx, cy])

                        # حساب عدد الأصابع المرفوعة
                        if len(lm_list) == 21:
                            fingers = []

                            # الإبهام (مقارنة x)
                            if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 2][1]:
                                fingers.append(1)
                            else:
                                fingers.append(0)

                            # باقي الأصابع (مقارنة y)
                            for tip in range(1, 5):
                                if lm_list[self.tip_ids[tip]][2] < lm_list[self.tip_ids[tip] - 2][2]:
                                    fingers.append(1)
                                else:
                                    fingers.append(0)

                            self.finger_count = fingers.count(1)
                            print(f"🔢 عدد الأصابع: {self.finger_count}")
                        else:
                            print(f"❌ عدد نقاط اليد غير صحيح: {len(lm_list)}")
                else:
                    print("❌ لم يتم اكتشاف أي يد في finger_counter - تحقق من:")
                    print("   - الإضاءة الجيدة")
                    print("   - وضع اليد أمام الكاميرا")
                    print("   - عدم وجود خلفية معقدة")

                # حساب FPS
                self._calculate_fps()
                
                time.sleep(0.01)  # تأخير قصير لتجنب الاستهلاك المفرط للمعالج
                    
            except Exception as e:
                print(f"خطأ في تشغيل الأداة: {e}")
                break
        
        # تنظيف الموارد
        if self.hands:
            try:
                self.hands.close()
            except:
                pass

# إنشاء instance عام للاستخدام
finger_counter = FingerCounter()

def start_finger_counter():
    """دالة لبدء التعرف على عدد الأصابع"""
    return finger_counter.start_finger_counter()

def stop_finger_counter():
    """دالة لإيقاف التعرف على عدد الأصابع"""
    return finger_counter.stop_finger_counter()

def get_finger_count():
    """دالة للحصول على عدد الأصابع الحالي"""
    return finger_counter.get_finger_count()

def get_performance_stats():
    """دالة للحصول على إحصائيات الأداء"""
    return finger_counter.get_performance_stats()

def get_current_frame():
    """دالة للحصول على الإطار الحالي من الكاميرا"""
    return finger_counter.get_current_frame()

def reset_state():
    """دالة لإعادة تعيين حالة الأداة"""
    return finger_counter.reset_state()

def test_hand_detection():
    """دالة لاختبار اكتشاف اليد"""
    return finger_counter.test_hand_detection()

def adjust_detection_settings(confidence=None, complexity=None):
    """دالة لتعديل إعدادات الكشف"""
    return finger_counter.adjust_detection_settings(confidence, complexity)

def check_frame_status():
    """دالة للتحقق من حالة الإطار"""
    return finger_counter.check_frame_status()

def force_start():
    """دالة لإجبار بدء الأداة"""
    return finger_counter.force_start()

def reset_completely():
    """دالة لإعادة تعيين كامل للأداة"""
    return finger_counter.reset_completely()

def diagnose_camera_issue():
    """دالة لتشخيص مشاكل الكاميرا"""
    return finger_counter.diagnose_camera_issue()

def test_landmark_drawing():
    """دالة لاختبار رسم النقاط"""
    return finger_counter.test_landmark_drawing()

def force_reset_and_start():
    """دالة لإجبار إعادة تعيين وبدء الأداة"""
    return finger_counter.force_reset_and_start()


