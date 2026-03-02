import cv2
import mediapipe as mp
import pyautogui
import threading
import time
import numpy as np
from collections import deque

class EyeMouseController:
    def __init__(self):
        self.cam = None
        self.face_mesh = None
        self.screen_w, self.screen_h = pyautogui.size()
        self.is_running = False
        self.thread = None
        
        # تحسينات الأداء - نفس إعدادات hand_mouse
        self.smoothing_factor = 0.3
        self.click_threshold = 0.03
        self.movement_threshold = 0.005
        self.position_history = deque(maxlen=5)
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # إحصائيات الأداء
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def start_eye_mouse(self):
        """بدء التحكم بالماوس بالعين"""
        if self.is_running and self.thread and self.thread.is_alive():
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            
        try:
            # تحسين إعدادات MediaPipe
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                refine_landmarks=True,
                max_num_faces=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6
            )
            self.is_running = True
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_eye_mouse)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء التحكم بالماوس بالعين'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_eye_mouse(self):
        """إيقاف التحكم بالماوس بالعين"""
        self.is_running = False
        
        # انتظار إيقاف الـ thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)  # انتظار لمدة ثانيتين كحد أقصى
        
        # تنظيف الموارد
        if self.face_mesh:
            try:
                self.face_mesh.close()
            except:
                pass
            self.face_mesh = None
        
        # إعادة تعيين الحالة
        self.thread = None
        with self.frame_lock:
            self.current_frame = None
        
        return {'status': 'success', 'message': 'تم إيقاف التحكم بالماوس بالعين'}
    
    def reset_state(self):
        """إعادة تعيين حالة الأداة بالكامل"""
        self.stop_eye_mouse()
        
        # إعادة تعيين جميع المتغيرات
        self.is_running = False
        self.thread = None
        self.face_mesh = None
        
        # تنظيف الإطار
        with self.frame_lock:
            self.current_frame = None
        
        # إعادة تعيين الإحصائيات
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.position_history.clear()
        
        return {'status': 'success', 'message': 'تم إعادة تعيين حالة الأداة'}
    
    def _calculate_fps(self):
        """حساب معدل الإطارات"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.fps_start_time = current_time
    
    def _smooth_position(self, new_x, new_y):
        """تنعيم حركة الماوس - نفس خوارزمية hand_mouse"""
        self.position_history.append((new_x, new_y))
        if len(self.position_history) < 2:
            return new_x, new_y
        
        # حساب المتوسط المتحرك مع عامل التنعيم
        avg_x = sum(pos[0] for pos in self.position_history) / len(self.position_history)
        avg_y = sum(pos[1] for pos in self.position_history) / len(self.position_history)
        
        # تطبيق عامل التنعيم
        smooth_x = avg_x * self.smoothing_factor + new_x * (1 - self.smoothing_factor)
        smooth_y = avg_y * self.smoothing_factor + new_y * (1 - self.smoothing_factor)
        
        return smooth_x, smooth_y
    
    def get_performance_stats(self):
        """الحصول على إحصائيات الأداء"""
        return {
            'fps': self.current_fps,
            'is_running': self.is_running,
            'smoothing_factor': self.smoothing_factor,
            'click_threshold': self.click_threshold,
            'movement_threshold': self.movement_threshold
        }
    
    def adjust_sensitivity(self, smoothing_factor=None, click_threshold=None):
        """تعديل حساسية الأداة"""
        if smoothing_factor is not None:
            self.smoothing_factor = smoothing_factor
        if click_threshold is not None:
            self.click_threshold = click_threshold
        return {'status': 'success', 'message': 'تم تعديل الحساسية'}
    
    def get_current_frame(self):
        """الحصول على الإطار الحالي من الكاميرا"""
        with self.frame_lock:
            if self.current_frame is not None:
                import base64
                _, buffer = cv2.imencode('.jpg', self.current_frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return frame_base64
        return None
    
    def _run_eye_mouse(self):
        """تشغيل منطق التحكم بالماوس بالعين المحسن"""
        while self.is_running:
            try:
                # الحصول على الإطار من camera_feed
                with self.frame_lock:
                    if self.current_frame is None:
                        time.sleep(0.01)
                        continue
                    frame = self.current_frame.copy()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output = self.face_mesh.process(rgb_frame)
                landmark_points = output.multi_face_landmarks
                frame_h, frame_w, _ = frame.shape
                
                # حساب FPS
                self._calculate_fps()
                
                if landmark_points:
                    landmarks = landmark_points[0].landmark
                    
                    # تتبع حركة العين المحسن - استخدام نقاط العين الصحيحة
                    # نقاط العين اليمنى (من MediaPipe Face Mesh) - نقاط أكثر دقة
                    right_eye_landmarks = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
                    
                    # رسم نقاط العين
                    for idx in right_eye_landmarks:
                        if idx < len(landmarks):
                            landmark = landmarks[idx]
                            x = int(landmark.x * frame_w)
                            y = int(landmark.y * frame_h)
                            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                    
                    # استخدام نقطة مركز العين للتحكم (النقطة 468 هي مركز العين)
                    if len(landmarks) > 468:  # نقطة مركز العين
                        center_landmark = landmarks[468]
                        screen_x = self.screen_w * center_landmark.x
                        screen_y = self.screen_h * center_landmark.y
                        
                        # تنعيم الحركة - نفس سرعة hand_mouse
                        smooth_x, smooth_y = self._smooth_position(screen_x, screen_y)
                        pyautogui.moveTo(smooth_x, smooth_y)
                        
                        # رسم نقطة مركز العين
                        center_x = int(center_landmark.x * frame_w)
                        center_y = int(center_landmark.y * frame_h)
                        cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)
                    
                    # كشف إغلاق العين للنقر - استخدام نقاط الجفن
                    if len(landmarks) > 159:
                        upper_lid = landmarks[159]
                        lower_lid = landmarks[145]
                        
                        # رسم نقاط الجفن
                        upper_x = int(upper_lid.x * frame_w)
                        upper_y = int(upper_lid.y * frame_h)
                        lower_x = int(lower_lid.x * frame_w)
                        lower_y = int(lower_lid.y * frame_h)
                        
                        cv2.circle(frame, (upper_x, upper_y), 3, (0, 255, 255), -1)
                        cv2.circle(frame, (lower_x, lower_y), 3, (0, 255, 255), -1)
                        
                        # كشف إغلاق العين - تحسين الحساسية
                        if (upper_lid.y - lower_lid.y) < 0.002:  # حساسية أعلى
                            pyautogui.click()
                            time.sleep(0.3)  # تقليل وقت الانتظار
                
                # تحسين الأداء - نفس سرعة hand_mouse
                time.sleep(0.01)  # سرعة محسنة
                    
            except Exception as e:
                print(f"خطأ في تشغيل الأداة: {e}")
                break
        
        # تنظيف الموارد
        if self.face_mesh:
            self.face_mesh.close()

# إنشاء instance عام للاستخدام
eye_mouse_controller = EyeMouseController()

def start_eye_mouse():
    """دالة لبدء التحكم بالماوس بالعين"""
    return eye_mouse_controller.start_eye_mouse()

def stop_eye_mouse():
    """دالة لإيقاف التحكم بالماوس بالعين"""
    return eye_mouse_controller.stop_eye_mouse()

def get_performance_stats():
    """دالة للحصول على إحصائيات الأداء"""
    return eye_mouse_controller.get_performance_stats()

def get_current_frame():
    """دالة للحصول على الإطار الحالي من الكاميرا"""
    return eye_mouse_controller.get_current_frame()

def adjust_sensitivity(smoothing_factor=None, click_threshold=None):
    """دالة لتعديل حساسية الأداة"""
    return eye_mouse_controller.adjust_sensitivity(smoothing_factor, click_threshold)

def reset_state():
    """دالة لإعادة تعيين حالة الأداة"""
    return eye_mouse_controller.reset_state()


