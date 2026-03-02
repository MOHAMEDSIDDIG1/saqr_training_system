import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import threading
import time
from collections import deque

class VoiceController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = None
        self.is_running = False
        self.thread = None
        self.volume = None
        self.min_vol = 0
        self.max_vol = 0
        
        # تحسينات الأداء
        self.smoothing_factor = 0.3
        self.position_history = deque(maxlen=5)
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # إحصائيات الأداء
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # إعدادات ثبات الصوت
        self.volume_change_threshold = 0.1  # عتبة تغيير الصوت
        self.last_volume = 0.5  # آخر مستوى صوت
        self.volume_stability_frames = 0  # عدد الإطارات المستقرة
        self.stability_required = 5  # عدد الإطارات المطلوبة للثبات
        
        # إعدادات دقة الحركة
        self.min_distance = 20  # المسافة الدنيا (إصبعان مضمومان)
        self.max_distance = 200  # المسافة العليا (إصبعان مفتوحان بالكامل)
        self.volume_start_threshold = 30  # عتبة بدء التحكم في الصوت
        self.current_volume_percentage = 0  # النسبة المئوية الحالية للصوت
        
    def start_voice_control(self):
        """بدء التحكم في الصوت باليدين"""
        # إعادة تعيين الحالة إذا كانت الأداة متوقفة
        if self.is_running and (not self.thread or not self.thread.is_alive()):
            self.is_running = False
            self.thread = None
        
        if self.is_running and self.thread and self.thread.is_alive():
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            
        try:
            # تحسين إعدادات MediaPipe (بدون كاميرا منفصلة)
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6,
                model_complexity=0
            )
            
            # إعداد التحكم في الصوت
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # الحصول على نطاق مستوى الصوت
                vol_range = self.volume.GetVolumeRange()
                self.min_vol = vol_range[0]
                self.max_vol = vol_range[1]
                
                # اختبار التحكم في الصوت
                current_vol = self.volume.GetMasterVolumeLevel()
                print(f"تم تهيئة التحكم في الصوت. المستوى الحالي: {current_vol}")
                print(f"نطاق الصوت: {self.min_vol} إلى {self.max_vol}")
                
            except Exception as audio_error:
                return {'status': 'error', 'message': f'خطأ في إعداد الصوت: {str(audio_error)}'}
            
            self.is_running = True
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_voice_control)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء التحكم في الصوت باليدين'}
        except Exception as e:
            self.is_running = False
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_voice_control(self):
        """إيقاف التحكم في الصوت"""
        self.is_running = False
        
        # انتظار إيقاف الـ thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        # تنظيف الموارد
        if self.hands:
            try:
                self.hands.close()
            except:
                pass
            self.hands = None
        
        # إعادة تعيين الحالة
        self.thread = None
        with self.frame_lock:
            self.current_frame = None
        
        return {'status': 'success', 'message': 'تم إيقاف التحكم في الصوت'}
    
    def reset_state(self):
        """إعادة تعيين حالة الأداة بالكامل"""
        self.stop_voice_control()
        
        # إعادة تعيين جميع المتغيرات
        self.is_running = False
        self.thread = None
        self.hands = None
        self.volume = None
        
        # تنظيف الإطار
        with self.frame_lock:
            self.current_frame = None
        
        # إعادة تعيين الإحصائيات
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.position_history.clear()
        
        # إعادة تعيين إعدادات الصوت
        self.current_volume_percentage = 0
        self.volume_stability_frames = 0
        self.last_volume = 0.5
        
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
        """تنعيم حركة اليد"""
        self.position_history.append((new_x, new_y))
        if len(self.position_history) < 2:
            return new_x, new_y
        
        # حساب المتوسط المتحرك
        avg_x = sum(pos[0] for pos in self.position_history) / len(self.position_history)
        avg_y = sum(pos[1] for pos in self.position_history) / len(self.position_history)
        
        return avg_x, avg_y
    
    def _calculate_volume_percentage(self, distance):
        """حساب النسبة المئوية للصوت بناءً على المسافة"""
        # إذا كانت المسافة أقل من العتبة، لا يبدأ التحكم
        if distance < self.volume_start_threshold:
            return 0
        
        # حساب النسبة المئوية (0-100%)
        percentage = np.interp(distance, [self.min_distance, self.max_distance], [0, 100])
        percentage = max(0, min(100, percentage))  # التأكد من أن النسبة بين 0-100
        
        return percentage
    
    def _should_change_volume(self, new_volume):
        """تحديد ما إذا كان يجب تغيير الصوت"""
        # حساب الفرق بين الصوت الحالي والجديد
        volume_diff = abs(new_volume - self.last_volume)
        
        # إذا كان الفرق كبيراً، إعادة تعيين عداد الاستقرار
        if volume_diff > self.volume_change_threshold:
            self.volume_stability_frames = 0
            return False
        
        # زيادة عداد الاستقرار
        self.volume_stability_frames += 1
        
        # إذا وصلنا للعدد المطلوب من الإطارات المستقرة، تغيير الصوت
        if self.volume_stability_frames >= self.stability_required:
            self.last_volume = new_volume
            self.volume_stability_frames = 0
            return True
        
        return False
    
    def get_performance_stats(self):
        """الحصول على إحصائيات الأداء"""
        # التحقق من الحالة الفعلية
        actual_running = self.is_running and self.thread and self.thread.is_alive()
        
        return {
            'fps': self.current_fps,
            'is_running': actual_running,
            'smoothing_factor': self.smoothing_factor,
            'volume_threshold': self.volume_change_threshold,
            'stability_frames': self.volume_stability_frames,
            'stability_required': self.stability_required,
            'volume_percentage': self.current_volume_percentage,
            'min_distance': self.min_distance,
            'max_distance': self.max_distance
        }
    
    def adjust_volume_stability(self, threshold=None, stability_frames=None):
        """تعديل إعدادات ثبات الصوت"""
        if threshold is not None:
            self.volume_change_threshold = max(0.01, min(0.5, threshold))
        if stability_frames is not None:
            self.stability_required = max(1, min(20, stability_frames))
        
        return {
            'status': 'success',
            'message': f'تم تعديل إعدادات الثبات: عتبة={self.volume_change_threshold:.2f}, إطارات={self.stability_required}'
        }
    
    def adjust_volume_precision(self, min_distance=None, max_distance=None, start_threshold=None):
        """تعديل إعدادات دقة الحركة"""
        if min_distance is not None:
            self.min_distance = max(10, min(100, min_distance))
        if max_distance is not None:
            self.max_distance = max(100, min(500, max_distance))
        if start_threshold is not None:
            self.volume_start_threshold = max(10, min(100, start_threshold))
        
        return {
            'status': 'success',
            'message': f'تم تعديل إعدادات الدقة: أدنى={self.min_distance}, أعلى={self.max_distance}, عتبة={self.volume_start_threshold}'
        }
    
    def check_and_reset_state(self):
        """التحقق من الحالة وإعادة التعيين التلقائي إذا لزم الأمر"""
        # التحقق من الحالة الفعلية
        if self.is_running and (not self.thread or not self.thread.is_alive()):
            # إعادة تعيين الحالة
            self.is_running = False
            self.thread = None
            return {'status': 'success', 'message': 'تم إعادة تعيين الحالة تلقائياً'}
        
        return {'status': 'success', 'message': 'الحالة طبيعية'}
    
    def test_volume_control(self):
        """اختبار التحكم في الصوت"""
        try:
            if self.volume is None:
                return {'status': 'error', 'message': 'لم يتم تهيئة التحكم في الصوت'}
            
            # اختبار تغيير الصوت
            current_vol = self.volume.GetMasterVolumeLevel()
            test_vol = max(self.min_vol, min(self.max_vol, current_vol + 0.1))
            self.volume.SetMasterVolumeLevel(test_vol, None)
            
            # التحقق من التغيير
            new_vol = self.volume.GetMasterVolumeLevel()
            
            return {
                'status': 'success', 
                'message': f'تم اختبار التحكم في الصوت. من {current_vol:.3f} إلى {new_vol:.3f}',
                'current_volume': current_vol,
                'test_volume': test_vol,
                'new_volume': new_vol,
                'volume_changed': abs(new_vol - current_vol) > 0.01
            }
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في اختبار التحكم في الصوت: {str(e)}'}
    
    def force_volume_change(self, percentage):
        """تغيير الصوت بشكل مباشر"""
        try:
            if self.volume is None:
                return {'status': 'error', 'message': 'لم يتم تهيئة التحكم في الصوت'}
            
            # تحويل النسبة المئوية إلى مستوى صوت النظام
            vol_system = np.interp(percentage, [0, 100], [self.min_vol, self.max_vol])
            
            # الحصول على المستوى الحالي
            old_vol = self.volume.GetMasterVolumeLevel()
            
            # تغيير الصوت
            self.volume.SetMasterVolumeLevel(vol_system, None)
            
            # التحقق من التغيير
            new_vol = self.volume.GetMasterVolumeLevel()
            
            return {
                'status': 'success',
                'message': f'تم تغيير الصوت إلى {percentage}% (من {old_vol:.3f} إلى {new_vol:.3f})',
                'old_volume': old_vol,
                'new_volume': new_vol,
                'volume_changed': abs(new_vol - old_vol) > 0.01
            }
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في تغيير الصوت: {str(e)}'}
    
    def get_current_frame(self):
        """الحصول على الإطار الحالي من الكاميرا"""
        with self.frame_lock:
            if self.current_frame is not None:
                import base64
                _, buffer = cv2.imencode('.jpg', self.current_frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return frame_base64
        return None
    
    def _run_voice_control(self):
        """تشغيل منطق التحكم في الصوت"""
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
                
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)
                
                # حساب FPS
                self._calculate_fps()

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # رسم نقاط اليد
                        self.mp_drawing.draw_landmarks(
                            img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                        
                        # الحصول على نقاط الإبهام والسبابة
                        thumb_tip = hand_landmarks.landmark[4]
                        index_tip = hand_landmarks.landmark[8]
                        
                        # حساب المسافة بين الإبهام والسبابة
                        x1, y1 = int(thumb_tip.x * img.shape[1]), int(thumb_tip.y * img.shape[0])
                        x2, y2 = int(index_tip.x * img.shape[1]), int(index_tip.y * img.shape[0])
                        
                        length = np.hypot(x2 - x1, y2 - y1)
                        
                        # حساب النسبة المئوية للصوت بناءً على المسافة
                        volume_percentage = self._calculate_volume_percentage(length)
                        self.current_volume_percentage = volume_percentage
                        
                        # تحويل النسبة المئوية إلى مستوى صوت (0-1)
                        vol_normalized = volume_percentage / 100.0
                        
                        # استخدام آلية الثبات لتغيير الصوت
                        if self._should_change_volume(vol_normalized) and self.volume is not None:
                            try:
                                # تحويل إلى مستوى صوت النظام
                                vol_system = np.interp(vol_normalized, [0, 1], [self.min_vol, self.max_vol])
                                
                                # الحصول على المستوى الحالي قبل التغيير
                                old_vol = self.volume.GetMasterVolumeLevel()
                                
                                # تغيير الصوت
                                self.volume.SetMasterVolumeLevel(vol_system, None)
                                
                                # التحقق من التغيير
                                new_vol = self.volume.GetMasterVolumeLevel()
                                
                                print(f"تغيير الصوت: {volume_percentage:.1f}% | من {old_vol:.3f} إلى {new_vol:.3f}")
                                
                                # إذا لم يتغير الصوت، جرب طريقة أخرى
                                if abs(new_vol - old_vol) < 0.01:
                                    print("تحذير: الصوت لم يتغير، جرب طريقة أخرى...")
                                    # جرب تغيير صغير
                                    test_vol = old_vol + 0.1 if old_vol < -0.1 else old_vol - 0.1
                                    self.volume.SetMasterVolumeLevel(test_vol, None)
                                    print(f"جرب تغيير صغير إلى: {test_vol:.3f}")
                                    
                            except Exception as vol_error:
                                print(f"خطأ في تغيير الصوت: {vol_error}")
                        elif self.volume is None:
                            print("تحذير: لم يتم تهيئة التحكم في الصوت")
                        
                        # رسم خط ودائرتين
                        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
                        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

                # تحسين الأداء
                time.sleep(0.005)  # سرعة أعلى
                    
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
voice_controller = VoiceController()

def start_voice_control():
    """دالة لبدء التحكم في الصوت باليدين"""
    return voice_controller.start_voice_control()

def stop_voice_control():
    """دالة لإيقاف التحكم في الصوت"""
    return voice_controller.stop_voice_control()

def get_performance_stats():
    """دالة للحصول على إحصائيات الأداء"""
    return voice_controller.get_performance_stats()

def get_current_frame():
    """دالة للحصول على الإطار الحالي من الكاميرا"""
    return voice_controller.get_current_frame()

def reset_state():
    """دالة لإعادة تعيين حالة الأداة"""
    return voice_controller.reset_state()

def adjust_volume_stability(threshold=None, stability_frames=None):
    """دالة لتعديل إعدادات ثبات الصوت"""
    return voice_controller.adjust_volume_stability(threshold, stability_frames)

def adjust_volume_precision(min_distance=None, max_distance=None, start_threshold=None):
    """دالة لتعديل إعدادات دقة الحركة"""
    return voice_controller.adjust_volume_precision(min_distance, max_distance, start_threshold)

def check_and_reset_state():
    """دالة للتحقق من الحالة وإعادة التعيين التلقائي إذا لزم الأمر"""
    return voice_controller.check_and_reset_state()

def test_volume_control():
    """دالة لاختبار التحكم في الصوت"""
    return voice_controller.test_volume_control()

def force_volume_change(percentage):
    """دالة لتغيير الصوت بشكل مباشر"""
    return voice_controller.force_volume_change(percentage)


