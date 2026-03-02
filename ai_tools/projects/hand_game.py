import cv2
import mediapipe as mp
import random
import time
import math
import threading

class HandGame:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = None
        self.is_running = False
        self.thread = None
        self.balls = []
        self.score = 0
        self.start_time = time.time()
        self.screen_width = 640
        self.screen_height = 480
        
    def start_hand_game(self):
        """بدء لعبة التحكم باليدين"""
        if self.is_running:
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            
        try:
            self.hands = self.mp_hands.Hands(
                max_num_hands=1, 
                min_detection_confidence=0.7, 
                min_tracking_confidence=0.7
            )
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.screen_width)
            self.cap.set(4, self.screen_height)
            self.is_running = True
            self.balls = []
            self.score = 0
            self.start_time = time.time()
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_hand_game)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء لعبة التحكم باليدين'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_hand_game(self):
        """إيقاف لعبة التحكم باليدين"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        cv2.destroyAllWindows()
        return {'status': 'success', 'message': 'تم إيقاف لعبة التحكم باليدين'}
    
    def get_game_score(self):
        """الحصول على نقاط اللعبة"""
        return {'status': 'success', 'score': self.score}
    
    def reset_game(self):
        """إعادة تعيين اللعبة"""
        self.score = 0
        self.balls = []
        self.start_time = time.time()
        return {'status': 'success', 'message': 'تم إعادة تعيين اللعبة'}
    
    def _create_ball(self):
        """إنشاء كرة جديدة"""
        return {
            'x': random.randint(0, self.screen_width),
            'y': 0,
            'radius': 20,
            'speed': random.randint(1, 5)
        }
    
    def _draw_ball(self, image, ball):
        """رسم الكرة"""
        cv2.circle(image, (ball['x'], ball['y']), ball['radius'], (0, 0, 255), -1)
    
    def _move_ball(self, ball):
        """تحريك الكرة"""
        ball['y'] += ball['speed']
    
    def _is_collision(self, ball, x, y):
        """فحص الاصطدام"""
        distance = math.hypot(ball['x'] - x, ball['y'] - y)
        return distance < ball['radius']
    
    def _run_hand_game(self):
        """تشغيل منطق لعبة التحكم باليدين"""
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                success, image = self.cap.read()
                if not success:
                    break

                # قلب الصورة للحصول على مرآة
                image = cv2.flip(image, 1)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # معالجة الصورة للحصول على معالم اليد
                results = self.hands.process(image_rgb)

                # الحصول على حجم الصورة
                height, width, _ = image.shape

                # إضافة كرة جديدة كل 2 ثانية
                if time.time() - self.start_time > 2:
                    self.balls.append(self._create_ball())
                    self.start_time = time.time()

                # تحريك ورسم الكرات
                for ball in self.balls:
                    self._move_ball(ball)
                    self._draw_ball(image, ball)

                # إزالة الكرات التي تصل إلى أسفل الشاشة
                self.balls = [ball for ball in self.balls if ball['y'] < self.screen_height]

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                        # الحصول على معالم الإصبع السبابة
                        index_finger_tip = hand_landmarks.landmark[8]

                        # تحويل إحداثيات الكاميرا إلى إحداثيات الشاشة
                        finger_x = int(index_finger_tip.x * width)
                        finger_y = int(index_finger_tip.y * height)

                        # التحقق من الاصطدام بالكرات
                        for ball in self.balls[:]:  # استخدام نسخة من القائمة لتجنب مشاكل التعديل
                            if self._is_collision(ball, finger_x, finger_y):
                                self.score += 1
                                self.balls.remove(ball)

                # عرض السكور على الشاشة
                cv2.putText(image, f'Score: {self.score}', (10, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # لا نعرض نافذة خارجية - كل شيء داخل الموقع
                # استخدام cv2.waitKey() مع timeout قصير لتجنب تجميد الكاميرا
                if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
                    break
                time.sleep(0.01)  # تأخير قصير لتجنب الاستهلاك المفرط للمعالج
                    
            except Exception as e:
                print(f"خطأ في تشغيل الأداة: {e}")
                break
        
        # تنظيف الموارد
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        cv2.destroyAllWindows()

# إنشاء instance عام للاستخدام
hand_game = HandGame()

def start_hand_game():
    """دالة لبدء لعبة التحكم باليدين"""
    return hand_game.start_hand_game()

def stop_hand_game():
    """دالة لإيقاف لعبة التحكم باليدين"""
    return hand_game.stop_hand_game()

def get_game_score():
    """دالة للحصول على نقاط اللعبة"""
    return hand_game.get_game_score()

def reset_game():
    """دالة لإعادة تعيين اللعبة"""
    return hand_game.reset_game()


