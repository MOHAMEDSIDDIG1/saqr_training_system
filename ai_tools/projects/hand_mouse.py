import cv2
import mediapipe as mp
import pyautogui
import math
import threading
import time
import numpy as np
import base64
from collections import deque

class HandMouseController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = None
        self.cap = None
        self.is_running = False
        self.thread = None
        self.screen_width = 0
        self.screen_height = 0
        self.prev_click_state = False
        
        # تحسينات الأداء - سرعة ودقة أعلى
        self.smoothing_factor = 0.3  # عامل تنعيم أقل للسرعة
        self.click_threshold = 0.03  # عتبة نقر أكثر حساسية
        self.movement_threshold = 0.005  # عتبة حركة أقل للدقة
        
        # تنعيم الحركة
        self.position_history = deque(maxlen=5)  # تاريخ المواضع للتنعيم
        self.last_position = None
        
        # إحصائيات الأداء
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # إطار الكاميرا الحالي
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def start_hand_mouse(self):
        """بدء التحكم بالماوس باليدين"""
        # فحص إذا كانت الأداة تعمل فعلياً
        if self.is_running and self.thread and self.thread.is_alive():
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
        
        # إعادة تعيين الحالة إذا كانت الأداة متوقفة
        if not self.is_running or not self.thread or not self.thread.is_alive():
            self.is_running = False
            
        try:
            # تحسين إعدادات MediaPipe للأداء
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,  # وضع الفيديو للسرعة
                max_num_hands=1, 
                min_detection_confidence=0.6,  # دقة متوازنة للسرعة
                min_tracking_confidence=0.6,   # دقة متوازنة للسرعة
                model_complexity=0  # نموذج بسيط للسرعة
            )
            
            # تحسين إعدادات الكاميرا
            # لا نفتح كاميرا منفصلة - نستخدم الكاميرا من camera_feed
            # self.cap = None  # لا نحتاج كاميرا منفصلة
            
            self.screen_width, self.screen_height = pyautogui.size()
            self.is_running = True
            self.prev_click_state = False
            
            # إعادة تعيين المتغيرات
            self.position_history.clear()
            self.last_position = None
            self.frame_count = 0
            self.fps_start_time = time.time()
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_hand_mouse)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء التحكم بالماوس باليدين'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_hand_mouse(self):
        """إيقاف التحكم بالماوس باليدين"""
        if not self.is_running:
            return {'status': 'error', 'message': 'الأداة غير نشطة'}
            
        self.is_running = False
        
        # انتظار انتهاء الـ thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)  # انتظار لمدة ثانيتين كحد أقصى
        
        # تنظيف الموارد
        if self.hands:
            self.hands.close()
            self.hands = None
        
        # إعادة تعيين المتغيرات
        self.thread = None
        self.position_history.clear()
        self.last_position = None
        
        return {'status': 'success', 'message': 'تم إيقاف التحكم بالماوس باليدين'}
    
    def _smooth_position(self, new_x, new_y):
        """تنعيم حركة الماوس لتجنب الاهتزاز"""
        if self.last_position is None:
            self.last_position = (new_x, new_y)
            return new_x, new_y
        
        # تنعيم الحركة
        smooth_x = self.last_position[0] + (new_x - self.last_position[0]) * self.smoothing_factor
        smooth_y = self.last_position[1] + (new_y - self.last_position[1]) * self.smoothing_factor
        
        # فحص إذا كانت الحركة كبيرة بما يكفي
        if abs(smooth_x - self.last_position[0]) < self.movement_threshold and \
           abs(smooth_y - self.last_position[1]) < self.movement_threshold:
            return self.last_position
        
        self.last_position = (smooth_x, smooth_y)
        return smooth_x, smooth_y
    
    def _calculate_fps(self):
        """حساب معدل الإطارات"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:  # كل ثانية
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.fps_start_time = current_time
    
    def _run_hand_mouse(self):
        """تشغيل منطق التحكم بالماوس باليدين المحسن"""
        while self.is_running:
            try:
                # انتظار حتى يكون هناك إطار متاح من camera_feed
                if self.current_frame is not None:
                    image = self.current_frame.copy()
                else:
                    time.sleep(0.01)
                    continue

                # معالجة اليدين على الإطار
                height, width, _ = image.shape
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_rgb)
                
                # لا نرسم نقاط اليد هنا - يتم رسمها في camera_feed
                # نحن فقط نعالج اليدين للتحكم بالماوس
                
                # حساب FPS
                self._calculate_fps()

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # تتبع حركة اليد - استخدام نقطة وسط اليد
                        middle_finger_mcp = hand_landmarks.landmark[9]  # نقطة وسط اليد
                        
                        # تحويل الإحداثيات إلى شاشة
                        x = middle_finger_mcp.x * width
                        y = middle_finger_mcp.y * height
                        screen_x = (x / width) * self.screen_width
                        screen_y = (y / height) * self.screen_height
                        
                        # تنعيم الحركة
                        smooth_x, smooth_y = self._smooth_position(screen_x, screen_y)
                        
                        # تحريك الماوس
                        pyautogui.moveTo(int(smooth_x), int(smooth_y))
                        
                        # كشف النقر المحسن
                        index_finger_tip = hand_landmarks.landmark[8]
                        thumb_tip = hand_landmarks.landmark[4]
                        middle_finger_tip = hand_landmarks.landmark[12]
                        
                        # حساب المسافة بين الإبهام والسبابة
                        distance_thumb_index = math.hypot(
                            index_finger_tip.x - thumb_tip.x, 
                            index_finger_tip.y - thumb_tip.y
                        )
                        
                        # حساب المسافة بين الإبهام والوسطى
                        distance_thumb_middle = math.hypot(
                            middle_finger_tip.x - thumb_tip.x, 
                            middle_finger_tip.y - thumb_tip.y
                        )
                        
                        # كشف النقر المحسن
                        click_state = (distance_thumb_index < self.click_threshold and 
                                     distance_thumb_middle < self.click_threshold)
                        
                        if click_state and not self.prev_click_state:
                            pyautogui.mouseDown()
                        elif not click_state and self.prev_click_state:
                            pyautogui.mouseUp()
                        self.prev_click_state = click_state
                        
                        # لا نضيف مؤشر النقر هنا - يتم عرضه في camera_feed

                # انتظار قليل قبل المعالجة التالية
                time.sleep(0.005)  # سرعة أعلى
                    
            except Exception as e:
                print(f"خطأ في تشغيل الأداة: {e}")
                break
        
        # تنظيف الموارد
        if self.hands:
            self.hands.close()
    
    def get_performance_stats(self):
        """الحصول على إحصائيات الأداء"""
        return {
            'fps': self.current_fps,
            'is_running': self.is_running,
            'smoothing_factor': self.smoothing_factor,
            'click_threshold': self.click_threshold
        }
    
    def adjust_sensitivity(self, smoothing_factor=None, click_threshold=None):
        """تعديل حساسية الأداة"""
        if smoothing_factor is not None:
            self.smoothing_factor = max(0.1, min(1.0, smoothing_factor))
        if click_threshold is not None:
            self.click_threshold = max(0.01, min(0.1, click_threshold))
        return {'status': 'success', 'message': 'تم تعديل الحساسية'}
    
    def reset_state(self):
        """إعادة تعيين حالة الأداة"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.hands:
            self.hands.close()
            self.hands = None
        self.thread = None
        self.position_history.clear()
        self.last_position = None
        self.current_frame = None
        return {'status': 'success', 'message': 'تم إعادة تعيين الحالة'}
    
    def get_current_frame(self):
        """الحصول على الإطار الحالي من الكاميرا"""
        with self.frame_lock:
            if self.current_frame is not None:
                # تحويل الإطار إلى base64
                _, buffer = cv2.imencode('.jpg', self.current_frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return frame_base64
        return None

# إنشاء instance عام للاستخدام
hand_mouse_controller = HandMouseController()

def start_hand_mouse():
    """دالة لبدء التحكم بالماوس باليدين"""
    return hand_mouse_controller.start_hand_mouse()

def stop_hand_mouse():
    """دالة لإيقاف التحكم بالماوس باليدين"""
    return hand_mouse_controller.stop_hand_mouse()

def get_performance_stats():
    """دالة للحصول على إحصائيات الأداء"""
    return hand_mouse_controller.get_performance_stats()

def adjust_sensitivity(smoothing_factor=None, click_threshold=None):
    """دالة لتعديل حساسية الأداة"""
    return hand_mouse_controller.adjust_sensitivity(smoothing_factor, click_threshold)

def reset_state():
    """دالة لإعادة تعيين حالة الأداة"""
    return hand_mouse_controller.reset_state()

def get_current_frame():
    """دالة للحصول على الإطار الحالي من الكاميرا"""
    return hand_mouse_controller.get_current_frame()


